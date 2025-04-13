import cv2

class USBCamera:
    def __init__(self, max_devices=10, width=640, height=480):
        self.cap = None
        self.index = None

        for i in range(max_devices):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print(f"[USB CAMERA] Found working device at /dev/video{i}")
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                    self.cap = cap
                    self.index = i
                    return
                cap.release()

        raise RuntimeError("[USB CAMERA ERROR] No usable /dev/videoX device found")

    def capture_frame(self) -> bytes:
        ret, frame = self.cap.read()
        if not ret:
            return b""
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes() if ret else b""

    def release(self):
        if self.cap:
            self.cap.release()
