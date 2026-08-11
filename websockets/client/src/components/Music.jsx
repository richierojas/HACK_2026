export function Music() {
  return (
    <section className="music-section">

      <div className="music-header">
        <p className="section-tag">NEWEST ALBUM</p>

        <h2>Cosmic SpellSynth Setlist</h2>

        <p>
          Artemis Audio's Battle of the Builds setlist,
          performed live on the Cosmic SpellSynth.
        </p>
      </div>

      {/* Live performance recording */}
      <div className="performance-section">

        <p className="section-tag">LIVE RECORDING</p>

        <h3>Artemis Audio — Live Performance</h3>

        <video
          controls
          className="performance-video"
        >
          <source
            src="/music/artemis-performance.mp4"
            type="video/mp4"
          />

          Your browser does not support video playback.
        </video>

      </div>

      {/* Setlist */}
      <div className="setlist">

        <div className="song-card">
          <span className="song-number">01</span>

          <div>
            <h3>
              Sweet Dreams (Are Made of This) — Eurythmics
            </h3>
          </div>
        </div>

        <div className="song-card">
          <span className="song-number">02</span>

          <div>
            <h3>
              A Thousand Miles — Vanessa Carlton
            </h3>
          </div>
        </div>

        <div className="song-card">
          <span className="song-number">03</span>

          <div>
            <h3>
              Experience — Ludovico Einaudi
            </h3>
          </div>
        </div>

      </div>

    </section>
  )
}