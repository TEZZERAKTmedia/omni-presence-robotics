import React, { useState, useEffect, useRef } from "react";

export default function UploadVideo() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const ws = useRef(null);

  useEffect(() => {
    // Connect WebSocket once on mount
    ws.current = new WebSocket("ws://localhost:5678");

    ws.current.onopen = () => {
      console.log("✅ WebSocket connected");
    };

    ws.current.onmessage = (msg) => {
      const message = JSON.parse(msg.data);
      if (message.type === "object_crops") {
        console.log("📦 Received crop metadata:", message.data);
        setStatus("✅ YOLO training complete. Metadata received.");
        // You could also lift this metadata up to pass to another component
      }
    };

    ws.current.onerror = (err) => {
      console.error("❌ WebSocket error:", err);
    };

    return () => ws.current.close(); // Cleanup on unmount
  }, []);

  const handleChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;

    setStatus("📤 Uploading video...");

    const formData = new FormData();
    formData.append("video", file);

    try {
      const res = await fetch("http://localhost:5001/upload-video", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setStatus("✅ Uploaded: " + data.message);

      // Now send WebSocket message to start training
      ws.current.send(
        JSON.stringify({
          action: "train",
          video_path: data.path // e.g. "temp/myfile.mp4"
        })
      );

      setStatus("⏳ Running YOLO object extraction...");
    } catch (err) {
      console.error(err);
      setStatus("❌ Upload failed");
    }
  };

  return (
    <div className="upload-video">
      <h3>📹 Upload Training Video</h3>
      <input type="file" accept="video/*" onChange={handleChange} />
      <button onClick={handleUpload}>Upload and Train</button>
      <p>{status}</p>
    </div>
  );
}
