from servo import Servo

servo = Servo()

# For continuous rotation, we expect normalized inputs (-1.0 to 1.0)
DEAD_ZONE = 0.05
# Set the maximum pulse magnitude for full speed.
# For example, if 2000 is full speed in one direction, -2000 is full speed in the opposite.
PULSE_MAX = 2000
# Neutral pulse is 0 (no movement)
NEUTRAL_PULSE = 0

def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))

def to_pulse(norm: float, dead_zone=DEAD_ZONE, pulse_max=PULSE_MAX) -> int:
    """
    Converts a normalized joystick input (-1 to 1) into a pulse value.
    Values within the dead zone return 0 (stop), and values outside are scaled linearly.
    """
    norm = clamp(norm, -1.0, 1.0)
    if abs(norm) < dead_zone:
        return NEUTRAL_PULSE
    # Scale normalized value linearly into the range [-pulse_max, pulse_max]
    return int(norm * pulse_max)

def control_camera_servo(pan: float, tilt: float):
    """
    For continuous rotation servos, we map the normalized pan and tilt values (-1.0 to 1.0)
    to a PWM pulse. A value of 0 results in a pulse of 0 (i.e. servo stops).
    Positive and negative inputs control the rotation direction and speed.
    """
    try:
        pan_pulse = to_pulse(pan)
        tilt_pulse = to_pulse(tilt)
        print(f"[CAMERA SERVO] Pan pulse: {pan_pulse}, Tilt pulse: {tilt_pulse}")
        # Use set_servo_pulse() to deliver the pulse directly.
        # '0' for pan servo, '1' for tilt servo.
        servo.set_servo_pulse('0', pan_pulse)
        servo.set_servo_pulse('1', tilt_pulse)
    except Exception as e:
        print(f"[ERROR] Failed to move camera servos: {e}")
