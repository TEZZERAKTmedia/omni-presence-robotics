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
        self.pan_ref = [0]  # Start at neutral pulse
        self.tilt_ref = [0]

        self.lock = threading.Lock()

        # Stop both channels on boot to prevent spinning
        self.servo.pwm_servo.set_servo_pulse(self.pan_channel, 0)
        self.servo.pwm_servo.set_servo_pulse(self.tilt_channel, 0)

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
        # Clamp to range [-1.0, 1.0]
        pan_norm = max(min(pan_norm, 1.0), -1.0)
        tilt_norm = max(min(tilt_norm, 1.0), -1.0)

        # Convert joystick input to PWM pulses
        pan_pulse = int(abs(pan_norm) * 1000) if abs(pan_norm) >= 0.05 else 0
        tilt_pulse = int(abs(tilt_norm) * 1000) if abs(tilt_norm) >= 0.05 else 0

        pan_dir = "right" if pan_norm > 0 else "left"
        tilt_dir = "up" if tilt_norm > 0 else "down"

        print(f"[INPUT] pan={pan_norm}, tilt={tilt_norm}")
        print(f"[CAMERA SERVO] Pan: {pan_dir} {pan_pulse} | Tilt: {tilt_dir} {tilt_pulse}")

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
        self.servo.pwm_servo.set_servo_pulse(self.pan_channel, 0)
        self.servo.pwm_servo.set_servo_pulse(self.tilt_channel, 0)
        print("[CAMERA SERVO] Both servos stopped")

# Singleton instance
camera_servo_controller = CameraServoController()

def control_camera_servo(pan: float, tilt: float):
    camera_servo_controller.update_servo(pan, tilt)