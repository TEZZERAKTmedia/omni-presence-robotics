import React, { useEffect, useRef, useState } from 'react';
import './video.css';

const cameraInfo = {
  CSI: "CSI Camera: Uses the Pi’s native camera interface (e.g. the official PiCam). Lower latency, high integration with libcamera but blocks /dev/video0 from USB webcams.",
  USB: "USB Camera: Uses any UVC-compatible USB webcam. Easy plug‑and‑play, works with OpenCV VideoCapture, but slightly higher latency compared to CSI.",
};

const VideoFeed = () => {
  const containerRef = useRef(null);
  const socketRef = useRef(null);
  const reconnectRef = useRef(null);
  const imageRef = useRef(null);

  const [activeCamera, setActiveCamera] = useState('USB');
  const [showInfoFor, setShowInfoFor] = useState(null);

  const wsUrl = activeCamera === 'CSI'
    ? 'ws://localhost:8765'
    : 'ws://localhost:8770';

  useEffect(() => {
    const connectSocket = () => {
      const socket = new WebSocket(wsUrl);
      socketRef.current = socket;

      socket.onopen = () => clearInterval(reconnectRef.current);
      socket.onmessage = (event) => {
        if (event.data && event.data.length > 100 && imageRef.current) {
          imageRef.current.src = `data:image/jpeg;base64,${event.data}`;
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
  }, [wsUrl]);

  const toggleFullscreen = () => {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else {
      containerRef.current?.requestFullscreen();
    }
  };

  const handleCameraChange = (camera) => {
    imageRef.current && (imageRef.current.src = '');
    setActiveCamera(camera);
    setShowInfoFor(null);
  };

  return (
    <div className="video-feed" ref={containerRef}>
      <div className="camera-toggle-buttons">
        {['CSI','USB'].map(cam => (
          <button
            key={cam}
            className={activeCamera === cam ? 'active' : ''}
            onClick={() => handleCameraChange(cam)}
          >
            {cam} Camera
          </button>
        ))}
      </div>

     

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
