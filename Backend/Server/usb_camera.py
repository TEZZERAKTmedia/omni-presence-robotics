import ffmpeg
import numpy as np

class USBCamera:
    def __init__(self, device="/dev/video0", width=640, height=480):
        self.device = device
        self.width = width
        self.height = height
        self.process = (
            ffmpeg
            .input(device, format='v4l2', framerate=30, video_size='640x480')
            .output('pipe:', format='rawvideo', pix_fmt='rgb24')
            .run_async(pipe_stdout=True)
        )
        print(f"[✅ USB CAMERA] Capturing from {device}")

    def capture_frame(self) -> bytes:
        frame_size = self.width * self.height * 3  # RGB
        in_bytes = self.process.stdout.read(frame_size)
        if len(in_bytes) != frame_size:
            return b''
        return in_bytes  # Can convert to image if needed

    def release(self):
        self.process.stdout.close()
        self.process.wait()
