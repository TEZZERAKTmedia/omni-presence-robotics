import asyncio
import websockets
import numpy as np
import cv2
import base64

from usb_camera import USBCamera

usb_camera = USBCamera()

async def usb_stream_handler(websocket, path=None):
    print("[USB STREAM] Client connected")
    try:
        while True:
            frame = usb_camera.capture_frame()
            if frame is not None:
                # Encode JPEG
                success, jpeg = cv2.imencode('.jpg', frame)
                if success:
                    b64_jpeg = base64.b64encode(jpeg).decode('utf-8')
                    await websocket.send(b64_jpeg)
                    print("[USB STREAM] Sent frame")
                else:
                    print("[USB STREAM] JPEG encoding failed")
            else:
                print("[USB STREAM] No frame captured")
            await asyncio.sleep(0.03)
    except websockets.exceptions.ConnectionClosed:
        print("[USB STREAM] Client disconnected")
    except Exception as e:
        print(f"[ERROR USB STREAM] {e}")

async def main():
    async with websockets.serve(usb_stream_handler, "0.0.0.0", 8770, max_size=2**23):
        print("[USB STREAM] WebSocket server started on ws://0.0.0.0:8770")
        await asyncio.Future()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        usb_camera.release()
        print("[SHUTDOWN] USB camera server stopped.")
