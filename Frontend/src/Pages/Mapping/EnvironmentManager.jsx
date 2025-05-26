import React, { useState, useEffect } from 'react'

export default function EnvironmentOverlayModal({ onSelect, onStartMapping }) {
  const [environments, setEnvironments] = useState([])
  const [newName, setNewName] = useState('')
  const [isCreating, setIsCreating] = useState(false)

  useEffect(() => {
    fetch('/api/environments')
      .then(res => res.json())
      .then(setEnvironments)
  }, [])

  const createNewEnvironment = async () => {
    if (!newName) return
    setIsCreating(true)
    await fetch('/api/environments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: newName }),
    })
    const updated = await fetch('/api/environments').then(res => res.json())
    setEnvironments(updated)
    setNewName('')
    setIsCreating(false)
    onStartMapping() // transition into MappingAutomationPage
  }

  const deleteEnvironment = async (name) => {
    if (!window.confirm(`Delete "${name}"?`)) return
    await fetch(`/api/environments/${name}`, { method: 'DELETE' })
    const updated = await fetch('/api/environments').then(res => res.json())
    setEnvironments(updated)
  }

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      backgroundColor: 'rgba(0,0,0,0.7)',
      color: 'white',
      padding: '2rem',
      zIndex: 9999,
      display: 'flex',
      flexDirection: 'column',
      gap: '1rem'
    }}>
      <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>🌐 Manage Environments</h2>

      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <input
          style={{
            backgroundColor: 'white',
            color: 'black',
            padding: '0.5rem',
            borderRadius: '4px',
            flex: '1'
          }}
          placeholder="New Environment Name"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
        />
        <button
          style={{
            backgroundColor: '#16a34a',
            color: 'white',
            padding: '0.5rem 1rem',
            borderRadius: '4px',
            fontWeight: 'bold'
          }}
          onClick={createNewEnvironment}
        >
          Create
        </button>
      </div>

      {isCreating && (
        <div style={{
          width: '100%',
          height: '8px',
          borderRadius: '4px',
          backgroundColor: '#2d2d2d',
          overflow: 'hidden'
        }}>
          <div style={{
            height: '100%',
            width: '100%',
            backgroundColor: '#22c55e',
            animation: 'pulse 1s infinite'
          }} />
        </div>
      )}

      <ul style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {environments.map((env) => (
          <li
            key={env}
            style={{
              backgroundColor: '#2d2d2d',
              padding: '0.75rem 1rem',
              borderRadius: '6px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}
          >
            <span>{env}</span>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                onClick={() => onSelect(env)}
                style={{
                  backgroundColor: '#3b82f6',
                  color: 'white',
                  padding: '0.25rem 0.75rem',
                  borderRadius: '4px'
                }}
              >
                Load
              </button>
              <button
                onClick={() => deleteEnvironment(env)}
                style={{
                  backgroundColor: '#ef4444',
                  color: 'white',
                  padding: '0.25rem 0.75rem',
                  borderRadius: '4px'
                }}
              >
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
