# joystick_motor_controller.py

from motor import Ordinary_Car
import time

# Initialize the car
car = Ordinary_Car()

# Constants
DEAD_ZONE = 0.1
MIN_THRESHOLD = 400
MAX_PWM = 1200
UPDATE_RESOLUTION = 0.01  # Joystick granularity filter

# Keep track of last time a command was sent
last_command_time = time.time()


def apply_minimum_threshold(value, threshold=MIN_THRESHOLD):
    if value == 0:
        return 0
    elif value > 0:
        return max(value, threshold)
    else:
        return min(value, -threshold)


def drive_from_joystick(servo0: float, servo1: float):
    """
    Accepts joystick input between -1.0 and 1.0 for x (servo0) and y (servo1),
    and converts it to motor commands using differential drive logic.
    """
    global last_command_time

    # Round inputs for performance and stability
    servo0 = round(servo0, 2)
    servo1 = round(servo1, 2)

    # Apply dead zone
    if abs(servo0) < DEAD_ZONE:
        servo0 = 0
    if abs(servo1) < DEAD_ZONE:
        servo1 = 0

    # Exit early if no significant input
    if servo0 == 0 and servo1 == 0:
        stop()
        return

    # Differential drive calculation
    x = servo0
    y = servo1

    left_speed = int((y + x) * MAX_PWM)
    right_speed = int((y - x) * MAX_PWM)

    # Apply clamping
    left_speed = max(min(left_speed, MAX_PWM), -MAX_PWM)
    right_speed = max(min(right_speed, MAX_PWM), -MAX_PWM)

    # Apply minimum thresholds to avoid buzzing
    left_speed = apply_minimum_threshold(left_speed)
    right_speed = apply_minimum_threshold(right_speed)

    print(f"[JOYSTICK DRIVE] Left: {left_speed}, Right: {right_speed}")
    car.set_motor_model(left_speed, left_speed, right_speed, right_speed)
    last_command_time = time.time()


def stop():
    """Stop all motors safely."""
    print("[STOP] Motors stopping...")
    car.set_motor_model(0, 0, 0, 0)


def check_idle_and_stop():
    """If no input has been received in a while, stop the motors."""
    if time.time() - last_command_time > 0.5:
        stop()
