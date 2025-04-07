import React, { useState, useRef, useEffect } from 'react';
import './Joystick.css';
import { connectWebSocket, sendCommand } from '../../config/config';

export default function JoystickController() {
  const padRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [servoValues, setServoValues] = useState({ servo0: 0, servo1: 0 });

  useEffect(() => {
    connectWebSocket('ws://localhost:8001'); // or your ngrok domain
  }, []);

  useEffect(() => {
    if (dragging) {
        sendCommand({ type: 'camera-servo', payload: servoValues });

    }
  }, [servoValues, dragging]);
  const handleTouchStart = (e) => {
    setDragging(true);
    updatePosition(e.touches[0]); // get first touch point
  };
  
  const handleTouchMove = (e) => {
    if (dragging) {
      updatePosition(e.touches[0]); // use touch instead of mouse
    }
  };
  
  const handleTouchEnd = () => {
    setDragging(false);
    setPosition({ x: 0, y: 0 });
    setServoValues({ servo0: 0, servo1: 0 });
  };

  const handleMouseDown = (e) => {
    setDragging(true);
    updatePosition(e);
  };

  const handleMouseUp = () => {
    setDragging(false);
    setPosition({ x: 0, y: 0 });
    setServoValues({ servo0: 0, servo1: 0 });
  };

  const handleMouseMove = (e) => {
    if (dragging) {
      updatePosition(e);
    }
  };

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

    const normalizedX = +(clampedX / radius).toFixed(2);
    const normalizedY = +(clampedY / radius).toFixed(2);

    setPosition({ x: clampedX, y: clampedY });
    setServoValues({
      servo0: normalizedX,
      servo1: -normalizedY
    });
  };

  const handleClick = (direction) => {
    let update = { servo0: 0, servo1: 0 };
    switch (direction) {
      case 'left': update.servo0 = -1; break;
      case 'right': update.servo0 = 1; break;
      case 'up': update.servo1 = 1; break;
      case 'down': update.servo1 = -1; break;
    }
    setServoValues(update);
    console.log('Manual D-pad click:', update);
  };

  useEffect(() => {
    if (dragging) {
      console.log('Joystick movement:', servoValues);
    }
  }, [servoValues, dragging]);

  return (
    <div
      ref={padRef}
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseUp}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      className="joystick-container"
    >
      <div
        className="joystick-knob"
        style={{ transform: `translate(${position.x}px, ${position.y}px)` }}
      />
      <button onClick={() => handleClick('left')} className="joystick-arrow left">⬅️</button>
      <button onClick={() => handleClick('right')} className="joystick-arrow right">➡️</button>
      <button onClick={() => handleClick('up')} className="joystick-arrow up">⬆️</button>
      <button onClick={() => handleClick('down')} className="joystick-arrow down">⬇️</button>
            {/* Optional: Display servo values 
      <div className="joystick-info">
        <div>Servo0 (horizontal): {servoValues.servo0}</div>
        <div>Servo1 (vertical): {servoValues.servo1}</div>
      </div>
      */}
    </div>
  );
}
