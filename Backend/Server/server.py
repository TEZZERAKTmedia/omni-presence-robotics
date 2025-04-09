import socket
import fcntl
import struct
import asyncio
import threading
import json
import websockets
from infrared import Infrared 
from tcp_server import TCPServer
import websocket_server
from joystick_motor_controller import drive_from_joystick
from camera_servo_controller import control_camera_servo
from camera import Camera
from camera_streamer import CameraStreamer

# Initialize camera and start persistent frame capture
global_camera = Camera()
streamer = CameraStreamer(global_camera)
streamer.start()
infrared = Infrared()

# ----------------------------
# Robust WebSocket stream handler
# ----------------------------
async def stream_handler(*args, **kwargs):
    # Handle argument unpacking from websockets.serve
    if len(args) >= 2:
        websocket, path = args[0], args[1]
    elif len(args) == 1:
        websocket = args[0]
        path = None
        print("⚠️ Warning: No path provided in handler arguments")
    else:
        raise TypeError("stream_handler() requires at least 1 argument")

    print("📡 Video client connected; path:", path)

    try:
        while True:
            frame = streamer.get_frame()
            if frame:
                await websocket.send(frame)
            await asyncio.sleep(0.05)  # Stream ~20 FPS
    except websockets.exceptions.ConnectionClosed:
        print("❌ Video client disconnected")
    except Exception as e:
        print(f"🚨 Video stream error: {e}")


# ----------------------------
# Video WebSocket server
# ----------------------------
async def start_video_ws_server():
    print("📺 Starting WebSocket video stream on port 8765")
    async with websockets.serve(stream_handler, "0.0.0.0", 8765):
        await asyncio.Future()  # Keep the server running


# ----------------------------
# Run video WebSocket in a separate thread
# ----------------------------
def run_video_server_in_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_video_ws_server())
    loop.run_forever()


# ----------------------------
# TCP Server Wrapper
# ----------------------------
class Server:
    def __init__(self):
        self.ip_address = self.get_interface_ip()
        self.command_server = TCPServer()
        self.video_server = TCPServer()
        self.command_server_is_busy = False
        self.video_server_is_busy = False

    def get_interface_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ip = socket.inet_ntoa(
                fcntl.ioctl(
                    s.fileno(),
                    0x8915,
                    struct.pack('256s', b'wlan0'[:15])
                )[20:24]
            )
            return ip
        except Exception as e:
            print(f"[ERROR] Could not get IP address: {e}")
            return "127.0.0.1"

    def start_tcp_servers(self, command_port=5000, video_port=8000, max_clients=1, listen_count=1):
        try:
            self.command_server.start(self.ip_address, command_port, max_clients, listen_count)
            self.video_server.start(self.ip_address, video_port, max_clients, listen_count)
        except Exception as e:
            print(f"[ERROR] Starting TCP servers: {e}")

    def stop_tcp_servers(self):
        try:
            self.command_server.close()
            self.video_server.close()
        except Exception as e:
            print(f"[ERROR] Stopping TCP servers: {e}")

    def send_data_to_command_client(self, data: bytes, ip_address: str = None):
        self.command_server_is_busy = True
        try:
            if ip_address:
                self.command_server.send_to_client(ip_address, data)
            else:
                self.command_server.send_to_all_client(data)
        except Exception as e:
            print(f"[ERROR] Sending to command client: {e}")
        finally:
            self.command_server_is_busy = False

    def send_data_to_video_client(self, data: bytes, ip_address: str = None):
        self.video_server_is_busy = True
        try:
            if ip_address:
                self.video_server.send_to_client(ip_address, data)
            else:
                self.video_server.send_to_all_client(data)
        finally:
            self.video_server_is_busy = False

    def read_data_from_command_server(self):
        return self.command_server.message_queue

    def read_data_from_video_server(self):
        return self.video_server.message_queue


# ----------------------------
# Main Server Loop
# ----------------------------
if __name__ == '__main__':
    print("[SERVER] Starting...")
    server = Server()
    server.start_tcp_servers(5003, 8003)

    # 🎮 Command WebSocket server (port 8001)
    ws_thread = threading.Thread(
        target=lambda: asyncio.run(websocket_server.start_ws_server(server.read_data_from_command_server())),
        daemon=True
    )
    ws_thread.start()

    # 📹 Video WebSocket stream server (port 8765)
    video_ws_thread = threading.Thread(
        target=run_video_server_in_thread,
        daemon=True
    )
    video_ws_thread.start()

    try:
        while True:
            cmd_queue = server.read_data_from_command_server()
            if cmd_queue.qsize() > 0:
                client_address, message = cmd_queue.get()
                print(f"[INCOMING] {client_address}: {message}")

                if client_address == "websocket_ui":
                    try:
                        data = json.loads(message)
                        payload = data.get("payload", {})
                        msg_type = data.get("type")
                        if msg_type == "joystick":
                                steer = payload.get("servo0", 0)
                                throttle = payload.get("servo1", 0)

                                if throttle > 0 and infrared.read_all_infrared() != 0:
                                    print("[INFRARED] Obstacle detected. Blocking forward movement.")
                                    throttle = 0

                                print(f"[JOYSTICK] steer={steer}, throttle={throttle}")
                                drive_from_joystick(steer, throttle)

                        elif msg_type == "camera-servo":
                            print(f"[CAMERA JOYSTICK] pan={payload.get('pan')} tilt={payload.get('tilt')}")
                            control_camera_servo(payload.get("pan", 0), payload.get("tilt", 0))
                        else:
                            print(f"[WARN] Unhandled message type: {msg_type}")

                    except json.JSONDecodeError:
                        print("[ERROR] Invalid JSON from WebSocket:", message)
                    except Exception as e:
                        print("[ERROR] Failed to handle input:", e)
                else:
                    server.send_data_to_command_client(message, client_address)

            video_queue = server.read_data_from_video_server()
            if video_queue.qsize() > 0:
                client_address, message = video_queue.get()
                print(f"[VIDEO] {client_address}: {message}")
                server.send_data_to_video_client(message, client_address)

    except KeyboardInterrupt:
        print("[SHUTDOWN] Stopping server...")
        server.stop_tcp_servers()
