import asyncio
import websockets
import numpy as np
import cv2
import base64

from usb_camera import USBCamera

usb_camera = USBCamera()

async def usb_stream_handler(websocket, path=None):
    try:
        print("[USB STREAM] Client connected")
        while True:
            frame = usb_camera.capture_frame()
            if frame is not None:
                success, jpeg = cv2.imencode('.jpg', frame)
                if success:
                    b64_jpeg = base64.b64encode(jpeg).decode('utf-8')
                    await websocket.send(b64_jpeg)
            await asyncio.sleep(0.05)
    except websockets.exceptions.ConnectionClosed:
        print("[USB STREAM] Client disconnected")
    except Exception as e:
        print(f"[ERROR USB STREAM] {e}")

async def main():
    async with websockets.serve(usb_stream_handler, "0.0.0.0", 8770):
        await asyncio.Future()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        usb_camera.release()
        print("[SHUTDOWN] USB camera server stopped.")
