from servo import Servo
import time

servo_controller = Servo()
channel = '2'
pwm_channel = servo_controller.pwm_channel_map[channel]

test_pulses = [1500, 1400, 1300, 1200, 1100, 1000, 1500, 1600, 1700, 1800, 1900, 2000]

for pulse in test_pulses:
    print(f"Testing pulse width: {pulse} µs")
    servo_controller.pwm_servo.set_servo_pulse(pwm_channel, pulse)
    time.sleep(2)

# Final stop
servo_controller.pwm_servo.set_servo_pulse(pwm_channel, 1500)
print("Test complete. Servo stopped.")

