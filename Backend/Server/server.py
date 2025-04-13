import socket
import fcntl
import struct
import asyncio
import threading
import json
import websockets
import time

from infrared import Infrared 
from tcp_server import TCPServer
import websocket_server
from joystick_motor_controller import drive_from_joystick as drive_mecanum_joystick
from joystick_terrain import drive_from_terrain_joystick
from cat_toy_servo import control_cat_toy
from usb_camera import USBCamera
from joystick_motor_controller import check_idle_and_stop
from camera_servo_controller import control_camera_servo
from camera import Camera
from camera_streamer import CameraStreamer

# -----------------------------------------------------------------------------
# Initialize Cameras and Streamers
# -----------------------------------------------------------------------------
# CSI Camera (using the Pi camera via the CSI interface)
pi_camera = Camera()                   
pi_streamer = CameraStreamer(pi_camera, fps=20)

usb_camera = USBCamera()  # ✅ Instantiate the USB camera
usb_streamer = CameraStreamer(usb_camera, fps=20)


# Start both streamers
pi_streamer.start()
usb_streamer.start()

# For backward compatibility, set global_camera and streamer to the CSI camera
global_camera = pi_camera
streamer = pi_streamer

# Initialize Infrared sensor and other flags
infrared = Infrared()
camera_fully_tilted = False

# -----------------------------------------------------------------------------
# WebSocket Stream Handlers for Video
# -----------------------------------------------------------------------------
async def csi_stream_handler(websocket, path=None):
    print("📡 CSI Camera client connected; path:", path)
    try:
        while True:
            frame = streamer.get_frame()
            if frame:
                await websocket.send(frame)
            await asyncio.sleep(0.05)  # ~20 FPS
    except websockets.exceptions.ConnectionClosed:
        print("❌ CSI Camera client disconnected")
    except Exception as e:
        print(f"🚨 CSI stream error: {e}")

async def usb_stream_handler(websocket, path=None):
    print("📡 USB Camera client connected; path:", path)
    try:
        while True:
            frame = usb_streamer.get_frame()
            if frame:
                await websocket.send(frame)
            await asyncio.sleep(0.05)
    except websockets.exceptions.ConnectionClosed:
        print("❌ USB Camera client disconnected")
    except Exception as e:
        print(f"🚨 USB stream error: {e}")

async def start_csi_video_ws_server():
    print("📺 Starting CSI Camera WebSocket stream on port 8765")
    async with websockets.serve(csi_stream_handler, "0.0.0.0", 8765):
        await asyncio.Future()  # Keep running

async def start_usb_video_ws_server():
    print("📺 Starting USB Camera WebSocket stream on port 8770")
    async with websockets.serve(usb_stream_handler, "0.0.0.0", 8770):
        await asyncio.Future()

def run_async_server(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)
    loop.run_forever()

def run_csi_video_server_in_thread():
    t = threading.Thread(target=lambda: run_async_server(start_csi_video_ws_server()), daemon=True)
    t.start()

def run_usb_video_server_in_thread():
    t = threading.Thread(target=lambda: run_async_server(start_usb_video_ws_server()), daemon=True)
    t.start()

# Start the video stream servers in separate threads
run_csi_video_server_in_thread()
run_usb_video_server_in_thread()

# -----------------------------------------------------------------------------
# TCP Server Wrapper for Commands and Video
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# Main Server Loop: Process Incoming Commands
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    print("[SERVER] Starting...")
    server = Server()
    server.start_tcp_servers(5003, 8003)

    # Start the command WebSocket server on port 8001
    ws_thread = threading.Thread(
        target=lambda: asyncio.run(websocket_server.start_ws_server(server.read_data_from_command_server())),
        daemon=True
    )
    ws_thread.start()

    try:
        while True:
            # Check for incoming commands
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
                            fl = payload.get("frontLeft", 0)
                            fr = payload.get("frontRight", 0)
                            bl = payload.get("backLeft", 0)
                            br = payload.get("backRight", 0)
                            # Simple obstacle avoidance based on infrared sensor
                            if (fl > 0 or fr > 0 or bl > 0 or br > 0) and infrared.read_all_infrared() != 0:
                                print("[INFRARED] Obstacle detected. Blocking forward movement.")
                                fl = fr = bl = br = 0
                            print(f"[JOYSTICK] FL={fl}, FR={fr}, BL={bl}, BR={br}")
                            drive_mecanum_joystick(fl, fr, bl, br)

                        elif msg_type == "terrain":
                            fl = payload.get("frontLeft", 0)
                            fr = payload.get("frontRight", 0)
                            bl = payload.get("backLeft", 0)
                            br = payload.get("backRight", 0)
                            print(f"[TERRAIN] FL={fl}, FR={fr}, BL={bl}, BR={br}")
                            drive_from_terrain_joystick(fl, fr, bl, br)

                        elif msg_type == "camera-servo":
                            print(f"[CAMERA JOYSTICK] pan={payload.get('pan')} tilt={payload.get('tilt')}")
                            control_camera_servo(payload.get("pan", 0), payload.get("tilt", 0))

                        elif msg_type == "cat-toy":
                            direction = payload.get("direction", "stop")
                            speed = payload.get("speed", 1)
                            print(f"[CAT TOY] Direction: {direction}, Speed: {speed}")
                            control_cat_toy(direction, speed)

                        else:
                            print(f"[WARN] Unhandled message type: {msg_type}")

                    except json.JSONDecodeError:
                        print("[ERROR] Invalid JSON from WebSocket:", message)
                    except Exception as e:
                        print(f"[ERROR] Failed to handle input: {e}")
                else:
                    server.send_data_to_command_client(message, client_address)

            # Process outgoing video commands
            video_queue = server.read_data_from_video_server()
            if video_queue.qsize() > 0:
                client_address, message = video_queue.get()
                print(f"[VIDEO] {client_address}: {message}")
                server.send_data_to_video_client(message, client_address)

    except KeyboardInterrupt:
        print("[SHUTDOWN] Stopping server...")
        server.stop_tcp_servers()
