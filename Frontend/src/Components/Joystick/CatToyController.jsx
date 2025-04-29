import React, { useState } from 'react';
import { sendCommand } from '../../config/config';
import './Joystick.css';

export default function ServoToyController() {
  const [activeDirection, setActiveDirection] = useState('stop');
  const [speed, setSpeed] = useState(1);

  const speeds = [1, 2, 4, 8];

  const sendDirection = (direction, speedMultiplier) => {
    sendCommand({
      type: 'cat-toy',
      payload: {
        direction: direction,
        speed: speedMultiplier
      }
    });
    setActiveDirection(direction);
  };

  const handleMouseDown = (direction) => () => sendDirection(direction, speed);
  const handleMouseUp = () => sendDirection('stop', speed);

  return (
    <div className="servo-toy-controller">
      <div className="speed-selector">
        <h4>Cat Toy</h4>
        <label>Speed:</label>
        <select value={speed} onChange={(e) => setSpeed(parseInt(e.target.value, 10))}>
          {speeds.map((s) => (
            <option key={s} value={s}>{s}x</option>
          ))}
        </select>
      </div>
      <div className="triangle-wrapper">
      <button
        className={`triangle-button left ${activeDirection === 'left' ? 'active' : ''}`}
        onMouseDown={handleMouseDown('left')}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <span className="triangle-label">L</span>
      </button>

      </div>
      <div className="triangle-wrapper">
      <button
        className={`triangle-button right ${activeDirection === 'right' ? 'active' : ''}`}
        onMouseDown={handleMouseDown('right')}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <span className="triangle-label">R</span>
      </button>

      </div>
    </div>
  );
}
