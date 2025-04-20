import React, { useEffect, useState, useRef } from 'react';
import './video.css';

const VideoFeed = () => {
  // State for storing the latest image
  const [imageSrc, setImageSrc] = useState('');
  // Reference to the container element (for fullscreen toggling)
  const containerRef = useRef(null);
  // Reference to the current WebSocket connection
  const socketRef = useRef(null);
  // Reference to a reconnect interval timer
  const reconnectRef = useRef(null);
  // State for the active camera selection ("CSI" or "USB")
  const [activeCamera, setActiveCamera] = useState('USB');

  // Decide the WebSocket URL based on the active camera.
  // For example, use port 8765 for the CSI camera and 8770 for the USB camera.
  const wsUrl = activeCamera === 'CSI' ? 'ws://localhost:8765' : 'ws://localhost:8770';

  useEffect(() => {
    // Function to connect to the WebSocket for video streaming.
    const connectSocket = () => {
      console.log(`Connecting to video stream: ${wsUrl}`);
      const socket = new WebSocket(wsUrl);
      socketRef.current = socket;

      socket.onopen = () => {
        console.log('[WebSocket] Connected to video stream');
        clearInterval(reconnectRef.current);
      };

      // When a message is received, update the image source
      socket.onmessage = (event) => {
        if (event.data && event.data.length > 100) {
          console.log("[WebSocket] Received data:", event.data.slice(0, 50)); // Just to check it's a base64 string

          // Assume event.data is Base64-encoded JPEG data
          setImageSrc(`data:image/jpeg;base64,${event.data}`);
        }
      };

      socket.onerror = (error) => {
        console.error('[WebSocket] Video stream error:', error);
      };

      socket.onclose = () => {
        console.warn('[WebSocket] Video stream disconnected, attempting to reconnect...');
        // Reconnect every 2 seconds if the connection closes
        reconnectRef.current = setInterval(() => {
          if (!socketRef.current || socketRef.current.readyState === WebSocket.CLOSED) {
            connectSocket();
          }
        }, 2000);
      };
    };

    connectSocket();

    // Cleanup on component unmount or when the activeCamera changes
    return () => {
      clearInterval(reconnectRef.current);
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [wsUrl, activeCamera]);

  // Toggle full screen when the container is clicked
  const toggleFullscreen = () => {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else if (containerRef.current) {
      containerRef.current.requestFullscreen();
    }
  };

  // Handle camera selection change from the dropdown
  const handleCameraChange = (event) => {
    // Clear the current image and set the new active camera
    setImageSrc('');
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

      {imageSrc ? (
        <img src={imageSrc} alt="Live Feed" />
      ) : (
        <p style={{ color: '#fff', textAlign: 'center' }}>
          Waiting for video stream...
        </p>
      )}
    </div>
  );
};

export default VideoFeed;
