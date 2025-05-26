import React, { useRef, useEffect, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import ProceduralPointMap from './ProceduralPointMap'
import * as THREE from 'three'

export default function SimulatedMapping() {
  const camRef = useRef()
  const [curve] = useState(() =>
    new THREE.CatmullRomCurve3(
      Array.from({ length: 10 }, () => new THREE.Vector3(
        (Math.random() - 0.5) * 10,
        (Math.random() - 0.5) * 5,
        (Math.random() - 0.5) * 10
      )),
      false,
      'centripetal'
    )
  )

  const cameraPos = useRef(0)

  useFrame(({ camera }) => {
    if (!curve) return
    cameraPos.current += 0.001
    if (cameraPos.current > 1) cameraPos.current = 0
    const pos = curve.getPointAt(cameraPos.current)
    const lookAt = curve.getPointAt((cameraPos.current + 0.01) % 1)

    camera.position.copy(pos)
    camera.lookAt(lookAt)
  })

  return (
    <>
      <ProceduralPointMap count={8000} />

      <mesh>
        <line>
          <bufferGeometry setFromPoints={curve.getPoints(50)} />
          <lineBasicMaterial color="#ff66cc" />
        </line>
      </mesh>
    </>
  )
}
