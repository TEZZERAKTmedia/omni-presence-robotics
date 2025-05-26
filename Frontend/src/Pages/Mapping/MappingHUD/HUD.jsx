import React, { useContext } from 'react'
import { EnvironmentMappingContext } from './EnvironmentMappingContext'

export default function StatusHUD() {
  const {
    slamReady,
    exploring,
    pose,
    landmarks,
    explorationComplete
  } = useContext(EnvironmentMappingContext)

  return (
    <div style={styles.hud}>
      <h4 style={styles.title}>🔍 Mapping Status</h4>
      <p><strong>SLAM:</strong> {slamReady ? '✅ Ready' : '⏳ Connecting...'}</p>
      <p><strong>Pose:</strong> {pose ? `${pose.x.toFixed(2)}, ${pose.y.toFixed(2)}` : 'N/A'}</p>
      <p><strong>Landmarks:</strong> {landmarks.length}</p>
      <p><strong>Status:</strong> {explorationComplete ? '✅ Complete' : exploring ? '🧠 Scanning...' : 'Paused'}</p>
    </div>
  )
}

const styles = {
  hud: {
    position: 'fixed',
    bottom: '33%',
    left: '50%',
    transform: 'translateX(-50%)',
    backgroundColor: 'rgba(0, 0, 0, 0.75)',
    color: 'white',
    padding: '1rem 2rem',
    borderRadius: '12px',
    fontSize: '0.9rem',
    boxShadow: '0 0 10px rgba(0,255,255,0.2)',
    zIndex: 1000,
    pointerEvents: 'none' // allows clicks to go through to canvas
  },
  title: {
    fontSize: '1rem',
    marginBottom: '0.5rem',
    color: '#00ffff'
  }
}
