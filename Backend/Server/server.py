import socket
import fcntl
import struct
import asyncio
import threading
import json

from infrared import Infrared
from tcp_server import TCPServer
import websocket_server
from joystick_motor_controller import drive_from_joystick as drive_mecanum_joystick
from joystick_terrain import drive_from_terrain_joystick
from cat_toy_servo import control_cat_toy
from joystick_motor_controller import check_idle_and_stop
from camera_servo_controller import control_camera_servo

infrared = Infrared()

class Server:
    def __init__(self):
        selfgit.ip_address = self.get_interface_ip()
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
        except Exception:
            return "127.0.0.1"

    def start_tcp_servers(self, command_port=5000, video_port=8000, max_clients=1, listen_count=1):
        try:
            self.command_server.start(self.ip_address, command_port, max_clients, listen_count)
            self.video_server.start(self.ip_address, video_port, max_clients, listen_count)
        except Exception:
            pass

    def stop_tcp_servers(self):
        try:
            self.command_server.close()
            self.video_server.close()
        except Exception:
            pass

    def send_data_to_command_client(self, data: bytes, ip_address: str = None):
        self.command_server_is_busy = True
        try:
            if ip_address:
                self.command_server.send_to_client(ip_address, data)
            else:
                self.command_server.send_to_all_client(data)
        except Exception:
            pass
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

if __name__ == '__main__':
    server = Server()
    server.start_tcp_servers(5003, 8003)

    ws_thread = threading.Thread(
        target=lambda: asyncio.run(websocket_server.start_ws_server(server.read_data_from_command_server())),
        daemon=True
    )
    ws_thread.start()

    try:
        while True:
            cmd_queue = server.read_data_from_command_server()
            if cmd_queue.qsize() > 0:
                client_address, message = cmd_queue.get()
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
                            if (fl > 0 or fr > 0 or bl > 0 or br > 0) and infrared.read_all_infrared() != 0:
                                fl = fr = bl = br = 0
                            drive_mecanum_joystick(fl, fr, bl, br)

                        elif msg_type == "terrain":
                            fl = payload.get("frontLeft", 0)
                            fr = payload.get("frontRight", 0)
                            bl = payload.get("backLeft", 0)
                            br = payload.get("backRight", 0)
                            drive_from_terrain_joystick(fl, fr, bl, br)

                        elif msg_type == "camera-servo":
                            control_camera_servo(payload.get("pan", 0), payload.get("tilt", 0))

                        elif msg_type == "cat-toy":
                            control_cat_toy(payload.get("direction", "stop"), payload.get("speed", 1))

                    except json.JSONDecodeError:
                        pass
                    except Exception:
                        pass
                else:
                    server.send_data_to_command_client(message, client_address)

            video_queue = server.read_data_from_video_server()
            if video_queue.qsize() > 0:
                client_address, message = video_queue.get()
                server.send_data_to_video_client(message, client_address)

    except KeyboardInterrupt:
        server.stop_tcp_servers()