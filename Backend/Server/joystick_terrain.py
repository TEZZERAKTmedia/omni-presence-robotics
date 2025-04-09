from motor import Ordinary_Car
import time

# Initialize the car
car = Ordinary_Car()

# Constants
DEAD_ZONE = 0.1
MIN_THRESHOLD = 300
MAX_PWM = 1600
IDLE_TIMEOUT = 10

# State
last_command_time = time.time()

def apply_min_threshold(value, threshold=MIN_THRESHOLD):
    if value == 0:
        return 0
    elif value > 0:
        return max(value, threshold)
    else:
        return min(value, -threshold)

def drive_from_terrain_joystick(fl: float, fr: float, bl: float, br: float):
    global last_command_time

    def process(val):
        val = round(val, 2)
        if abs(val) < DEAD_ZONE:
            return 0
        return val

    fl = process(fl)
    fr = process(fr)
    bl = process(bl)
    br = process(br)

    if fl == 0 and fr == 0 and bl == 0 and br == 0:
        stop()
        return

    def scale(val):
        return apply_min_threshold(int(val * MAX_PWM))

    fl_pwm = scale(fl)
    fr_pwm = scale(fr)
    bl_pwm = scale(bl)
    br_pwm = scale(br)

    print(f"[TERRAIN] FL: {fl_pwm}, FR: {fr_pwm}, BL: {bl_pwm}, BR: {br_pwm}")
    car.set_motor_model(fl_pwm, bl_pwm, fr_pwm, br_pwm)
    last_command_time = time.time()

def stop():
    print("[STOP] Motors stopping...")
    car.set_motor_model(0, 0, 0, 0)

def check_idle_and_stop():
    if time.time() - last_command_time > IDLE_TIMEOUT:
        stop()
