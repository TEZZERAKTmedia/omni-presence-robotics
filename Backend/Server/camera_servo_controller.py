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
        self.pan_ref = [0]
        self.tilt_ref = [0]
        self.lock = threading.Lock()

        # Safe movement constraints
        self.min_pulse = 1300
        self.max_pulse = 1700

        # Immediately stop both servos on init
        self.stop_all()

    def _run_servo(self, channel, pulse_ref, label):
        while self.running:
            with self.lock:
                pulse = pulse_ref[0]
            print(f"[CAMERA SERVO] {label} pulse: {pulse}")
            self.servo.pwm_servo.set_servo_pulse(channel, pulse)
            time.sleep(0.05)
        self.servo.pwm_servo.set_servo_pulse(channel, 0)
        print(f"[CAMERA SERVO] {label} stopped")

    def update_servo(self, pan_norm: float, tilt_norm: float):
        pan_norm = max(min(pan_norm, 1.0), -1.0)
        tilt_norm = max(min(tilt_norm, 1.0), -1.0)

        def to_safe_pulse(norm_value):
            if abs(norm_value) < 0.05:
                return 0  # dead zone
            return int(1500 + norm_value * ((self.max_pulse - 1500) if norm_value > 0 else (1500 - self.min_pulse)))

        pan_pulse = to_safe_pulse(pan_norm)
        tilt_pulse = to_safe_pulse(tilt_norm)

        with self.lock:
            self.pan_ref[0] = pan_pulse
            self.tilt_ref[0] = tilt_pulse

        if not self.running:
            self.running = True
            self.pan_thread = threading.Thread(target=self._run_servo, args=(self.pan_channel, self.pan_ref, "Pan"), daemon=True)
            self.tilt_thread = threading.Thread(target=self._run_servo, args=(self.tilt_channel, self.tilt_ref, "Tilt"), daemon=True)
            self.pan_thread.start()
            self.tilt_thread.start()

    def stop_all(self):
        """Force stop servos"""
        self.running = False
        if self.pan_thread:
            self.pan_thread.join()
        if self.tilt_thread:
            self.tilt_thread.join()
        self.servo.pwm_servo.set_servo_pulse(self.pan_channel, 0)
        self.servo.pwm_servo.set_servo_pulse(self.tilt_channel, 0)
        print("[CAMERA SERVO] Both servos stopped")

# Global instance and external control hooks
camera_servo_controller = CameraServoController()

def control_camera_servo(pan: float, tilt: float):
    print(f"[INPUT] pan={pan}, tilt={tilt}")
    camera_servo_controller.update_servo(pan, tilt)

def init_camera_servo():
    print("[INIT] Resetting camera servo to safe state")
    camera_servo_controller.stop_all()
