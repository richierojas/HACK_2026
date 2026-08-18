import { useEffect, useRef, useState, useCallback } from 'react'
import { SONGS, WINDOWS, APPROACH_SECONDS, LEAD_IN_SECONDS } from '../songs.js'
import './RhythmGame.css'

const LANES = 8

// Perspective. Notes travel from Z_FAR to Z_NEAR; screen position comes from
// 1/z, which is what makes them accelerate toward you like real depth rather
// than sliding at a constant speed.
// Z_FAR controls how much depth there is. Too high and the note spends most of
// its flight as a dot near the horizon and then rushes the last stretch, which
// is impossible to time against. 2.5 keeps the 3D feel while the note travels
// at a readable pace.
const Z_FAR = 2.5
const Z_NEAR = 1

function depth(progress) {
  // progress 0 = just spawned at the horizon, 1 = on the hit line
  const z = Z_FAR + (Z_NEAR - Z_FAR) * progress
  const scale = 1 / z
  const min = 1 / Z_FAR
  const max = 1 / Z_NEAR
  return (scale - min) / (max - min)
}

const LANE_HUES = [190, 210, 265, 295, 320, 30, 45, 140]

// Stretches or squeezes every note time. Below 1 the song plays slower with the
// gaps between notes opening up, which is the difference between a chart being
// learnable and being a blur.
const SPEEDS = [
  { label: 'RELAXED', value: 0.7 },
  { label: 'STEADY', value: 0.85 },
  { label: 'NORMAL', value: 1 },
  { label: 'FAST', value: 1.25 },
]

