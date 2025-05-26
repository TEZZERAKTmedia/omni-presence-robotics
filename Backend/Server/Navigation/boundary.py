# boundary.py

import time
from servo import Servo

def hold_head_level(pan_channel='0', tilt_channel='1', angle=90):
    servo = Servo()
    print("[BOUNDARY] Locking head to neutral position...")

    try:
        while True:
            servo.set_servo_pwm(pan_channel, angle)
            servo.set_servo_pwm(tilt_channel, angle)
            time.sleep(5)  # Reapply every few seconds for safety
    except KeyboardInterrupt:
        print("\n[BOUNDARY] Servo hold ended.")

if __name__ == '__main__':
    hold_head_level()
