import React, { useState } from 'react';
import JoystickController from './Joystick';
import TerrainJoystickController from './TerrainJoystick';
import './JoystickToggle.css';

const modeInfo = {
  mecanum: "Mecanum Drive: Uses four mecanum wheels to move omnidirectionally—forward, backward, strafe, and rotate in place.",
  terrain: "Terrain Drive: Uses traditional skid‑steering (differential) for better traction on uneven or off‑road surfaces.",
};

export default function JoystickToggle() {
  const [mode, setMode] = useState('terrain');
  const [showInfoFor, setShowInfoFor] = useState(null);

  const handleModeChange = (newMode) => {
    setMode(newMode);
    setShowInfoFor(null);
  };

  return (
    <div className="joystick-toggle-wrapper">
      {/* Mode Switch UI */}
      <div className="mode-toggle-circle">
        <div className={`toggle-indicator ${mode}`} />
        <button
          onClick={() => handleModeChange('mecanum')}
          className={mode === 'mecanum' ? 'active' : ''}
        >
          M⚙️
        </button>
        <button
          onClick={() => handleModeChange('terrain')}
          className={mode === 'terrain' ? 'active' : ''}
        >
          T⛰️
        </button>
      </div>

      {/* Mode Name + Info Button */}
      <div className="mode-info">
        <span className="mode-name">
          {mode === 'mecanum' ? 'Mecanum Drive' : 'Terrain Drive'}
        </span>
        <button
          className="info-button"
          onClick={() => setShowInfoFor(mode)}
        >
          ℹ️
        </button>
      </div>

      {/* Modal */}
      {showInfoFor && (
        <div
          className="modal-overlay"
          onClick={() => setShowInfoFor(null)}
        >
          <div
            className="modal-content"
            onClick={e => e.stopPropagation()}
          >
            <button
              className="modal-close"
              onClick={() => setShowInfoFor(null)}
            >
              ✖️
            </button>
            <h2>
              {showInfoFor === 'mecanum' ? 'Mecanum Drive' : 'Terrain Drive'}
            </h2>
            <p>{modeInfo[showInfoFor]}</p>
          </div>
        </div>
      )}

      {/* Joystick Component */}
      {mode === 'mecanum' ? (
        <JoystickController />
      ) : (
        <TerrainJoystickController />
      )}
    </div>
  );
}
