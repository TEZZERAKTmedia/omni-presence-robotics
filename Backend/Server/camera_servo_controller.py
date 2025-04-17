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
        self.pan_ref = [1500]
        self.tilt_ref = [1500]
        self.lock = threading.Lock()

        # Software angle estimation (in degrees)
        self.pan_angle = 0
        self.tilt_angle = 0

        # Rotation limits
        self.pan_max = 180
        self.pan_min = -180
        self.tilt_max = 90
        self.tilt_min = -90

        # Approximate angle per command burst (tune based on motor behavior)
        self.step_per_update = 5  # degrees per input tick

        # Stop servos on boot
        self.servo.pwm_servo.set_servo_pulse(self.pan_channel, 0)
        self.servo.pwm_servo.set_servo_pulse(self.tilt_channel, 0)

    def _run_servo(self, channel, pulse_ref, label):
        while self.running:
            with self.lock:
                pulse = pulse_ref[0]
            print(f"[CAMERA SERVO] {label} pulse: {pulse}")
            self.servo.pwm_servo.set_servo_pulse(channel, pulse)
            time.sleep(0.05)  # Adjust if needed
        self.servo.pwm_servo.set_servo_pulse(channel, 0)
        print(f"[CAMERA SERVO] {label} stopped")

    def update_servo(self, pan_norm: float, tilt_norm: float):
        pan_norm = max(min(pan_norm, 1.0), -1.0)
        tilt_norm = max(min(tilt_norm, 1.0), -1.0)

        # Estimate future angles
        estimated_pan = self.pan_angle + (pan_norm * self.step_per_update)
        estimated_tilt = self.tilt_angle + (tilt_norm * self.step_per_update)

        # Enforce pan limits
        if estimated_pan > self.pan_max:
            pan_norm = 0
            estimated_pan = self.pan_max
            print("[LIMIT] Pan reached max right")
        elif estimated_pan < self.pan_min:
            pan_norm = 0
            estimated_pan = self.pan_min
            print("[LIMIT] Pan reached max left")

        # Enforce tilt limits
        if estimated_tilt > self.tilt_max:
            tilt_norm = 0
            estimated_tilt = self.tilt_max
            print("[LIMIT] Tilt reached max up")
        elif estimated_tilt < self.tilt_min:
            tilt_norm = 0
            estimated_tilt = self.tilt_min
            print("[LIMIT] Tilt reached max down")

        # Only update angles if movement is happening
        if pan_norm != 0:
            self.pan_angle = estimated_pan
        if tilt_norm != 0:
            self.tilt_angle = estimated_tilt

        # Convert normalized input to PWM pulse
        def to_safe_pulse(norm_value, min_pulse=1300, max_pulse=1700):
            if abs(norm_value) < 0.05:
                return 0  # Dead zone
            return int(1500 + norm_value * ((max_pulse - 1500) if norm_value > 0 else (1500 - min_pulse)))

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

    def stop(self):
        self.running = False
        if self.pan_thread:
            self.pan_thread.join()
        if self.tilt_thread:
            self.tilt_thread.join()

        # Reset angles to safe default (if needed)
        self.pan_angle = 0
        self.tilt_angle = 0

        self.servo.pwm_servo.set_servo_pulse(self.pan_channel, 0)
        self.servo.pwm_servo.set_servo_pulse(self.tilt_channel, 0)
        print("[CAMERA SERVO] Both servos stopped")

# Global instance and external controller function
camera_servo_controller = CameraServoController()

def control_camera_servo(pan: float, tilt: float):
    print(f"[INPUT] pan={pan}, tilt={tilt}")
    camera_servo_controller.update_servo(pan, tilt)
