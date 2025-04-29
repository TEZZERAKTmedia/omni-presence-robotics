# autonomy_server.py
import asyncio
from slam_interface import SlamManager, PoseListener
from control_server import ControlServer
from cost_map_builder import build_cost_map
from path_planner import a_star
from navigator import Navigator

class AutonomyServer:
    def __init__(self):
        self.slam_manager = SlamManager()
        self.pose_listener = PoseListener()
        self.control_server = ControlServer(self)
        self.navigator = Navigator()
        self.cost_map = None
        self.current_goal = None
        self.running = False

    async def start(self):
        await self.slam_manager.start_slam()
        await self.pose_listener.connect()
        await self.control_server.start()

        self.running = True
        await self.navigation_loop()

    async def navigation_loop(self):
        while self.running:
            # Always send live landmarks to all clients
            landmarks_message = json.dumps({
                "type": "landmarks_update",
                "payload": {"landmarks": self.pose_listener.landmarks}
            })
            await self.control_server.broadcast(landmarks_message)

            if self.control_server.autonomy_enabled and self.control_server.goal:
                pose = await self.pose_listener.get_pose()
                goal = self.control_server.goal

                if not self.cost_map:
                    self.cost_map = build_cost_map(self.pose_listener.landmarks)

                if pose and goal:
                    path = a_star(self.cost_map, pose, goal)
                    if path:
                        await self.navigator.follow_path(path)

            await asyncio.sleep(0.5)  # Small delay to prevent spamming too fast


    async def stop(self):
        self.running = False
        await self.slam_manager.stop_slam()
        await self.pose_listener.disconnect()

if __name__ == "__main__":
    server = AutonomyServer()
    asyncio.run(server.start())
