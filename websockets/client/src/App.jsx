import { useState, useEffect, useRef } from 'react'
import { Routes, Route } from 'react-router'

import { Navbar } from './components/Navbar.jsx'
import { Hero } from './components/Hero.jsx'
import { Instrument } from './components/Instrument.jsx'
import { SoundProfiles } from './components/SoundProfiles.jsx'
import { Band } from './components/Band.jsx'
import { Music } from './components/Music.jsx'

import './App.css'

function App() {
  const [count, setCount] = useState(0)
  const [message, setMessage] = useState('')
  const [chatLogs, setChatLogs] = useState([])
  const [masterSwitchState, setMasterSwitchState] = useState(false)
  const [buttonState, setButtonState] = useState(true)
  const [lastButton, setLastButton] = useState(null)

  const wsRef = useRef(null)

  const buttonHandler = () => {
    //Fill this out
    setMasterSwitchState(0)
  }

  // Initialize WebSocket connection
  useEffect(() => {
    // Connect to WebSocket server
    wsRef.current = new WebSocket('ws://0.0.0.0:8765')

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

              <div
                className={`visualizer-orb ${
                  lastButton
                    ? lastButton.toLowerCase().replace(' ', '')
                    : ''
                }`}
              />

              <div className="last-input">
                Last Input: {lastButton || 'Waiting..'}
              </div>

            </div>

          </section>
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
