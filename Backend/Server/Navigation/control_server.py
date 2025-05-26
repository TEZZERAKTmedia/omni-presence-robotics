import asyncio
import websockets
import json
from servo import Servo  # ✅ make sure this import path is correct

# Initialize servo controller instance
servo_controller = Servo()

def set_servo_angle(channel: str, angle: int):
    """
    Allows external modules like navigator.py to control the servo.
    """
    try:
        servo_controller.set_servo_pwm(channel, angle)
        print(f"[CTRL] Set servo {channel} to angle {angle}")
    except Exception as e:
        print(f"[CTRL ERROR] Failed to set servo angle: {e}")


class ControlServer:
    def __init__(self, autonomy_server):
        self.autonomy_server = autonomy_server
        self.clients = set()
        self.autonomy_enabled = False
        self.goal = None

    async def start(self):
        self.server = await websockets.serve(self._handler, "0.0.0.0", 8790)

    async def broadcast(self, message):
        if self.clients:
            await asyncio.gather(*[client.send(message) for client in self.clients])

    async def _handler(self, websocket, path):
        print("[CTRL] Client connected")
        self.clients.add(websocket)
        try:
            async for message in websocket:
                data = json.loads(message)
                if data.get("type") == "autonomy":
                    self.autonomy_enabled = bool(data["payload"]["enabled"])
                    print(f"[CTRL] Autonomy set to {self.autonomy_enabled}")
                if data.get("type") == "goal":
                    self.goal = tuple(data["payload"]["goal"])
                    print(f"[CTRL] New goal set: {self.goal}")
                if data.get("type") == "mapping_control":
                    action = data["payload"]["action"]
                    print(f"[CTRL] Mapping control received: {action}")
                    if action == "start":
                        await self.autonomy_server.slam_manager.start_slam()
                    elif action == "pause" or action == "stop":
                        await self.autonomy_server.slam_manager.stop_slam()
        except Exception as e:
            print(f"[CTRL ERROR] {e}")
        finally:
            self.clients.remove(websocket)
