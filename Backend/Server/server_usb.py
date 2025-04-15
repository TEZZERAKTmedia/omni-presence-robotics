import asyncio
import websockets
from usb_camera import USBCamera
from camera_streamer import CameraStreamer

usb_camera = USBCamera()
streamer = CameraStreamer(usb_camera, fps=20)
streamer.start()

async def usb_stream_handler(websocket, path=None):
    print("📡 USB Camera client connected")
    try:
        while True:
            frame = streamer.get_frame()
            if frame:
                await websocket.send(frame)
            await asyncio.sleep(0.05)
    except websockets.exceptions.ConnectionClosed:
        print("❌ USB Camera client disconnected")
    except Exception as e:
        print(f"[ERROR USB] {e}")

async def main():
    print("📺 USB Camera WebSocket server running on port 8770")
    async with websockets.serve(usb_stream_handler, "0.0.0.0", 8770):
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
