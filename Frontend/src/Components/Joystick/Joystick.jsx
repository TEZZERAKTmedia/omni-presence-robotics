import React, { useState, useRef, useEffect } from 'react';
import './Joystick.css';
import { connectWebSocket, sendCommand } from '../../config/config';

const DEAD_ZONE = 0.05;
const UPDATE_INTERVAL = 100;

export default function JoystickController() {
  const padRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [servoValues, setServoValues] = useState({ servo0: 0, servo1: 0 });

  useEffect(() => {
    connectWebSocket('ws://localhost:8001');
  }, []);

  useEffect(() => {
    if (!dragging) return;
    const interval = setInterval(() => {
      sendCommand({ type: 'joystick', payload: servoValues });
    }, UPDATE_INTERVAL);
    return () => clearInterval(interval);
  }, [dragging, servoValues]);

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

    const normX = +(clampedX / radius).toFixed(2); // steering
    const normY = +(clampedY / radius).toFixed(2); // throttle

    // Apply dead zone
    const steering = Math.abs(normX) < DEAD_ZONE ? 0 : normX;
    const throttle = Math.abs(normY) < DEAD_ZONE ? 0 : -normY; // invert so up = forward

    setPosition({ x: clampedX, y: clampedY });
    setServoValues({
      servo0: throttle,   // Apply throttle to all wheels
      servo1: steering    // Control steering servo
    });
  };

  const reset = () => {
    setDragging(false);
    setPosition({ x: 0, y: 0 });
    setServoValues({ servo0: 0, servo1: 0 });
    sendCommand({ type: 'joystick', payload: { servo0: 0, servo1: 0 } });
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
      <button onClick={() => setServoValues({ servo0: 0, servo1: -1 })} className="joystick-arrow left">⬅️</button>
      <button onClick={() => setServoValues({ servo0: 0, servo1: 1 })} className="joystick-arrow right">➡️</button>
      <button onClick={() => setServoValues({ servo0: 1, servo1: 0 })} className="joystick-arrow up">⬆️</button>
      <button onClick={() => setServoValues({ servo0: -1, servo1: 0 })} className="joystick-arrow down">⬇️</button>
    </div>
  );
}
