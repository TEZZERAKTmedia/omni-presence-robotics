import React, { useEffect, useState, useRef } from 'react';
import './video.css';

const VideoFeed = () => {
  const [imageSrc, setImageSrc] = useState('');
  const containerRef = useRef(null);
  const socketRef = useRef(null);
  const reconnectRef = useRef(null);

  useEffect(() => {
    const connectSocket = () => {
      const socket = new WebSocket('ws://localhost:8765');
      socketRef.current = socket;

      socket.onopen = () => {
        console.log('[WebSocket] Connected to video stream');
        clearInterval(reconnectRef.current);
      };

      socket.onmessage = (event) => {
        if (event.data && event.data.length > 100) {
          setImageSrc(`data:image/jpeg;base64,${event.data}`);
        }
      };

      socket.onerror = (error) => {
        console.error('[WebSocket] Video stream error:', error);
      };

      socket.onclose = () => {
        console.warn('[WebSocket] Disconnected from video stream, trying to reconnect...');
        // Try to reconnect every 2 seconds
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
      socketRef.current?.close();
    };
  }, []);

  const toggleFullscreen = () => {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else if (containerRef.current) {
      containerRef.current.requestFullscreen();
    }
  };

  return (
    <div
      className="video-feed"
      ref={containerRef}
      onClick={toggleFullscreen}
      title="Click to toggle fullscreen"
    >
      {imageSrc ? (
        <img src={imageSrc} alt="Live Feed" />
      ) : (
        <p style={{ color: '#fff', textAlign: 'center' }}>Waiting for video stream...</p>
      )}
    </div>
  );
};

export default VideoFeed;
