import asyncio
import websockets
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
            frame = streamer.get_frame()
            if frame:
                await websocket.send(frame)
            await asyncio.sleep(0.05)  # 20 fps cap
    except websockets.exceptions.ConnectionClosed:
        pass  # Silent disconnect
    except Exception:
        pass  # Silent error

# Start the WebSocket server on port 8770
async def main():
    async with websockets.serve(usb_stream_handler, "0.0.0.0", 8770):
        await asyncio.Future()  # Keep server alive

if __name__ == '__main__':
    asyncio.run(main())
