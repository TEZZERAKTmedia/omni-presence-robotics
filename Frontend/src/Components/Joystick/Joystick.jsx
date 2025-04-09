import React, { useState, useRef, useEffect } from 'react';
import './Joystick.css';
import { connectWebSocket, sendCommand } from '../../config/config';

const DEAD_ZONE = 0.05;

export default function JoystickController() {
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

    const normX = +(clampedX / radius).toFixed(2); // strafe
    const normY = +(clampedY / radius).toFixed(2); // forward/backward
    const rotation = 0;

    const xInput = Math.abs(normX) < DEAD_ZONE ? 0 : normX;
    const yInput = Math.abs(normY) < DEAD_ZONE ? 0 : normY;

    // Mecanum drive equations
    let fl = yInput + xInput + rotation;
    let fr = yInput - xInput - rotation;
    let bl = yInput - xInput + rotation;
    let br = yInput + xInput - rotation;

    // Normalize to max magnitude of 1
    const max = Math.max(1, Math.abs(fl), Math.abs(fr), Math.abs(bl), Math.abs(br));
    fl /= max;
    fr /= max;
    bl /= max;
    br /= max;

    setPosition({ x: clampedX, y: clampedY });

    const payload = {
      frontLeft: fl,
      frontRight: fr,
      backLeft: bl,
      backRight: br
    };

    sendCommand({ type: 'joystick', payload });
  };

  const reset = () => {
    setDragging(false);
    setPosition({ x: 0, y: 0 });

    sendCommand({
      type: 'joystick',
      payload: {
        frontLeft: 0,
        frontRight: 0,
        backLeft: 0,
        backRight: 0
      }
    });
  };

  const sendDpadCommand = (fl, fr, bl, br) => {
    sendCommand({
      type: 'joystick',
      payload: { frontLeft: fl, frontRight: fr, backLeft: bl, backRight: br }
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

      {/* D-Pad Buttons */}
      <button onClick={() => sendDpadCommand(-1, 1, -1, 1)} className="joystick-arrow left">⬅️</button>
      <button onClick={() => sendDpadCommand(1, -1, 1, -1)} className="joystick-arrow right">➡️</button>
      <button onClick={() => sendDpadCommand(1, 1, 1, 1)} className="joystick-arrow up">⬆️</button>
      <button onClick={() => sendDpadCommand(-1, -1, -1, -1)} className="joystick-arrow down">⬇️</button>
    </div>
  );
}
