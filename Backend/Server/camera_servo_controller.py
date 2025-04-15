from servo import Servo
import threading
import time

class CameraServoController:
    def __init__(self, pan_channel='0', tilt_channel='1'):
        self.servo = Servo()
        self.pan_channel = self.servo.pwm_channel_map[pan_channel]
        self.tilt_channel = self.servo.pwm_channel_map[tilt_channel]
        self.running = False
        self.pan_thread = None
        self.tilt_thread = None
        self.current_pan = 0000
        self.current_tilt = 1500

        self.lock = threading.Lock()

    def _run_servo(self, channel, pulse_ref):
        while self.running:
            with self.lock:
                pulse = pulse_ref[0]
            self.servo.pwm_servo.set_servo_pulse(channel, pulse)
            time.sleep(0.05)
        self.servo.pwm_servo.set_servo_pulse(channel, 0)

    def update_servo(self, pan_norm: float, tilt_norm: float):
        # Clamp normalized input
        pan_norm = max(min(pan_norm, 1.0), -1.0)
        tilt_norm = max(min(tilt_norm, 1.0), -1.0)

        pan_pulse = int(1500 + (pan_norm * 500))  # 1000 to 2000
        tilt_pulse = int(1500 + (tilt_norm * 500))

        with self.lock:
            self.current_pan = pan_pulse
            self.current_tilt = tilt_pulse

        if not self.running:
            self.running = True
            self.pan_thread = threading.Thread(target=self._run_servo, args=(self.pan_channel, [self.current_pan]), daemon=True)
            self.tilt_thread = threading.Thread(target=self._run_servo, args=(self.tilt_channel, [self.current_tilt]), daemon=True)
            self.pan_thread.start()
            self.tilt_thread.start()

    def stop(self):
        self.running = False
        if self.pan_thread:
            self.pan_thread.join()
        if self.tilt_thread:
            self.tilt_thread.join()
        self.servo.pwm_servo.set_servo_pulse(self.pan_channel, 0)
        self.servo.pwm_servo.set_servo_pulse(self.tilt_channel, 0)

camera_servo_controller = CameraServoController()

def control_camera_servo(pan: float, tilt: float):
    camera_servo_controller.update_servo(pan, tilt)
