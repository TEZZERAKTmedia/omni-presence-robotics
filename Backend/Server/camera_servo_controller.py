from servo import Servo

servo = Servo()

# Individual neutral points for each continuous rotation servo
NEUTRAL_SERVO_0 = 1520  # Pan servo
NEUTRAL_SERVO_1 = 1500  # Tilt servo

# Maximum delta from neutral (± range around neutral)
PULSE_MAX = 400
DEAD_ZONE = 0.05

def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

def to_pulse(norm: float, neutral: int, pulse_max=PULSE_MAX) -> int:
    """
    Convert a normalized value (-1.0 to 1.0) into a servo pulse around a neutral value.
    If within DEAD_ZONE, return the neutral pulse to stop motion.
    """
    norm = clamp(norm, -1.0, 1.0)
    if abs(norm) < DEAD_ZONE:
        return neutral
    return int(neutral + norm * pulse_max)

def control_camera_servo(pan: float, tilt: float):
    """
    Control two continuous rotation servos for pan and tilt.
    Converts normalized input to PWM values per servo.
    """
    try:
        pan_pulse = to_pulse(pan, neutral=NEUTRAL_SERVO_0)
        tilt_pulse = to_pulse(tilt, neutral=NEUTRAL_SERVO_1)

        print(f"[CAMERA SERVO] Pan pulse: {pan_pulse}, Tilt pulse: {tilt_pulse}")
        servo.set_servo_pulse('0', pan_pulse)
        servo.set_servo_pulse('1', tilt_pulse)
    except Exception as e:
        print(f"[ERROR] Failed to move camera servos: {e}")

# Optional: set both servos to neutral when run directly
if __name__ == "__main__":
    control_camera_servo(0, 0)
