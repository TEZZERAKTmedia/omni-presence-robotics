import asyncio
import websockets
import json
import os
import signal
import subprocess


# --- Path helpers ---
def base_path(*parts):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", *parts))

def get_slam_binary_path():
    return base_path("ORB_SLAM3", "Examples", "Stereo", "stereo_tum")

def binary_exists():
    return os.path.isfile(get_slam_binary_path())

async def try_build_orbslam():
    print("[SLAM] Checking for SLAM binary...")

    if binary_exists():
        print("[SLAM] SLAM binary found ✅")
        return True

    print("[SLAM] SLAM binary missing — attempting build... 🔧")

    orbslam_dir = base_path("ORB_SLAM3")
    build_script = os.path.join(orbslam_dir, "build.sh")

    try:
        subprocess.run(
            ["bash", build_script],
            cwd=orbslam_dir,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        print("[SLAM ERROR] Build script failed:\n", e.stderr.decode())
        return False

    if binary_exists():
        print("[SLAM] Build successful! 🎉")
        return True
    else:
        print("[SLAM] Build failed — binary still missing ❌")
        return False


# --- PoseListener class ---
class PoseListener:
    def __init__(self, uri="ws://localhost:8780"):
        self.uri = uri
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
                    await self.pose_queue.put((
                        data["pose"]["x"],
                        data["pose"]["y"],
                        data["pose"]["heading"]
                    ))
                if "landmarks" in data:
                    self.landmarks = data["landmarks"]
            except json.JSONDecodeError:
                continue

    async def get_pose(self):
        if not self.pose_queue.empty():
            return await self.pose_queue.get()
        return None

    async def disconnect(self):
        if hasattr(self, 'conn'):
            await self.conn.close()


# --- Global pose listener instance ---
pose_listener = PoseListener()

async def get_current_pose():
    return await pose_listener.get_pose()


# --- SLAM Manager ---
class SlamManager:
    def __init__(self):
        self.proc = None
        self.orbslam_dir = base_path("ORB_SLAM3")
        self.env_dir = os.path.join(self.orbslam_dir, "environments", "default")

    async def start_slam(self):
        if not os.path.exists(self.env_dir):
            os.makedirs(self.env_dir)

        self.proc = await asyncio.create_subprocess_exec(
            "./Examples/Stereo/stereo_tum",
            "Vocabulary/ORBvoc.txt",
            "Examples/Stereo/TUM1_stereo.yaml",
            "dataset/left",
            "dataset/right",
            cwd=self.orbslam_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            preexec_fn=os.setsid
        )
        await asyncio.sleep(2)

    async def stop_slam(self):
        if self.proc:
            os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
            await asyncio.sleep(1)

    def save_map(self, path):
        print(f"[SLAM] (mock) Saving map to {path}...")

    def load_map(self, path):
        print(f"[SLAM] (mock) Loading map from {path}...")
