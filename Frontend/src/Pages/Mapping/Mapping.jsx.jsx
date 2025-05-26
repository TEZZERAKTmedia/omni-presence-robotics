import React, { useState } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import PointMap from './PointMap'
import FallbackScene from './FallbackScene'
// import SimulatedMapping from './MappingAnimation/SimulatedMapping' // 🔁 temporarily disabled
import EnvironmentOverlayModal from './EnvironmentManager'
import StatusHUD from './MappingHUD/HUD'
import { EnvironmentMappingProvider } from './MappingHUD/EnvironmentMappingContext'

export default function SceneCanvas({ points }) {
  const [startSim, setStartSim] = useState(false)
  const [mappingStarted, setMappingStarted] = useState(false)
  const [showEnvOverlay, setShowEnvOverlay] = useState(false)
  const [showMappingUI, setShowMappingUI] = useState(false)

  const hasPoints = Array.isArray(points) && points.length > 0

  const handleStartMapping = () => {
    setStartSim(true)
    setTimeout(() => {
      setShowMappingUI(true)
      setStartSim(false)
    }, 1000)
  }

  const handleEnvSelected = (envName) => {
    console.log("Selected:", envName)
  }

  const handleNewMappingStart = () => {
    setShowEnvOverlay(false)
    setMappingStarted(true)
  }

  return (
    <>
      <EnvironmentMappingProvider>
        <Canvas camera={{ position: [0, 2, 5], fov: 60 }}>
          <ambientLight />
          <pointLight position={[10, 10, 10]} />
          <OrbitControls />

          {/* 🔁 Simulated Mapping Temporarily Disabled */}
          {/* {startSim ? (
            <SimulatedMapping />
          ) : hasPoints ? (
            <PointMap points={points} />
          ) : (
            <FallbackScene onStart={handleStartMapping} />
          )} */}

          {hasPoints ? (
            <PointMap points={points} />
          ) : (
            <FallbackScene onStart={handleStartMapping} />
          )}
        </Canvas>

        <StatusHUD />

        {showEnvOverlay && (
          <EnvironmentOverlayModal
            onSelect={handleEnvSelected}
            onStartMapping={handleNewMappingStart}
          />
        )}
      </EnvironmentMappingProvider>
    </>
  )
}
