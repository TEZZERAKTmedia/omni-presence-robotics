# navigator.py
import asyncio
import math
from car import Car
from utils import distance, angle_between_points

class Navigator:
    def __init__(self):
        self.car = Car()
        self.current_pose = (0, 0)  # x, y
        self.heading = 0            # degrees (0° = facing right)

    def update_pose(self, pose):
        self.current_pose = pose

    async def rotate_to_target(self, target):
        # Calculate the angle to target
        target_angle = angle_between_points(self.current_pose, target)
        angle_diff = (target_angle - self.heading + 360) % 360
        print(f"[NAV] Rotating: Current Heading {self.heading:.1f}°, Target {target_angle:.1f}°, Diff {angle_diff:.1f}°")

        # Simple logic: Rotate Left or Right based on shortest path
        if angle_diff > 180:
            # Rotate Left
            while angle_diff > 10:
                self.car.motor.set_motor_model(-500, -500, 500, 500)
                await asyncio.sleep(0.05)
                self.heading = (self.heading - 5) % 360
                angle_diff = (target_angle - self.heading + 360) % 360
        else:
            # Rotate Right
            while angle_diff > 10:
                self.car.motor.set_motor_model(500, 500, -500, -500)
                await asyncio.sleep(0.05)
                self.heading = (self.heading + 5) % 360
                angle_diff = (target_angle - self.heading + 360) % 360

        self.car.motor.set_motor_model(0, 0, 0, 0)
        await asyncio.sleep(0.2)

    async def drive_straight(self, target):
        print(f"[NAV] Driving toward {target}")
        while distance(self.current_pose, target) > 5:  # 5 units (cells) tolerance
            self.car.motor.set_motor_model(600, 600, 600, 600)
            await asyncio.sleep(0.2)
            # Assume during each move we update pose externally
        self.car.motor.set_motor_model(0, 0, 0, 0)

    async def follow_path(self, path):
        for target in path:
            await self.rotate_to_target(target)
            await self.drive_straight(target)
            print(f"[NAV] Reached waypoint {target}")
            await asyncio.sleep(0.2)
        print("[NAV] Path completed!")
        self.car.motor.set_motor_model(0, 0, 0, 0)
