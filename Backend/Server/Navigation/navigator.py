import asyncio
import math
import os
import json
import time
from car import Car
from perception import check_for_obstacle
from slam_interface import get_current_pose
from control_server import set_servo_angle
from utils import angle_between_points
import os

class Navigator:
    def __init__(
        self,
        visited_file="visited_resume.json",
        autosave_interval=100
    ):
        self.car            = Car()
        self.current_pose   = (0.0, 0.0)
        self.heading        = 0.0   # degrees
        self.visited        = set()
        self.visited_file   = visited_file
        self.autosave_interval = autosave_interval
        self._last_saved_count = 0

        # If there’s an existing resume file, load it
        if os.path.exists(self.visited_file):
            self.load_visited()

        # Control whether the robot is in navigation mode
        self.navigation_mode_enabled = os.getenv("ENABLE_NAVIGATION", "0") == "1"
        self.scan_enabled = os.getenv("ENABLE_SCAN", "0") == "1"

    def load_visited(self):
        with open(self.visited_file, "r") as f:
            data = json.load(f)
        self.visited = set((x, y) for x, y in data)
        self._last_saved_count = len(self.visited)
        print(f"[NAV] Loaded {len(self.visited)} visited positions from {self.visited_file}")

    def save_visited(self):
        data = list(self.visited)
        with open(self.visited_file, "w") as f:
            json.dump(data, f)
        print(f"[NAV] Saved {len(self.visited)} visited positions to {self.visited_file}")

    def update_pose(self):
        self.current_pose = get_current_pose()
        key = (round(self.current_pose[0], 1), round(self.current_pose[1], 1))
        self.visited.add(key)

    def predict_pose_ahead(self, dist):
        rad = math.radians(self.heading)
        dx = math.cos(rad) * dist
        dy = math.sin(rad) * dist
        return (self.current_pose[0] + dx, self.current_pose[1] + dy)

    def has_visited(self, pose):
        key = (round(pose[0], 1), round(pose[1], 1))
        return key in self.visited

    async def rotate_randomly(self):
        if not self.navigation_mode_enabled:
            return
        turn_degrees = 90
        direction = 1 if int(self.heading) % 2 == 0 else -1
        steps = turn_degrees // 5
        for _ in range(steps):
            speed = 400 * direction
            self.car.motor.set_motor_model(-speed, -speed, speed, speed)
            await asyncio.sleep(0.05)
            self.heading = (self.heading + 5 * direction) % 360
        self.car.motor.set_motor_model(0, 0, 0, 0)
        await asyncio.sleep(0.2)

    async def move_forward(self, duration=0.7, speed=600):
        if not self.navigation_mode_enabled:
            return
        self.car.motor.set_motor_model(speed, speed, speed, speed)
        await asyncio.sleep(duration)
        self.car.motor.set_motor_model(0, 0, 0, 0)
        self.update_pose()

    async def perform_pan_tilt_scan(self):
        if not self.scan_enabled:
            return
        for tilt in [0, 30]:
            set_servo_angle("tilt", tilt)
            await asyncio.sleep(0.3)
            for pan in range(-90, 91, 30):
                set_servo_angle("pan", pan)
                await asyncio.sleep(0.2)
        set_servo_angle("pan", 0)
        set_servo_angle("tilt", 0)
        await asyncio.sleep(0.1)

    async def follow_path(self, path):
        if not self.navigation_mode_enabled:
            print("[NAV] Navigation mode disabled — skipping path following.")
            return

        for target in path:
            self.update_pose()

            if self.has_visited(target):
                continue

            target_angle = angle_between_points(self.current_pose, target)
            angle_diff = (target_angle - self.heading + 360) % 360
            if angle_diff > 180:
                direction = -1
                angle_diff = 360 - angle_diff
            else:
                direction = 1

            steps = int(angle_diff // 5)
            for _ in range(steps):
                speed = 400 * direction
                self.car.motor.set_motor_model(-speed, -speed, speed, speed)
                await asyncio.sleep(0.05)
                self.heading = (self.heading + 5 * direction) % 360

            self.car.motor.set_motor_model(0, 0, 0, 0)
            await asyncio.sleep(0.1)

            await self.move_forward()

    async def _explore_step(self, scan):
        if not self.navigation_mode_enabled:
            return False

        self.update_pose()

        if check_for_obstacle():
            await self.rotate_randomly()
            return False

        if scan and self.scan_enabled:
            await self.perform_pan_tilt_scan()

        next_pose = self.predict_pose_ahead(0.2)
        if self.has_visited(next_pose):
            await self.rotate_randomly()
            return False
        else:
            await self.move_forward()
            return True

    async def explore_full(
        self,
        scan=True,
        max_idle_cycles=30,
        cycle_delay=0.2,
        on_chunk=None
    ):
        if not self.navigation_mode_enabled:
            print("[NAV] Navigation mode disabled — skipping exploration.")
            return

        print("[NAV] Starting exploration with chunked autosave...")
        self.update_pose()
        last_count = len(self.visited)
        idle = 0

        while True:
            moved = await self._explore_step(scan)
            curr_count = len(self.visited)

            if curr_count > last_count:
                last_count = curr_count
                idle = 0
                print(f"[NAV] New visited ≈ {curr_count}")

                if curr_count - self._last_saved_count >= self.autosave_interval:
                    self.save_visited()
                    if on_chunk:
                        await on_chunk()
                    self._last_saved_count = curr_count

            else:
                idle += 1

            if idle >= max_idle_cycles:
                print("[NAV] Exploration idle threshold reached—complete.")
                break

            await asyncio.sleep(cycle_delay)

        self.save_visited()
        if on_chunk:
            await on_chunk()
        print(f"[NAV] Exploration finished, visited ≈ {len(self.visited)} positions.")
