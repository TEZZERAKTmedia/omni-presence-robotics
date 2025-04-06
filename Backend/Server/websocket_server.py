import asyncio
import json
import websockets

# This gets passed in from your main Server instance
shared_queue = None

async def websocket_handler(websocket):
    print("WebSocket client connected.")
    async for message in websocket:
        try:
            data = json.loads(message)
            client_address = websocket.remote_address
            # Pack the data like TCP would have
            shared_queue.put((client_address, message))
        except Exception as e:
            print("WebSocket error:", e)

async def start_ws_server(queue_ref):
    global shared_queue
    shared_queue = queue_ref
    async with websockets.serve(websocket_handler, "0.0.0.0", 8001):
        print("WebSocket server running on port 8001")
        await asyncio.Future()  # keep running
