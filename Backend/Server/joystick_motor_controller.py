# joystick_motor_controller.py

from motor import Ordinary_Car

# Initialize the car
car = Ordinary_Car()

def drive_from_joystick(servo0: float, servo1: float):
    """
    Accepts joystick input between -1.0 and 1.0 for x (servo0) and y (servo1),
    and converts it to motor commands using differential drive logic.
    """

    # Optional dead zone to prevent twitchy idle movement
    DEAD_ZONE = 0.1
    if abs(servo0) < DEAD_ZONE:
        servo0 = 0
    if abs(servo1) < DEAD_ZONE:
        servo1 = 0

    # Scale to a slower speed range for safety
    MAX_PWM = 800  # out of a possible 4095
    x = servo0
    y = servo1

    # Simple differential drive formula
    left_speed = int((y + x) * MAX_PWM)
    right_speed = int((y - x) * MAX_PWM)

    # Clamp to safety
    left_speed = max(min(left_speed, MAX_PWM), -MAX_PWM)
    right_speed = max(min(right_speed, MAX_PWM), -MAX_PWM)

    print(f"[JOYSTICK DRIVE] Left: {left_speed}, Right: {right_speed}")
    car.set_motor_model(left_speed, left_speed, right_speed, right_speed)

def stop():
    """Stop all motors safely."""
    print("[STOP] Motors stopping...")
    car.set_motor_model(0, 0, 0, 0)
