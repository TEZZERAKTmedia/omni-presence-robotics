import asyncio
import websockets
import numpy as np
import cv2
import base64

from usb_camera import USBCamera
from camera_streamer import CameraStreamer

# Initialize camera and streaming engine
usb_camera = USBCamera()
streamer = CameraStreamer(usb_camera, fps=20)
streamer.start()

# Async stream handler for each WebSocket client
async def usb_stream_handler(websocket, path=None):
    try:
        while True:
            frame_bytes = streamer.get_frame()
            if frame_bytes:
                # Convert raw RGB bytes to an image array
                frame = np.frombuffer(frame_bytes, dtype=np.uint8).reshape((usb_camera.height, usb_camera.width, 3))
                # Convert to JPEG
                success, jpeg = cv2.imencode('.jpg', frame)
                if success:
                    # Encode as base64 and send to frontend
                    b64_jpeg = base64.b64encode(jpeg).decode('utf-8')
                    await websocket.send(b64_jpeg)
            await asyncio.sleep(0.05)
    except websockets.exceptions.ConnectionClosed:
        pass  # Client disconnected
    except Exception as e:
        print(f"[ERROR USB STREAM] {e}")

# Start the WebSocket server on port 8770
async def main():
    async with websockets.serve(usb_stream_handler, "0.0.0.0", 8770):
        await asyncio.Future()  # Keep server alive

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[SHUTDOWN] USB camera server stopped.")
