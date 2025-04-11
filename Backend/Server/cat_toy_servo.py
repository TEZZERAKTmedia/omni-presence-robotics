from servo import Servo
import threading
import time

class CatToyController:
    def __init__(self, channel='2'):
        self.servo = Servo()
        self.channel = channel
        self.pwm_channel = self.servo.pwm_channel_map[channel]
        self.current_direction = 'stop'
        self.running = False
        self.thread = None

        # Define pulse widths for each speed multiplier
        self.speed_pulse_map = {
            1: 300,  # Original difference
            2: 600,  # 2x
            4: 900,  # 4x
            8: 1200  # 8x (near servo max limits)
        }

    def _run_servo(self, pulse_width):
        print(f"[CAT TOY] Sending pulse width: {pulse_width}")
        while self.running:
            self.servo.pwm_servo.set_servo_pulse(self.pwm_channel, pulse_width)
            time.sleep(0.05)

        print("[CAT TOY] Servo stopped, pulse=0")
        self.servo.pwm_servo.set_servo_pulse(self.pwm_channel, 0)

    def set_direction(self, direction, speed=1):
        if direction == self.current_direction and self.running:
            return

        self.current_direction = direction

        if self.thread and self.thread.is_alive():
            self.running = False
            self.thread.join()

        if direction == 'left':
            pulse = 1500 - self.speed_pulse_map.get(speed, 300)
        elif direction == 'right':
            pulse = 1500 + self.speed_pulse_map.get(speed, 300)
        else:
            pulse = 0
            self.servo.pwm_servo.set_servo_pulse(self.pwm_channel, pulse)
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_servo, args=(pulse,))
        self.thread.start()

    def stop(self):
        self.set_direction('stop')

cat_toy_controller = CatToyController(channel='2')

def control_cat_toy(direction: str, speed: int = 1):
    cat_toy_controller.set_direction(direction, speed)
