from servo import Servo

servo = Servo()

DEAD_ZONE = 0.05

# Pan (symmetric)
PAN_MIN_ANGLE = 60
PAN_MAX_ANGLE = 120
PAN_SCALE = 1.0

# Tilt (asymmetric: more range downward)
TILT_MIN_ANGLE = 70   # Less up
TILT_MAX_ANGLE = 140  # More down
TILT_SCALE = 1.0      # Full input range

def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))

def to_angle(norm, scale, min_angle, max_angle):
    norm = clamp(norm, -1.0, 1.0)

    if abs(norm) < DEAD_ZONE:
        return (min_angle + max_angle) // 2

    scaled = norm * scale
    scaled = clamp(scaled, -1.0, 1.0)

    angle = int((scaled + 1) / 2 * (max_angle - min_angle) + min_angle)
    return clamp(angle, min_angle, max_angle)

def control_camera_servo(pan: float, tilt: float):
    try:
        pan_angle = to_angle(pan, scale=PAN_SCALE, min_angle=PAN_MIN_ANGLE, max_angle=PAN_MAX_ANGLE)
        tilt_angle = to_angle(tilt, scale=TILT_SCALE, min_angle=TILT_MIN_ANGLE, max_angle=TILT_MAX_ANGLE)

        print(f"[CAMERA SERVO] Pan → {pan_angle}, Tilt → {tilt_angle}")
        servo.set_servo_pwm('0', pan_angle)
        servo.set_servo_pwm('1', tilt_angle)

    except Exception as e:
        print(f"[ERROR] Failed to move camera servos: {e}")
