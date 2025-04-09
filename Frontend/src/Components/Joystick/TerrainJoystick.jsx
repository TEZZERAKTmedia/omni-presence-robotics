import React, { useState, useRef, useEffect } from 'react';
import './Joystick.css';
import { connectWebSocket, sendCommand } from '../../config/config';

const DEAD_ZONE = 0.05;

export default function TerrainJoystickController() {
  const padRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    connectWebSocket('ws://localhost:8001');
  }, []);

  const updatePosition = (e) => {
    const rect = padRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    const x = e.clientX - centerX;
    const y = e.clientY - centerY;
    const radius = rect.width / 2;

    const distance = Math.min(Math.sqrt(x * x + y * y), radius);
    const angle = Math.atan2(y, x);
    const clampedX = distance * Math.cos(angle);
    const clampedY = distance * Math.sin(angle);

    const normX = clampedX / radius;
    const normY = clampedY / radius;

    const xInput = Math.abs(normX) < DEAD_ZONE ? 0 : +normX.toFixed(2); // turn
    const yInput = Math.abs(normY) < DEAD_ZONE ? 0 : +normY.toFixed(2); // forward/backward

    // Terrain-style tank drive logic
    let left = yInput + xInput;
    let right = yInput - xInput;

    // Clamp to range [-1, 1]
    const max = Math.max(1, Math.abs(left), Math.abs(right));
    left /= max;
    right /= max;

    setPosition({ x: clampedX, y: clampedY });

    sendCommand({
      type: 'terrain',
      payload: {
        frontLeft: left,
        backLeft: left,
        frontRight: right,
        backRight: right
      }
    });
  };

  const reset = () => {
    setDragging(false);
    setPosition({ x: 0, y: 0 });

    sendCommand({
      type: 'terrain',
      payload: {
        frontLeft: 0,
        backLeft: 0,
        frontRight: 0,
        backRight: 0
      }
    });
  };

  return (
    <div
      ref={padRef}
      className="joystick-container"
      onMouseDown={(e) => { setDragging(true); updatePosition(e); }}
      onMouseMove={(e) => dragging && updatePosition(e)}
      onMouseUp={reset}
      onMouseLeave={reset}
      onTouchStart={(e) => { setDragging(true); updatePosition(e.touches[0]); }}
      onTouchMove={(e) => dragging && updatePosition(e.touches[0])}
      onTouchEnd={reset}
    >
      <div className="joystick-knob" style={{ transform: `translate(${position.x}px, ${position.y}px)` }} />
    </div>
  );
}
