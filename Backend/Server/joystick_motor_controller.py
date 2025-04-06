from motor import Ordinary_Car
import time

# Initialize the car
car = Ordinary_Car()

# Constants
DEAD_ZONE = 0.1
MIN_THRESHOLD = 300
MAX_LINEAR_PWM = 1600
MAX_TURN_PWM = 2000
IDLE_TIMEOUT = 0.5

# State
last_command_time = time.time()

def apply_min_threshold(value, threshold=MIN_THRESHOLD):
    if value == 0:
        return 0
    elif value > 0:
        return max(value, threshold)
    else:
        return min(value, -threshold)

def drive_from_joystick(servo0: float, servo1: float):
    global last_command_time

    # Round inputs to 2 decimals
    servo0 = round(servo0, 2)
    servo1 = round(servo1, 2)

    # Apply dead zone
    if abs(servo0) < DEAD_ZONE:
        servo0 = 0
    if abs(servo1) < DEAD_ZONE:
        servo1 = 0

    # If no input, stop
    if servo0 == 0 and servo1 == 0:
        stop()
        return

    # Turning boost if no forward motion
    if abs(servo1) < DEAD_ZONE and abs(servo0) > 0:
        left_speed = int(-servo0 * MAX_TURN_PWM)
        right_speed = int(servo0 * MAX_TURN_PWM)
    else:
        # Regular differential drive logic
        x = servo0
        y = servo1
        left_speed = int((y + x) * MAX_LINEAR_PWM)
        right_speed = int((y - x) * MAX_LINEAR_PWM)

    # Clamp output
    left_speed = max(min(left_speed, MAX_TURN_PWM), -MAX_TURN_PWM)
    right_speed = max(min(right_speed, MAX_TURN_PWM), -MAX_TURN_PWM)

    # Enforce minimum power
    left_speed = apply_min_threshold(left_speed)
    right_speed = apply_min_threshold(right_speed)

    print(f"[JOYSTICK DRIVE] L: {left_speed}, R: {right_speed}")
    car.set_motor_model(left_speed, left_speed, right_speed, right_speed)
    last_command_time = time.time()

def stop():
    print("[STOP] Motors stopping...")
    car.set_motor_model(0, 0, 0, 0)

def check_idle_and_stop():
    if time.time() - last_command_time > IDLE_TIMEOUT:
        stop()
