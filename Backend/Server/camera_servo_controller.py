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
        self.pan_ref = [0]   # neutral (stopped)
        self.tilt_ref = [0]

        self.lock = threading.Lock()

        # Ensure both are stopped at boot
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
        pan_norm = max(min(pan_norm, 1.0), -1.0)
        tilt_norm = max(min(tilt_norm, 1.0), -1.0)

        # Convert normalized values into directional signed pulses
        pan_pulse = int(pan_norm * 1000) if abs(pan_norm) >= 0.05 else 0
        tilt_pulse = int(tilt_norm * 1000) if abs(tilt_norm) >= 0.05 else 0

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
    print(f"[INPUT] pan={pan}, tilt={tilt}")
    camera_servo_controller.update_servo(pan, tilt)
