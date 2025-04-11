import React, { useState } from 'react';
import { sendCommand } from '../../config/config';
import './Joystick.css';

export default function ServoToyController() {
  const [activeDirection, setActiveDirection] = useState('stop');

  const sendDirection = (direction) => {
    sendCommand({
      type: 'cat-toy',
      payload: {
        direction: direction
      }
    });
    setActiveDirection(direction);
  };

  const handleMouseDown = (direction) => () => sendDirection(direction);
  const handleMouseUp = () => sendDirection('stop');

  return (
    <div className="servo-toy-controller">
      <div className="triangle-wrapper">
        <button
          className={`triangle-button left ${activeDirection === 'left' ? 'active' : ''}`}
          onMouseDown={handleMouseDown('left')}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          Left
        </button>
      </div>
      <div className="triangle-wrapper">
        <button
          className={`triangle-button right ${activeDirection === 'right' ? 'active' : ''}`}
          onMouseDown={handleMouseDown('right')}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          Right
        </button>
      </div>
    </div>
  );
}
