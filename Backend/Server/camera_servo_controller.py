from servo import Servo

servo = Servo()

# For continuous rotation servos, we use normalized inputs (-1.0 to 1.0)
DEAD_ZONE = 0.05
# Maximum pulse magnitude for full speed (theoretical full scale: ±PULSE_MAX)
PULSE_MAX = 2000  
# The neutral pulse (no movement) for continuous rotation is 0
NEUTRAL_PULSE = 0

def clamp(value, min_val, max_val):
    """Clamp a value between min_val and max_val."""
    return max(min_val, min(value, max_val))

def to_pulse(norm: float, dead_zone=DEAD_ZONE, pulse_max=PULSE_MAX) -> int:
    """
    Converts a normalized joystick input (-1 to 1) into a pulse value.
    If the absolute value is below DEAD_ZONE, return NEUTRAL_PULSE (0),
    ensuring the servo remains stopped when no input is commanded.
    Otherwise, scale the normalized value linearly into the range [-pulse_max, pulse_max].
    """
    norm = clamp(norm, -1.0, 1.0)
    if abs(norm) < dead_zone:
        return NEUTRAL_PULSE
    return int(norm * pulse_max)

def control_camera_servo(pan: float, tilt: float):
    """
    Controls two continuous rotation servos: one for pan (servo '0') and one for tilt (servo '1').
    Normalized inputs (-1.0 to 1.0) are converted to PWM pulses.
    A value of 0 results in a pulse of 0 (servo stops).
    """
    try:
        pan_pulse = to_pulse(pan)
        tilt_pulse = to_pulse(tilt)
        print(f"[CAMERA SERVO] Pan pulse: {pan_pulse}, Tilt pulse: {tilt_pulse}")
        # Send the computed pulse to each servo. This ensures that when pan or tilt is near 0,
        # the servos receive a pulse of 0 (i.e., no motion).
        servo.set_servo_pulse('0', pan_pulse)
        servo.set_servo_pulse('1', tilt_pulse)
    except Exception as e:
        print(f"[ERROR] Failed to move camera servos: {e}")

# Ensure that upon startup both servos are set to neutral (no movement)
if __name__ == "__main__":
    control_camera_servo(0, 0)
