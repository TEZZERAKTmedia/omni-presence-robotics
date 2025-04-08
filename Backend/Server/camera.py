import time
import cv2
import numpy as np
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
from libcamera import Transform

class Camera:
    def __init__(self, preview_size=(640, 480), stream_size=(400, 300), hflip=True, vflip=True):
        self.camera = Picamera2()
        self.transform = Transform(hflip=1 if hflip else 0, vflip=1 if vflip else 0)

        # Preview config
        preview_config = self.camera.create_preview_configuration(
            main={"size": preview_size},
            transform=self.transform
        )
        self.camera.configure(preview_config)
        self.camera.start()

        # Stream config for video recording
        self.stream_size = stream_size
        self.stream_config = self.camera.create_video_configuration(
            main={"size": stream_size},
            transform=self.transform
        )
        self.streaming = False

    def start_image(self):
        """Start the camera preview."""
        self.camera.start_preview(Preview.QTGL)
        self.camera.start()

    def save_image(self, filename: str) -> dict:
        """Capture and save a still image."""
        try:
            metadata = self.camera.capture_file(filename)
            return metadata
        except Exception as e:
            print(f"[ERROR] Capturing image: {e}")
            return None

    def start_stream(self, filename: str = None):
        """Start H264 video stream (used for saving video)."""
        if not self.streaming:
            if self.camera.started:
                self.camera.stop()
            self.camera.configure(self.stream_config)
            encoder = H264Encoder()
            output = FileOutput(filename if filename else "/dev/null")
            self.camera.start_recording(encoder, output)
            self.streaming = True

    def stop_stream(self):
        """Stop the video stream or recording."""
        if self.streaming:
            try:
                self.camera.stop_recording()
                self.streaming = False
            except Exception as e:
                print(f"[ERROR] Stopping stream: {e}")

    def save_video(self, filename: str, duration: int = 10):
        """Record and save video for a given duration."""
        self.start_stream(filename)
        time.sleep(duration)
        self.stop_stream()

    def capture_frame(self) -> bytes:
        """Capture a single frame and return as JPEG-encoded bytes."""
        try:
            frame = self.camera.capture_array()
            _, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes()
        except Exception as e:
            print(f"[ERROR] Capturing frame: {e}")
            return b""

    def close(self):
        """Close and clean up the camera."""
        if self.streaming:
            self.stop_stream()
        self.camera.close()

# 🧪 Optional test
if __name__ == '__main__':
    print("Starting camera test...")
    cam = Camera()
    time.sleep(2)
    cam.save_image("test.jpg")
    print("Image saved.")
    cam.close()
