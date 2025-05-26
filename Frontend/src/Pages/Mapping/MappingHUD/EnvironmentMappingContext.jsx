import { createContext, useState, useEffect, useRef } from 'react'

export const EnvironmentMappingContext = createContext()

export function EnvironmentMappingProvider({ children }) {
  const [slamReady, setSlamReady] = useState(false)
  const [pose, setPose] = useState(null)
  const [landmarks, setLandmarks] = useState([])
  const [exploring, setExploring] = useState(false)
  const [explorationComplete, setExplorationComplete] = useState(false)

  const wsRef = useRef(null)

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8780')
    wsRef.current = ws

    ws.onopen = () => setSlamReady(true)
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data)
      if (msg.pose) setPose(msg.pose)
      if (msg.landmarks) setLandmarks(msg.landmarks)
      if (msg.type === 'exploration_complete') {
        setExploring(false)
        setExplorationComplete(true)
      }
    }
    ws.onclose = () => setSlamReady(false)

    return () => ws.close()
  }, [])

  const send = (type, payload = {}) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type, payload }))
    }
  }

  const startExploration = () => {
    setExploring(true)
    send('start_exploration')
  }

  const stopExploration = () => {
    setExploring(false)
    send('stop_exploration')
  }

  return (
    <EnvironmentMappingContext.Provider value={{
      slamReady,
      pose,
      landmarks,
      exploring,
      explorationComplete,
      startExploration,
      stopExploration
    }}>
      {children}
    </EnvironmentMappingContext.Provider>
  )
}
