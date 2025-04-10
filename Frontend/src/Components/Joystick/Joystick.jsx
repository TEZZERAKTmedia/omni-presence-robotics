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
  useEffect(() => {
    if (!dragging) return;
  
    const handleMove = (e) => {
      if (e.touches) {
        updatePosition(e.touches[0]);
      } else {
        updatePosition(e);
      }
    };
  
    const handleUp = () => reset();
  
    // Global listeners so dragging works outside joystick
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
  
    const normX = clampedX / radius;
    const normY = clampedY / radius;
  
    const xInput = Math.abs(normX) < DEAD_ZONE ? 0 : +normX.toFixed(2);
    const yInput = Math.abs(normY) < DEAD_ZONE ? 0 : +normY.toFixed(2);
  
    // Mecanum drive equations
    let fl = yInput + xInput;
    let fr = yInput - xInput;
    let bl = yInput - xInput;
    let br = yInput + xInput;
  
    const max = Math.max(1, Math.abs(fl), Math.abs(fr), Math.abs(bl), Math.abs(br));
    fl /= max;
    fr /= max;
    bl /= max;
    br /= max;
  
    setPosition({ x: clampedX, y: clampedY });
  
    sendCommand({
      type: 'joystick',
      payload: { frontLeft: fl, frontRight: fr, backLeft: bl, backRight: br }
    });
  };
  

  const reset = () => {
    setDragging(false);
    setPosition({ x: 0, y: 0 });
  
    // Add small timeout to allow current direction to finish
    setTimeout(() => {
      sendCommand({
        type: 'joystick',
        payload: {
          frontLeft: 0,
          frontRight: 0,
          backLeft: 0,
          backRight: 0
        }
      });
    }, 100); // 100ms buffer
  };
  

  const sendDpadCommand = (fl, fr, bl, br) => {
    sendCommand({
      type: 'joystick',
      payload: { frontLeft: fl, frontRight: fr, backLeft: bl, backRight: br }
    });
  };

  return (
    <div className='outer-joystick-container'>
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
    </div>
  );
}
