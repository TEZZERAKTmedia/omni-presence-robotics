import asyncio
import websockets
import base64
from camera import Camera  # Assuming your code is in camera.py

camera = Camera()
camera.start_stream()  # Starts JPEG streaming

async def stream_handler(websocket, path):
    print("📡 Client connected for video stream")
    try:
        while True:
            frame = camera.get_frame()  # Get raw JPEG bytes
            encoded = base64.b64encode(frame).decode('utf-8')
            await websocket.send(encoded)
            await asyncio.sleep(0.05)  # ~20 fps
    except websockets.exceptions.ConnectionClosed:
        print("❌ Client disconnected")
    except Exception as e:
        print("🚨 Stream error:", e)

start_server = websockets.serve(stream_handler, "0.0.0.0", 8765)

print("🚀 WebSocket server started on ws://0.0.0.0:8765")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
