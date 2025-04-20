import React, { useEffect, useRef, useState } from 'react';
import './video.css';

const VideoFeed = () => {
  const containerRef = useRef(null);
  const socketRef = useRef(null);
  const reconnectRef = useRef(null);
  const imageRef = useRef(null);
  const [activeCamera, setActiveCamera] = useState('USB');

  const wsUrl = activeCamera === 'CSI'
    ? 'ws://localhost:8765'
    : 'ws://localhost:8770';

  useEffect(() => {
    const connectSocket = () => {
      console.log(`Connecting to video stream: ${wsUrl}`);
      const socket = new WebSocket(wsUrl);
      socketRef.current = socket;

      socket.onopen = () => {
        console.log('[WebSocket] Connected to video stream');
        clearInterval(reconnectRef.current);
      };

      socket.onmessage = (event) => {
        if (event.data && event.data.length > 100) {
          const frameUrl = `data:image/jpeg;base64,${event.data}`;
          if (imageRef.current) {
            imageRef.current.src = frameUrl;
          }
        }
      };

      socket.onerror = (error) => {
        console.error('[WebSocket] Video stream error:', error);
      };

      socket.onclose = () => {
        console.warn('[WebSocket] Video stream disconnected, attempting to reconnect...');
        reconnectRef.current = setInterval(() => {
          if (!socketRef.current || socketRef.current.readyState === WebSocket.CLOSED) {
            connectSocket();
          }
        }, 2000);
      };
    };

    connectSocket();

    return () => {
      clearInterval(reconnectRef.current);
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [wsUrl, activeCamera]);

  const toggleFullscreen = () => {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else if (containerRef.current) {
      containerRef.current.requestFullscreen();
    }
  };

  const handleCameraChange = (event) => {
    if (imageRef.current) {
      imageRef.current.src = ''; // Clear old frame
    }
    setActiveCamera(event.target.value);
  };

  return (
    <div
      className="video-feed"
      ref={containerRef}
      onClick={toggleFullscreen}
      title="Click to toggle fullscreen"
    >
      {/* Camera toggle UI */}
      <div className="camera-toggle">
        <label htmlFor="cameraSelect">Camera: </label>
        <select id="cameraSelect" value={activeCamera} onChange={handleCameraChange}>
          <option value="CSI">CSI Camera</option>
          <option value="USB">USB Camera</option>
        </select>
      </div>

      <img
        ref={imageRef}
        alt="Live Feed"
        style={{ width: '100%', maxHeight: '80vh', objectFit: 'contain' }}
      />
    </div>
  );
};

export default VideoFeed;
