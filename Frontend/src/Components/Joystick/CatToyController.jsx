import React from 'react';
import { sendCommand } from '../../config/config';
import './Joystick.css';

export default function ServoToyController() {
  const rotate = (direction) => {
    sendCommand({
      type: 'cat-toy-servo',
      payload: {
        servo2: direction
      }
    });
  };

  return (
    <div className="servo-toy-controller">
    <div className="triangle-wrapper">
      <button className="triangle-button left"></button>
    </div>
    <div className="triangle-wrapper">
      <button className="triangle-button right"></button>
    </div>
  </div>
  
  );
}
