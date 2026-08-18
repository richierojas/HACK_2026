import { useState, useEffect, useRef } from 'react'
import { Routes, Route } from 'react-router'

import { Navbar } from './components/Navbar.jsx'
import { Hero } from './components/Hero.jsx'
import { Instrument } from './components/Instrument.jsx'
import { SoundProfiles } from './components/SoundProfiles.jsx'
import { Band } from './components/Band.jsx'
import { Music } from './components/Music.jsx'
import { RhythmGame } from './components/RhythmGame.jsx'

import './App.css'

function App() {
  const [count, setCount] = useState(0)
  const [message, setMessage] = useState('')
  const [chatLogs, setChatLogs] = useState([])
  const [masterSwitchState, setMasterSwitchState] = useState(false)
  const [buttonState, setButtonState] = useState(true)
  const [lastButton, setLastButton] = useState(null)
  const [volume, setVolume] = useState(50)
  const [currentInstrument, setCurrentInstrument] = useState(null)

  // Every button press, with a sequence number. The game needs to react to
  // each press individually - without the counter, pressing the same button
  // twice in a row would look like unchanged state and be ignored.
  const [lastHit, setLastHit] = useState(null)
  const hitSeq = useRef(0)

  const wsRef = useRef(null)

  const buttonHandler = () => {
    //Fill this out
    setMasterSwitchState(0)
  }

  // Initialize WebSocket connection
  useEffect(() => {
    const wsHost = window.location.hostname || 'localhost'

    // Connect to WebSocket server
    wsRef.current = new WebSocket(`ws://${wsHost}:8765`)

    wsRef.current.onopen = () => {
      console.log('Connected to WebSocket server')
    }

    wsRef.current.onmessage = (event) => {
      console.log('Message from server:', event.data)
      try {
        const data = JSON.parse(event.data)
        if (data.type === "message") {
          setChatLogs(prev => [...prev, {
            message: data.value,
            timestamp: data.timestamp,
            type: 'received'
          }])
        } else if (data.type === "switch") {
          setMasterSwitchState(data.value)
        } else if (data.type === "button") {
          console.log('Button pressed:', data.value)
          setLastButton(data.value)
        } else if (data.type === "button-pressed") {
          const buttonNumber = data.value?.button
          if (buttonNumber != null) {
            setLastButton(`Button ${buttonNumber}`)
            hitSeq.current += 1
            setLastHit({ button: buttonNumber, seq: hitSeq.current })
          }
        } else if (data.type === "button-released") {
          const buttonNumber = data.value?.button
          if (buttonNumber != null) {
            setLastButton(`Button ${buttonNumber}`)
          }
        } else if (data.type === "volume") {
          const parsedVolume = Number(data.value)
          if (!Number.isNaN(parsedVolume)) {
            setVolume(parsedVolume)
          }
        } else if (data.type === "instrument") {
          setCurrentInstrument(data.value)
        }

      } catch (e) {
        console.error('Error parsing message:', e)
      }
    }

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    wsRef.current.onclose = () => {
      console.log('Disconnected from WebSocket server')
    }

    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  // Send message on Enter key
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && message.trim() && wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(
        {
          type: "message",
          value: message
        }
      ))

      setMessage('')
    }
  }

  const handleButtonClick = () => {
    const newState = !buttonState
    setButtonState(newState)
    wsRef.current.send(JSON.stringify(
      {
        type: "led",
        value: newState ? "on" : "off"
      }
    ))
  }

  const buttonClassName = lastButton
    ? lastButton.toLowerCase().replace(' ', '')
    : ''

  const instrumentClassName = currentInstrument
    ? `instrument-${currentInstrument.toLowerCase()}`
    : ''

  const orbScale = 0.75 + (volume / 100) * 0.4
  const orbGlow = 0.75 + (volume / 100) * 1.2

  return (
  <>
    <Navbar />

    <Routes>

      <Route
        path="/"
        element={<Hero />}
      />

      <Route
        path="/instrument"
        element={<Instrument />}
      />

      <Route
        path="/sounds"
        element={<SoundProfiles />}
      />

      <Route
        path="/band"
        element={<Band />}
      />

      <Route
        path="/live"
        element={
          <section id="live">

            <div className="rave-container">

              <div className="orb-system">
                <div className="orb-sigil" />

                <div className="orbit-ring orbit-ring-1">
                  <span className="orbit-particle orbit-particle-1" />
                </div>
                <div className="orbit-ring orbit-ring-2">
                  <span className="orbit-particle orbit-particle-2" />
                </div>
                <div className="orbit-ring orbit-ring-3">
                  <span className="orbit-particle orbit-particle-3" />
                </div>

                <div
                  className={`visualizer-orb ${buttonClassName} ${instrumentClassName}`.trim()}
                  style={{
                    '--orb-scale': orbScale.toFixed(2),
                    '--orb-glow': orbGlow.toFixed(2)
                  }}
                />
              </div>

              <div className="last-input">
                Last Input: {lastButton || 'Waiting..'} • Volume: {volume}% • Instrument: {currentInstrument || 'Waiting..'}
              </div>

            </div>

          </section>
        }
      />

      <Route
        path="/play"
        element={
          <RhythmGame
            lastHit={lastHit}
            currentInstrument={currentInstrument}
          />
        }
      />

      <Route
        path="/music"
        element={<Music />}
      />

    </Routes>
  </>
)
}

export default App
