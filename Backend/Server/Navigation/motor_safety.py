import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from pca9685_driver import PCA9685  # ✅ this now works

MOTOR_CHANNELS = [0, 1, 2, 3]  # Adjust to match your setup

def neutral_pulse_value():
    return int(1500 * 4096 / 20000)  # 1500 µs => ~307

def initialize_and_stop_servos():
    pwm = PCA9685()
    pwm.set_pwm_freq(50)

    neutral = neutral_pulse_value()

    for ch in MOTOR_CHANNELS:
        pwm.set_motor_pwm(ch, neutral)

    return pwm

def stop_servos(pwm):
    neutral = neutral_pulse_value()
    for ch in MOTOR_CHANNELS:
        pwm.set_motor_pwm(ch, neutral)
