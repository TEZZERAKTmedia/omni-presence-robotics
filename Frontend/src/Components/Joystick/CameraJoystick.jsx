import React, { useState, useRef, useEffect } from 'react';
import './Joystick.css';
import { connectWebSocket, sendCommand } from '../../config/config';

const DEAD_ZONE = 0.05;
const UPDATE_INTERVAL = 100;

export default function CameraJoystick() {
  const padRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [panTilt, setPanTilt] = useState({ pan: 0, tilt: 0 });

  // Connect to backend on mount
  useEffect(() => {
    connectWebSocket('ws://localhost:8001');
  }, []);

  // Send live updates while dragging
  useEffect(() => {
    if (!dragging) return;
    const interval = setInterval(() => {
      sendCommand({ type: 'camera-servo', payload: panTilt });
    }, UPDATE_INTERVAL);
    return () => clearInterval(interval);
  }, [dragging, panTilt]);

  // Handle joystick movement
  useEffect(() => {
    if (!dragging) return;

    const handleMove = (e) => {
      if (e.touches) updatePosition(e.touches[0]);
      else updatePosition(e);
    };

    const handleUp = () => reset();

    window.addEventListener('mousemove', handleMove);
    window.addEventListener('mouseup', handleUp);
    window.addEventListener('touchmove', handleMove, { passive: false });
    window.addEventListener('touchend', handleUp);

    return () => {
      window.removeEventListener('mousemove', handleMove);
      window.removeEventListener('mouseup', handleUp);
      window.removeEventListener('touchmove', handleMove);
      window.removeEventListener('touchend', handleUp);
    };
  }, [dragging]);

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

    const normX = +(clampedX / radius).toFixed(2);
    const normY = +(clampedY / radius).toFixed(2);

    setPosition({ x: clampedX, y: clampedY });
    setPanTilt({
      pan: Math.abs(normX) < DEAD_ZONE ? 0 : normX,
      tilt: Math.abs(normY) < DEAD_ZONE ? 0 : -normY // Invert for typical tilt behavior
    });
  };

  const reset = () => {
    setDragging(false);
    setPosition({ x: 0, y: 0 });
    setPanTilt({ pan: 0, tilt: 0 });
    sendCommand({ type: 'camera-servo', payload: { pan: 0, tilt: 0 } });
  };

  const handleButton = (pan, tilt) => {
    const payload = { pan, tilt };
    setPanTilt(payload);
    sendCommand({ type: 'camera-servo', payload });
  };

  return (
    <div
      ref={padRef}
      className="joystick-container"
      onMouseDown={(e) => { setDragging(true); updatePosition(e); }}
      onTouchStart={(e) => { setDragging(true); updatePosition(e.touches[0]); }}
      onTouchMove={(e) => dragging && updatePosition(e.touches[0])}
      onTouchEnd={reset}
    >
      <div className="joystick-knob" style={{ transform: `translate(${position.x}px, ${position.y}px)` }} />

      <button onMouseDown={() => handleButton(-1, 0)} onMouseUp={reset} className="joystick-arrow left">⬅️</button>
      <button onMouseDown={() => handleButton(1, 0)} onMouseUp={reset} className="joystick-arrow right">➡️</button>
      <button onMouseDown={() => handleButton(0, 1)} onMouseUp={reset} className="joystick-arrow up">⬆️</button>
      <button onMouseDown={() => handleButton(0, -1)} onMouseUp={reset} className="joystick-arrow down">⬇️</button>
    </div>
  );
}
