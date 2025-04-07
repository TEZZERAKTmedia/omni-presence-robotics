from servo import Servo
import time

servo = Servo()

# Test safe neutral
servo.set_servo_pwm('1', 90)
time.sleep(1)

# Try decreasing
servo.set_servo_pwm('1', 80)
time.sleep(1)

# Try increasing
servo.set_servo_pwm('1', 100)
time.sleep(1)

# Return to center
servo.set_servo_pwm('1', 90)
