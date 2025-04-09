import threading
import base64
import time

class CameraStreamer:
    def __init__(self, camera, fps=20):
        self.camera = camera
        self.latest_frame = None
        self.running = False
        self.lock = threading.Lock()
        self.interval = 1.0 / fps

    def start(self):
        if self.running:
            return
        self.running = True
        thread = threading.Thread(target=self._capture_loop, daemon=True)
        thread.start()

    def _capture_loop(self):
        while self.running:
            frame = self.camera.capture_frame()
            if frame:
                with self.lock:
                    self.latest_frame = base64.b64encode(frame).decode('utf-8')
            time.sleep(self.interval)

    def get_frame(self):
        with self.lock:
            return self.latest_frame

    def stop(self):
        self.running = False
