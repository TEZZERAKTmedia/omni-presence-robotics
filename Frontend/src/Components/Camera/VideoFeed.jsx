import React, { useEffect, useState, useRef } from 'react';
import './Video.css';

const VideoFeed = () => {
  const [imageSrc, setImageSrc] = useState('');
  const containerRef = useRef(null);

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8765'); // Update IP
    socket.onmessage = (event) => {
      setImageSrc(`data:image/jpeg;base64,${event.data}`);
    };
    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
    return () => socket.close();
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
      <img src={imageSrc} alt="Live Feed" />
    </div>
  );
};

export default VideoFeed;
