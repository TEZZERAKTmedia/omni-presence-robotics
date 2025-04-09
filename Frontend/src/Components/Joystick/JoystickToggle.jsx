import React, { useState } from 'react';
import JoystickController from './Joystick';
import TerrainJoystickController from './TerrainJoystick';
import './JoystickToggle.css';

export default function JoystickToggle() {
  const [mode, setMode] = useState('mecanum');

  return (
    <div className="joystick-toggle-wrapper">
      {/* Mode Switch UI */}
      <div className="mode-toggle-circle">
        <div className={`toggle-indicator ${mode}`} />
        <button onClick={() => setMode('mecanum')} className={mode === 'mecanum' ? 'active' : ''}>⚙️</button>
        <button onClick={() => setMode('terrain')} className={mode === 'terrain' ? 'active' : ''}>⛰️</button>
      </div>

      {/* Joystick Component */}
      {mode === 'mecanum' ? <JoystickController /> : <TerrainJoystickController />}
    </div>
  );
}
