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

    def _run_servo(self, pulse_width):
        print(f"[CAT TOY] Sending pulse width: {pulse_width}")
        while self.running:
            self.servo.pwm_servo.set_servo_pulse(self.pwm_channel, pulse_width)
            time.sleep(0.05)  # continuous pulses every 50 ms

        # Set pulse to 0 to stop completely
        print("[CAT TOY] Servo stopped, setting pulse to 0")
        self.servo.pwm_servo.set_servo_pulse(self.pwm_channel, 0)

    def set_direction(self, direction):
        if direction == self.current_direction:
            return  # no change needed

        self.current_direction = direction

        if self.thread and self.thread.is_alive():
            self.running = False
            self.thread.join()

        if direction == 'left':
            pulse = 900  # Faster left (2x speed)
        elif direction == 'right':
            pulse = 2100  # Faster right (2x speed)
        else:
            pulse = 0
            self.servo.pwm_servo.set_servo_pulse(self.pwm_channel, pulse)
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_servo, args=(pulse,))
        self.thread.start()

    def stop(self):
        self.set_direction('stop')

# Singleton instance
cat_toy_controller = CatToyController(channel='2')

def control_cat_toy(direction: str):
    cat_toy_controller.set_direction(direction)