export function RhythmGame({ lastHit, currentInstrument }) {
  const canvasRef = useRef(null)
  const stateRef = useRef(null)

  const [songIndex, setSongIndex] = useState(0)
  const [speedIndex, setSpeedIndex] = useState(1)
  const [playing, setPlaying] = useState(false)
  const [hud, setHud] = useState({ score: 0, combo: 0, best: 0, hits: 0, misses: 0, judgement: '' })
  const [finished, setFinished] = useState(null)

  const song = SONGS[songIndex]
  const speed = SPEEDS[speedIndex].value

  // The chart with every time scaled. Slower speed = larger gaps.
  const chart = {
    ...song,
    notes: song.notes.map((n) => ({ ...n, time: n.time / speed })),
    duration: song.duration / speed,
  }

  // ---- start / stop -------------------------------------------------------

  const start = useCallback(() => {
    const now = performance.now() / 1000
    stateRef.current = {
      startedAt: now + LEAD_IN_SECONDS,
      notes: chart.notes.map((n) => ({ ...n, state: 'pending' })),
      bursts: [],
      score: 0,
      combo: 0,
      best: 0,
      hits: 0,
      misses: 0,
      judgement: '',
      judgementAt: 0,
    }
    setFinished(null)
    setHud({ score: 0, combo: 0, best: 0, hits: 0, misses: 0, judgement: '' })
    setPlaying(true)
  }, [chart])

  const stop = useCallback(() => {
    setPlaying(false)
    stateRef.current = null
  }, [])

  // ---- judge a button press ----------------------------------------------

  useEffect(() => {
    const game = stateRef.current
    if (!playing || !game || !lastHit) return

    const songTime = performance.now() / 1000 - game.startedAt

    // The EARLIEST pending note in this lane that is inside the window - not
    // the nearest. Players always aim at the next note, so when two notes in a
    // lane fall close together a late press should clear the one you were
    // aiming at, rather than stealing the following note's slot and leaving
    // the first to expire as a miss.
    let target = null
    let bestDelta = Infinity
    for (const note of game.notes) {
      if (note.state !== 'pending' || note.button !== lastHit.button) continue
      const ahead = note.time - songTime          // positive = note not due yet
      if (ahead > WINDOWS.early) continue         // too early to count
      if (-ahead > WINDOWS.late) continue         // already gone
      if (target === null || note.time < target.time) {
        target = note
        bestDelta = Math.abs(ahead)
      }
    }

    if (!target) {
      // A press with no note near it breaks the combo but costs no score,
      // so mashing is discouraged without being punishing.
      game.combo = 0
      game.judgement = 'MISS'
      game.judgementAt = performance.now() / 1000
    } else {
      const perfect = bestDelta <= WINDOWS.perfect
      target.state = 'hit'
      game.combo += 1
      game.best = Math.max(game.best, game.combo)
      game.hits += 1
      game.score += (perfect ? 100 : 50) * (1 + Math.min(game.combo, 20) / 20)
      game.judgement = perfect ? 'PERFECT' : 'GOOD'
      game.judgementAt = performance.now() / 1000
      game.bursts.push({ lane: target.button - 1, born: performance.now() / 1000, perfect })
    }

    setHud({
      score: Math.round(game.score),
      combo: game.combo,
      best: game.best,
      hits: game.hits,
      misses: game.misses,
      judgement: game.judgement,
    })
  }, [lastHit, playing])

  // ---- render loop --------------------------------------------------------

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    let frame

    // Starfield lives outside the game state so it keeps drifting on the menu
    const stars = Array.from({ length: 220 }, () => ({
      x: Math.random() * 2 - 1,
      y: Math.random() * 2 - 1,
      z: Math.random() * Z_FAR + 0.4,
    }))

    const draw = () => {
      frame = requestAnimationFrame(draw)

      const rect = canvas.getBoundingClientRect()
      const dpr = window.devicePixelRatio || 1
      if (canvas.width !== rect.width * dpr || canvas.height !== rect.height * dpr) {
        canvas.width = rect.width * dpr
        canvas.height = rect.height * dpr
      }
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

      const w = rect.width
      const h = rect.height
      const cx = w / 2
      const horizon = h * 0.30
      const hitY = h * 0.82
      const now = performance.now() / 1000

      ctx.clearRect(0, 0, w, h)

      // ---- space background ----
      const sky = ctx.createLinearGradient(0, 0, 0, h)
      sky.addColorStop(0, '#05000f')
      sky.addColorStop(0.45, '#0a0320')
      sky.addColorStop(1, '#12002a')
      ctx.fillStyle = sky
      ctx.fillRect(0, 0, w, h)

      // ---- stars flying past ----
      for (const s of stars) {
        s.z -= 0.02
        if (s.z < 0.4) {
          s.z = Z_FAR
          s.x = Math.random() * 2 - 1
          s.y = Math.random() * 2 - 1
        }
        const k = 1 / s.z
        const sx = cx + s.x * k * w * 0.9
        const sy = horizon + s.y * k * h * 0.9
        if (sx < 0 || sx > w || sy < 0 || sy > h) continue
        const size = k * 2.2
        ctx.globalAlpha = Math.min(1, k * 1.6)
        ctx.fillStyle = '#cfe9ff'
        ctx.fillRect(sx, sy, size, size)
      }
      ctx.globalAlpha = 1

      // ---- lane geometry ----
      const laneX = (lane) => {
        const spread = w * 0.46
        return cx + ((lane + 0.5) / LANES - 0.5) * 2 * spread
      }

      // lane rails converging on the vanishing point
      for (let lane = 0; lane <= LANES; lane++) {
        const spread = w * 0.46
        const x = cx + (lane / LANES - 0.5) * 2 * spread
        const g = ctx.createLinearGradient(0, horizon, 0, hitY)
        g.addColorStop(0, 'rgba(120,200,255,0)')
        g.addColorStop(1, 'rgba(120,200,255,0.25)')
        ctx.strokeStyle = g
        ctx.lineWidth = 1
        ctx.beginPath()
        ctx.moveTo(cx, horizon)
        ctx.lineTo(x, hitY)
        ctx.stroke()
      }

      // ---- hit line ----
      ctx.strokeStyle = 'rgba(0,255,255,0.55)'
      ctx.lineWidth = 2
      ctx.shadowBlur = 18
      ctx.shadowColor = '#00ffff'
      ctx.beginPath()
      ctx.moveTo(cx - w * 0.46, hitY)
      ctx.lineTo(cx + w * 0.46, hitY)
      ctx.stroke()
      ctx.shadowBlur = 0

      // lane pads on the hit line
      for (let lane = 0; lane < LANES; lane++) {
        const x = laneX(lane)
        ctx.fillStyle = `hsla(${LANE_HUES[lane]}, 90%, 60%, 0.18)`
        ctx.beginPath()
        ctx.ellipse(x, hitY, w * 0.028, 7, 0, 0, Math.PI * 2)
        ctx.fill()
        ctx.fillStyle = `hsla(${LANE_HUES[lane]}, 90%, 75%, 0.75)`
        ctx.font = '600 11px system-ui, sans-serif'
        ctx.textAlign = 'center'
        ctx.fillText(String(lane + 1), x, hitY + 24)
      }

      const game = stateRef.current

      // ---- notes ----
      if (game) {
        const songTime = now - game.startedAt

        for (const note of game.notes) {
          if (note.state === 'hit') continue

          const untilHit = note.time - songTime
          if (untilHit > APPROACH_SECONDS) continue

          // Past the window and never pressed -> miss
          if (untilHit < -WINDOWS.late) {
            if (note.state === 'pending') {
              note.state = 'missed'
              game.combo = 0
              game.misses += 1
              game.judgement = 'MISS'
              game.judgementAt = now
              setHud({
                score: Math.round(game.score), combo: 0, best: game.best,
                hits: game.hits, misses: game.misses, judgement: 'MISS',
              })
            }
            if (untilHit < -0.6) continue
          }

          const progress = 1 - untilHit / APPROACH_SECONDS
          const f = depth(Math.max(0, Math.min(1.15, progress)))
          const x = cx + (laneX(note.button - 1) - cx) * f
          const y = horizon + (hitY - horizon) * f
          const r = 3 + 20 * f
          const hue = LANE_HUES[note.button - 1]
          const dim = note.state === 'missed' ? 0.18 : 1

          ctx.globalAlpha = dim
          ctx.shadowBlur = 22 * f
          ctx.shadowColor = `hsl(${hue}, 95%, 60%)`
          const grad = ctx.createRadialGradient(x, y, 0, x, y, r)
          grad.addColorStop(0, '#ffffff')
          grad.addColorStop(0.35, `hsl(${hue}, 95%, 68%)`)
          grad.addColorStop(1, `hsla(${hue}, 95%, 45%, 0.15)`)
          ctx.fillStyle = grad
          ctx.beginPath()
          ctx.arc(x, y, r, 0, Math.PI * 2)
          ctx.fill()
          ctx.shadowBlur = 0

          // number on the note once it is big enough to read
          if (f > 0.35 && note.state === 'pending') {
            ctx.fillStyle = 'rgba(10,0,25,0.85)'
            ctx.font = `700 ${Math.round(9 + 12 * f)}px system-ui, sans-serif`
            ctx.textAlign = 'center'
            ctx.textBaseline = 'middle'
            ctx.fillText(String(note.button), x, y)
            ctx.textBaseline = 'alphabetic'
          }
          ctx.globalAlpha = 1
        }

        // ---- hit bursts ----
        game.bursts = game.bursts.filter((b) => now - b.born < 0.45)
        for (const b of game.bursts) {
          const age = (now - b.born) / 0.45
          const x = laneX(b.lane)
          ctx.globalAlpha = 1 - age
          ctx.strokeStyle = b.perfect ? '#ffffff' : `hsl(${LANE_HUES[b.lane]}, 90%, 70%)`
          ctx.lineWidth = 3 * (1 - age)
          ctx.beginPath()
          ctx.arc(x, hitY, 12 + age * 70, 0, Math.PI * 2)
          ctx.stroke()
          ctx.globalAlpha = 1
        }

        // ---- countdown / finish ----
        if (songTime < 0) {
          ctx.fillStyle = '#9fe8ff'
          ctx.font = '700 64px system-ui, sans-serif'
          ctx.textAlign = 'center'
          ctx.fillText(String(Math.ceil(-songTime)), cx, h * 0.5)
        } else if (songTime > chart.duration + APPROACH_SECONDS) {
          const total = game.hits + game.misses
          setFinished({
            score: Math.round(game.score),
            hits: game.hits,
            misses: game.misses,
            best: game.best,
            accuracy: total ? Math.round((game.hits / total) * 100) : 0,
          })
          setPlaying(false)
          stateRef.current = null
        }

        // ---- judgement flash ----
        if (game.judgement && now - game.judgementAt < 0.5) {
          const age = (now - game.judgementAt) / 0.5
          ctx.globalAlpha = 1 - age
          ctx.fillStyle =
            game.judgement === 'PERFECT' ? '#ffffff'
            : game.judgement === 'GOOD' ? '#7dffb0'
            : '#ff5c7a'
          ctx.font = '800 30px system-ui, sans-serif'
          ctx.textAlign = 'center'
          ctx.fillText(game.judgement, cx, hitY - 60 - age * 20)
          ctx.globalAlpha = 1
        }
      }
    }

    frame = requestAnimationFrame(draw)
    return () => cancelAnimationFrame(frame)
  }, [chart.duration])

  // ---- ui -----------------------------------------------------------------

  return (
    <section id="play">
      <div className="play-shell">

        <canvas ref={canvasRef} className="play-canvas" />

        <div className="play-hud">
          <div className="hud-block">
            <span className="hud-label">SCORE</span>
            <span className="hud-value">{hud.score}</span>
          </div>
          <div className="hud-block">
            <span className="hud-label">COMBO</span>
            <span className="hud-value">{hud.combo}<small>x</small></span>
          </div>
          <div className="hud-block">
            <span className="hud-label">INSTRUMENT</span>
            <span className="hud-value small">{currentInstrument || '--'}</span>
          </div>
        </div>

        {!playing && !finished && (
          <div className="play-overlay">
            <h2>STAR RUNNER</h2>
            <p>
              Notes fly at you from deep space. Hit the matching button on the
              instrument as each one crosses the line.
            </p>
            <div className="speed-picker">
              {SPEEDS.map((s, i) => (
                <button
                  key={s.label}
                  className={`speed-choice ${i === speedIndex ? 'selected' : ''}`}
                  onClick={() => setSpeedIndex(i)}
                >
                  {s.label}
                </button>
              ))}
            </div>

            <div className="song-picker">
              {SONGS.map((s, i) => (
                <button
                  key={s.name}
                  className={`song-choice ${i === songIndex ? 'selected' : ''}`}
                  onClick={() => setSongIndex(i)}
                >
                  <span className="song-name">{s.name}</span>
                  <span className="song-meta">
                    {s.notes.length} notes · {(s.notes.length / (s.duration / speed)).toFixed(1)}/sec · {s.hint}
                  </span>
                </button>
              ))}
            </div>
            <button className="play-start" onClick={start}>LAUNCH</button>
          </div>
        )}

        {finished && (
          <div className="play-overlay">
            <h2>RUN COMPLETE</h2>
            <div className="result-grid">
              <div><span>SCORE</span><strong>{finished.score}</strong></div>
              <div><span>ACCURACY</span><strong>{finished.accuracy}%</strong></div>
              <div><span>BEST COMBO</span><strong>{finished.best}</strong></div>
              <div><span>HIT / MISS</span><strong>{finished.hits} / {finished.misses}</strong></div>
            </div>
            <button className="play-start" onClick={start}>RUN IT AGAIN</button>
            <button className="play-secondary" onClick={() => setFinished(null)}>PICK ANOTHER SONG</button>
          </div>
        )}

        {playing && (
          <button className="play-secondary floating" onClick={stop}>STOP</button>
        )}

      </div>
    </section>
  )
}
