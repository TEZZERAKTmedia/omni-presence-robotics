import cv2
import os

class USBCamera:
    def __init__(self, width=640, height=480):
        self.cap = None

        for index in range(10):  # 🔧 Check up to /dev/video9
            device = f"/dev/video{index}"
            if os.path.exists(device):
                cap = cv2.VideoCapture(index)
                if cap.isOpened():
                    ret, _ = cap.read()
                    if ret:
                        self.cap = cap
                        print(f"[✅ USB CAMERA] Opened {device}")
                        break
                    else:
                        cap.release()

        if self.cap is None:
            raise RuntimeError("[USB CAMERA ERROR] ❌ No usable /dev/videoX device found")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def capture_frame(self) -> bytes:
        ret, frame = self.cap.read()
        if not ret:
            return b""
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes() if ret else b""

    def release(self):
        if self.cap:
            self.cap.release()
