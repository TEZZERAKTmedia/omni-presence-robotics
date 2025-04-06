// Frontend/src/sawyerApi.js
let socket;

export const connectWebSocket = (url = 'ws://localhost:8001') => {
  socket = new WebSocket(url);

  socket.onopen = () => {
    console.log('[WebSocket] Connected to backend');
  };

  socket.onmessage = (event) => {
    console.log('[WebSocket] Message from server:', event.data);
  };

  socket.onerror = (err) => {
    console.error('[WebSocket] Error:', err);
  };

  socket.onclose = () => {
    console.warn('[WebSocket] Connection closed');
  };
};

export const sendCommand = (data) => {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(data));
  } else {
    console.warn('[WebSocket] Cannot send, socket not open');
  }
};
