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

  // Update position and send drive payload plus camera payload
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
  
    const xInput = Math.abs(normX) < DEAD_ZONE ? 0 : +normX.toFixed(2);
    const yInput = Math.abs(normY) < DEAD_ZONE ? 0 : +normY.toFixed(2);
  
    const forward = yInput;
    let left, right;

    if (Math.abs(forward) < 0.05 && Math.abs(xInput) >= DEAD_ZONE) {
      // In-place rotation: max torque
      left = -xInput;
      right = xInput;
    } else {
      // Standard curved driving
      const turn = xInput * 0.6;
      left = forward - turn;
      right = forward + turn;
    }

  
    const max = Math.max(1, Math.abs(left), Math.abs(right));
    left /= max;
    right /= max;
  
    setPosition({ x: clampedX, y: clampedY });
  
    // Only send terrain drive command now (no camera tilt)
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

  useEffect(() => {
    const handleMove = (e) => {
      if (!padRef.current || !dragging) return;
      const event = e.touches ? e.touches[0] : e;
      updatePosition(event); // update relative to joystick center
    };

    const handleUp = () => reset();

    window.addEventListener('mousemove', handleMove);
    window.addEventListener('mouseup', handleUp);
    window.addEventListener('touchmove', handleMove, { passive: false });
    window.addEventListener('touchend', handleUp);
    window.addEventListener('mouseleave', handleUp);

    return () => {
      window.removeEventListener('mousemove', handleMove);
      window.removeEventListener('mouseup', handleUp);
      window.removeEventListener('touchmove', handleMove);
      window.removeEventListener('touchend', handleUp);
      window.removeEventListener('mouseleave', handleUp);
    };
  }, [dragging]);

  return (
    <div className="outer-terrain-joystick-container">
      <div
        ref={padRef}
        className="terrain-joystick-container"
        onMouseDown={(e) => { setDragging(true); updatePosition(e); }}
        onTouchStart={(e) => { setDragging(true); updatePosition(e.touches[0]); }}
        onTouchMove={(e) => dragging && updatePosition(e.touches[0])}
        onTouchEnd={reset}
      >
        <div
          className="joystick-knob"
          style={{ transform: `translate(${position.x}px, ${position.y}px)` }}
        />
      </div>
    </div>
  );
}
