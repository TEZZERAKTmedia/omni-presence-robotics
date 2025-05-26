import React, { useRef, useState } from 'react'
import { Icosahedron, Html } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'

export default function FallbackScene({ onStart }) {
  const meshRef = useRef()
  const [isSpinningFast, setIsSpinningFast] = useState(false)

  // Animate spin
  useFrame(() => {
    if (meshRef.current) {
      const speed = isSpinningFast ? 0.08 : 0.01
      meshRef.current.rotation.y += speed
      meshRef.current.rotation.x += speed / 2
    }
  })

  const handleStart = () => {
    setIsSpinningFast(true)

    // Let animation play, then notify parent
    setTimeout(() => {
      onStart()  // this triggers simulation state in SceneCanvas
    }, 1000)
  }

  return (
    <>
      <Icosahedron args={[1, 1]} ref={meshRef}>
        <meshStandardMaterial color="#ff88cc" wireframe />
      </Icosahedron>

      <Html center>
        <div
          style={{
            color: 'white',
            background: 'rgba(0,0,0,0.6)',
            padding: '1rem',
            borderRadius: '8px',
            textAlign: 'center',
            marginTop: '-300%',
           
          }}
        >
          <p>No map loaded</p>
          <button onClick={handleStart} style={{ padding: '0.5rem 1rem'}}>
            Start Mapping
          </button>
        </div>
      </Html>
    </>
  )
}
