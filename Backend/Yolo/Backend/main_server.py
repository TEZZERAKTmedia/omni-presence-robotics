import asyncio
import websockets
import json
from yolo_processor import process_video_and_get_metadata

connected_clients = set()

async def handler(websocket):
    connected_clients.add(websocket)
    print("Client connected")

    try:
        async for message in websocket:
            data = json.loads(message)

            if data.get("action") == "train":
                video_path = data["video_path"]
                print(f"🚀 Running YOLO on: {video_path}")

                metadata = process_video_and_get_metadata(video_path)
                await websocket.send(json.dumps({
                    "type": "object_crops",
                    "data": metadata
                }))
    finally:
        connected_clients.remove(websocket)
        print("Client disconnected")

async def main():
    async with websockets.serve(handler, "0.0.0.0", 5678):
        print("✅ WebSocket YOLO training server running on ws://0.0.0.0:5678")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
