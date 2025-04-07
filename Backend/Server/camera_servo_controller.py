from servo import Servo

servo = Servo()

# Safety constraints
MIN_ANGLE = 60
MAX_ANGLE = 120
DEAD_ZONE = 0.05  # Ignore tiny accidental nudges

def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))

def to_angle(norm, min_angle=MIN_ANGLE, max_angle=MAX_ANGLE):
    """
    Converts normalized input (-1.0 to 1.0) to a safe servo angle.
    """
    # Clamp normalized input
    norm = clamp(norm, -1.0, 1.0)

    # Optional dead zone
    if abs(norm) < DEAD_ZONE:
        return (min_angle + max_angle) // 2  # center position

    angle = int((norm + 1) / 2 * (max_angle - min_angle) + min_angle)
    return clamp(angle, min_angle, max_angle)

def control_camera_servo(pan: float, tilt: float):
    """
    Maps joystick input to servo PWM angles with protection.
    """
    try:
        pan_angle = to_angle(pan)
        tilt_angle = to_angle(tilt)

        print(f"[CAMERA SERVO] Pan → {pan_angle}, Tilt → {tilt_angle}")

        servo.set_servo_pwm('0', pan_angle)  # Pan
        servo.set_servo_pwm('1', tilt_angle)  # Tilt

    except Exception as e:
        print(f"[ERROR] Failed to move camera servos: {e}")
