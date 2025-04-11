from servo import Servo



servo_controller = Servo()

def control_cat_toy(direction, str=None):
    channel = '2'
    if direction == 'left':
        print("[CAT TOY] Spinning left")
        servo_controller.pmw_servo.set_servo_pulse(servo_controller.pmw_channel_map[channel], 1000)  # Faster left
    elif direction == 'right':
        print("[CAT TOY] Spinning right")
        servo_controller.pmw_servo.set_servo_pulse(servo_controller.pmw_channel_map[channel], 2000)  # Faster right
    else:
        print("[CAT TOY] Stopping")
        servo_controller.pmw_servo.set_servo_pulse(servo_controller.pmw_channel_map[channel], 1500)  # Stop
