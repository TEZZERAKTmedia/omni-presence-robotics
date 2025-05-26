# autonomy_server.py
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from slam_interface import SlamManager, PoseListener, try_build_orbslam
from control_server import ControlServer
from navigator import Navigator
from cost_map_builder import build_cost_map
from frontier_finder import find_frontiers
from path_planner import a_star


def choose_best_frontier(frontiers, current_pose):
    def dist(a, b):
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
    return min(frontiers, key=lambda f: dist(current_pose, f))


class AutonomyServer:
    def __init__(self):
        self.map_file = "resume_map.env"
        self.visited_file = "visited_resume.json"
        self.visited = []

        self.slam_manager = SlamManager()
        self.pose_listener = PoseListener()
        self.control_server = ControlServer(self)
        self.navigator = Navigator(visited_file=self.visited_file)

        self.running = False

    async def start(self):
        # ✅ Try building ORB-SLAM before starting it
        if not await try_build_orbslam():
            print("[ERROR] SLAM binary could not be built.")
            await self.control_server.broadcast(json.dumps({
                "type": "slam_boot_error",
                "message": "SLAM binary build failed. Check robot hardware or build.sh."
            }))
            return  # ⛔ Abort early if build failed

        # ✅ Start SLAM
        await self.slam_manager.start_slam()

        if os.path.exists(self.map_file):
            self.slam_manager.load_map(self.map_file)
            print(f"[SERVER] Loaded previous SLAM map from {self.map_file}")

        await self.pose_listener.connect()
        await self.control_server.start()

        self.running = True
        await self.run_exploration_mode()
        await self.shutdown()

    async def run_exploration_mode(self):
        print("[EXPLORATION] Starting mapping process...")

        async def _save_map_chunk():
            self.slam_manager.save_map(self.map_file)
            print(f"[SERVER] Autosaved SLAM map to {self.map_file}")
            await self.control_server.broadcast(json.dumps({
                "type": "autosave",
                "map_file": self.map_file
            }))

        while self.running:
            pose = await self.pose_listener.get_pose()
            if pose:
                self.visited.append(pose)

                cost_map = build_cost_map(
                    self.pose_listener.landmarks,
                    visited=self.visited
                )

                frontiers = find_frontiers(cost_map)
                if not frontiers:
                    print("[EXPLORATION] No frontiers left.")
                    break

                goal = choose_best_frontier(frontiers, pose)
                path = a_star(cost_map, pose, goal)

                if path:
                    print(f"[NAV] Navigating to frontier at {goal}")
                    await self.navigator.follow_path(path)
                    await asyncio.sleep(0.2)
                    await _save_map_chunk()
                else:
                    print(f"[NAV] No path to frontier at {goal}, skipping...")

        self.slam_manager.save_map(self.map_file)
        print("[EXPLORATION] Final SLAM map saved.")
        await self.control_server.broadcast(json.dumps({
            "type": "exploration_complete",
            "map_file": self.map_file
        }))

    async def shutdown(self):
        print("[SERVER] Shutting down…")
        await self.control_server.stop()
        await self.pose_listener.disconnect()
        await self.slam_manager.stop_slam()
        self.running = False


if __name__ == "__main__":
    server = AutonomyServer()
    asyncio.run(server.start())
