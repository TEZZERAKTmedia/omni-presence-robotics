import React, { useState, useEffect } from 'react';
import './EnvironmentManager.css';

const EnvironmentManager = () => {
  const [environments, setEnvironments] = useState([]);
  const [newName, setNewName] = useState('');
  const [selectedEnv, setSelectedEnv] = useState(null);

  useEffect(() => {
    fetch('/api/environments')
      .then(res => res.json())
      .then(setEnvironments)
      .catch(err => console.error("Failed to load environments:", err));
  }, []);

  const startNewEnvironment = async () => {
    if (!newName) return;
    const res = await fetch('/api/environments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: newName }),
    });
    const updated = await res.json();
    setEnvironments(updated);
    setNewName('');
  };

  const deleteEnvironment = async (name) => {
    if (!window.confirm(`Delete "${name}"?`)) return;
    const res = await fetch(`/api/environments/${name}`, { method: 'DELETE' });
    const updated = await res.json();
    setEnvironments(updated);
    if (selectedEnv === name) setSelectedEnv(null);
  };

  const renameEnvironment = async (oldName, newName) => {
    const res = await fetch(`/api/environments/${oldName}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ newName }),
    });
    const updated = await res.json();
    setEnvironments(updated);
  };

  return (
    <div className="env-manager">
      <h2>🌍 Environment Manager</h2>

      <div className="env-create">
        <input
          type="text"
          placeholder="New environment name"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
        />
        <button onClick={startNewEnvironment}>Start Mapping</button>
      </div>

      <ul className="env-list">
        {environments.map((env) => (
          <li key={env}>
            <span onClick={() => setSelectedEnv(env)}>{env}</span>
            <button onClick={() => deleteEnvironment(env)}>🗑</button>
            <button
              onClick={() => {
                const newName = prompt("Rename environment", env);
                if (newName) renameEnvironment(env, newName);
              }}
            >
              ✏️
            </button>
          </li>
        ))}
      </ul>

      {selectedEnv && (
        <div className="env-preview">
          <h3>📡 Selected: {selectedEnv}</h3>
          <button onClick={() => console.log("Load and render map:", selectedEnv)}>
            Render Map
          </button>
        </div>
      )}
    </div>
  );
};

export default EnvironmentManager;
