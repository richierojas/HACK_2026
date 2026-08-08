import { useState, useEffect, useRef } from 'react'
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
    wsRef.current = new WebSocket('ws://localhost:8765')

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
      <section id="center">

        {/* WebSocket Message Input */}
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type message and press Enter to send"
          style={{
            marginTop: '20px',
            padding: '10px',
            borderRadius: '4px',
            border: '1px solid #ccc',
            width: '300px',
            fontSize: '16px'
          }}
        />

        <div style={{
          marginTop: '30px',
          padding: '15px',
          border: '1px solid #ddd',
          borderRadius: '4px',
          width: '100px',
          maxHeight: '350px',
          overflowY: 'auto',
          backgroundColor: '#f9f9f9'
        }}>
          <button 
            style={{ 
              marginTop: 0,
              width: '80px',
              height: '80px',
              borderRadius: '50%',
              borderWidth: '5px',
              backgroundColor:  masterSwitchState ? (buttonState ? 'red' : 'lightgray') : 'gray'
            }} 
            disabled = {!masterSwitchState}
            onClick={handleButtonClick}
            />
        </div>

        {/* Chat Logs Display */}
        <div style={{
          marginTop: '30px',
          padding: '15px',
          border: '1px solid #ddd',
          borderRadius: '4px',
          width: '350px',
          maxHeight: '400px',
          overflowY: 'auto',
          backgroundColor: '#f9f9f9'
        }}>
          <h3 style={{ marginTop: 0 }}>Chat Logs</h3>
          {chatLogs.length === 0 ? (
            <p style={{ color: '#999' }}>No messages yet</p>
          ) : (
            chatLogs.map((log, index) => (
              <div key={index} style={{
                marginBottom: '10px',
                padding: '8px',
                backgroundColor: '#f0f0f0',
                borderRadius: '3px',
                borderLeft: `3px solid #666`
              }}>
                <div style={{ fontSize: '12px', color: '#666' }}>
                  {log.timestamp}
                </div>
                <div style={{ fontSize: '14px', marginTop: '4px' }}>
                  {log.message}
                </div>
              </div>
            ))
          )}
        </div>
        {/*Rave Visualizer*/}
        <div style={{
          marginTop: '30px',
          textAlign: 'center',
        }}>
          <h3>Rave Visualizer</h3>
          <div style={{
            width: '200px',
            height: '200px',
            margin: '20px auto',
            borderRadius: '50%',
            background: 
              lastButton === 'Button 1' ? 'radial-gradient(circle, #ff0000, #ff6666)' :
              lastButton === 'Button 2' ? 'radial-gradient(circle, #00ff00, #66ff66)' :
              lastButton === 'Button 3' ? 'radial-gradient(circle, #0000ff, #6666ff)' :
              lastButton === 'Button 4' ? 'radial-gradient(circle, #ffff00, #ffff66)' :
              lastButton === 'Button 5' ? 'radial-gradient(circle, #ff00ff, #ff66ff)' :
              lastButton === 'Button 6' ? 'radial-gradient(circle, #00ffff, #66ffff)' :
              lastButton === 'Button 7' ? 'radial-gradient(circle, #ffa500, #ffb733)' :
              lastButton === 'Button 8' ? 'radial-gradient(circle, #800080, #993399)' :
              'radial-gradient(circle, #cccccc, #eeeeee)',
            transform: lastButton? 'scale(1.2)' : 'scale(1)',
            transition: '0.5s'
          }} />
          <h3>
            Last Input: {lastButton || 'Waiting...'}
          </h3>
        </div>

      </section>
    </>
  )
}

export default App
