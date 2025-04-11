from servo import Servo

servo_controller = Servo()

def control_cat_toy(direction, str=None):
    channel = '2'  # PWM channel 10 in your Servo class
    pwm_channel = servo_controller.pwm_channel_map[channel]

    if direction == 'left':
        print("[CAT TOY] Spinning left")
        servo_controller.pwm_servo.set_servo_pulse(pwm_channel, 1000)  # Fast left
    elif direction == 'right':
        print("[CAT TOY] Spinning right")
        servo_controller.pwm_servo.set_servo_pulse(pwm_channel, 2000)  # Fast right
    else:
        print("[CAT TOY] Stopping")
        servo_controller.pwm_servo.set_servo_pulse(pwm_channel, 1500)  # Stop
