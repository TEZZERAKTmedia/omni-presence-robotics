import React, { useState, useEffect, useRef } from "react";

const WS_URL = "ws://YOUR_BACKEND_IP:8790"; // <-- Update this with your Pi or server IP

export default function MappingAutomationPage() {
  const [ws, setWs] = useState(null);
  const [mapping, setMapping] = useState(false);
  const [landmarks, setLandmarks] = useState([]);
  const canvasRef = useRef(null);

  useEffect(() => {
    const socket = new WebSocket(WS_URL);
    socket.onopen = () => console.log("[WS] Connected");
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "landmarks_update") {
        setLandmarks(data.payload.landmarks);
      }
    };
    socket.onclose = () => console.log("[WS] Disconnected");
    setWs(socket);

    return () => socket.close();
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = "black";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = "lime";
    landmarks.forEach(([x, y]) => {
      const drawX = (x * 5) + canvas.width / 2;
      const drawY = (y * 5) + canvas.height / 2;
      ctx.fillRect(drawX, drawY, 2, 2);
    });
  }, [landmarks]);

  const sendMappingControl = (action) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: "mapping_control",
        payload: { action }
      }));

      if (action === "start") setMapping(true);
      if (action === "stop") setMapping(false);
      if (action === "pause") setMapping(false);
    }
  };

  return (
    <div className="flex flex-col items-center p-4">
      <h1 className="text-2xl font-bold mb-4">Mapping Automation Mode</h1>

      <div className="flex gap-4 mb-4">
        <button
          className="px-4 py-2 bg-green-500 text-white rounded"
          onClick={() => sendMappingControl("start")}
          disabled={mapping}
        >
          Start Scan
        </button>
        <button
          className="px-4 py-2 bg-yellow-400 text-black rounded"
          onClick={() => sendMappingControl("pause")}
          disabled={!mapping}
        >
          Pause Scan
        </button>
        <button
          className="px-4 py-2 bg-red-500 text-white rounded"
          onClick={() => sendMappingControl("stop")}
          disabled={!mapping}
        >
          Stop Scan
        </button>
      </div>

      <div className="relative">
        <canvas
          ref={canvasRef}
          width={400}
          height={400}
          className="border border-gray-300 rounded"
        />
        {mapping && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <span className="text-white text-lg">Scanning in Progress...</span>
          </div>
        )}
      </div>
    </div>
  );
}
