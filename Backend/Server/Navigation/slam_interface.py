# slam_interface.py
import asyncio
import websockets
import json
import subprocess
import os
import signal

class SlamManager:
    def __init__(self):
        self.proc = None
        self.env_dir = "External/ORB_SLAM3/environments/default"

    async def start_slam(self):
        if not os.path.exists(self.env_dir):
            os.makedirs(self.env_dir)
        self.proc = subprocess.Popen(
            ["python3", "slam_map_server.py", self.env_dir],
            cwd="External/ORB_SLAM3",
            preexec_fn=os.setsid
        )
        await asyncio.sleep(2)

    async def stop_slam(self):
        if self.proc:
            os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
            await asyncio.sleep(1)

class PoseListener:
    def __init__(self):
        self.uri = "ws://localhost:8780"
        self.pose_queue = asyncio.Queue()
        self.landmarks = []

    async def connect(self):
        self.conn = await websockets.connect(self.uri)
        asyncio.create_task(self._listener())

    async def _listener(self):
        async for msg in self.conn:
            try:
                data = json.loads(msg)
                if "pose" in data:
                    if self.pose_queue.full():
                        _ = self.pose_queue.get_nowait()
                    await self.pose_queue.put((data["pose"]["x"], data["pose"]["y"]))
                if "landmarks" in data:
                    self.landmarks = data["landmarks"]
            except json.JSONDecodeError:
                continue

    async def get_pose(self):
        if not self.pose_queue.empty():
            return await self.pose_queue.get()
        return None

    async def disconnect(self):
        await self.conn.close()
