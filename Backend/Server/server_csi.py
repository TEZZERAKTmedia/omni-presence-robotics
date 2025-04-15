import asyncio
import websockets
from camera import Camera
from camera_streamer import CameraStreamer

pi_camera = Camera()
streamer = CameraStreamer(pi_camera, fps=20)
streamer.start()

async def csi_stream_handler(websocket, path=None):
    print("📡 CSI Camera client connected")
    try:
        while True:
            frame = streamer.get_frame()
            if frame:
                await websocket.send(frame)
            await asyncio.sleep(0.05)
    except websockets.exceptions.ConnectionClosed:
        print("❌ CSI Camera client disconnected")
    except Exception as e:
        print(f"[ERROR CSI] {e}")

async def main():
    print("📺 CSI Camera WebSocket server running on port 8765")
    async with websockets.serve(csi_stream_handler, "0.0.0.0", 8765):
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
