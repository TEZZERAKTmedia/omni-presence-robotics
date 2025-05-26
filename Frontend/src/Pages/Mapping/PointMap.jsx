// PointMap.jsx
import React, { useMemo } from 'react'
import * as THREE from 'three'

export default function PointMap({ points }) {
  const { positions, colors } = useMemo(() => {
    const pos = new Float32Array(points.length * 3)
    const col = new Float32Array(points.length * 3)
    points.forEach((p, i) => {
      pos.set([p.x, p.y, p.z], i * 3)
      const c = new THREE.Color(p.color || '#ffffff')
      col.set([c.r, c.g, c.b], i * 3)
    })
    return { positions: pos, colors: col }
  }, [points])

  return (
    <points>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={positions.length / 3}
          array={positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={colors.length / 3}
          array={colors}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial size={0.03} vertexColors />
    </points>
  )
}
