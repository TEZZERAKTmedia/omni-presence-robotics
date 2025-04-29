import React, { useEffect, useRef, useState } from 'react';
import './video.css';

const VideoFeed = () => {
  const containerRef = useRef(null);
  const socketRef = useRef(null);
  const reconnectRef = useRef(null);
  const imageRef = useRef(null);
  const canvasRef = useRef(null); // new hidden canvas

  const [activeSide, setActiveSide] = useState('left'); // left or right
  const wsUrl = 'ws://localhost:8770'; // Only USB camera now

  useEffect(() => {
    const connectSocket = () => {
      const socket = new WebSocket(wsUrl);
      socketRef.current = socket;

      socket.onopen = () => clearInterval(reconnectRef.current);
      socket.onmessage = (event) => {
        if (event.data && event.data.length > 100 && imageRef.current) {
          const img = new Image();
          img.onload = () => {
            const canvas = canvasRef.current;
            const ctx = canvas.getContext('2d');
            canvas.width = img.width / 2;
            canvas.height = img.height;

            if (activeSide === 'left') {
              ctx.drawImage(img, 0, 0, img.width / 2, img.height, 0, 0, canvas.width, canvas.height);
            } else if (activeSide === 'right') {
              ctx.drawImage(img, img.width / 2, 0, img.width / 2, img.height, 0, 0, canvas.width, canvas.height);
            }

            imageRef.current.src = canvas.toDataURL('image/jpeg');
          };
          img.src = `data:image/jpeg;base64,${event.data}`;
        }
      };
      socket.onerror = (e) => console.error('[WebSocket] Error:', e);
      socket.onclose = () => {
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
  }, [wsUrl, activeSide]); // IMPORTANT: re-render when activeSide changes

  const toggleFullscreen = () => {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else {
      containerRef.current?.requestFullscreen();
    }
  };

  return (
    <div className="video-feed" ref={containerRef}>
      <div className="camera-toggle-buttons">
        {['left', 'right'].map(side => (
          <button
            key={side}
            className={activeSide === side ? 'active' : ''}
            onClick={() => setActiveSide(side)}
          >
            {side.charAt(0).toUpperCase() + side.slice(1)} Eye
          </button>
        ))}
      </div>

      {/* Hidden canvas */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      {/* Visible cropped image */}
      <img
        ref={imageRef}
        alt="Live Feed"
        onClick={toggleFullscreen}
        className="video-frame"
        title="Click to toggle fullscreen"
      />
    </div>
  );
};

export default VideoFeed;
