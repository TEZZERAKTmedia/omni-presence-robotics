import cv2

class USBCamera:
    def __init__(self, device_index=0, width=640, height=480):
        self.cap = cv2.VideoCapture(device_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.width = width
        self.height = height

        if not self.cap.isOpened():
            raise RuntimeError(f"[❌ USB CAMERA] Could not open camera index {device_index}")
        print(f"[✅ USB CAMERA] Opened /dev/video{device_index}")

    def capture_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame  # This is already a NumPy BGR image

    def release(self):
        self.cap.release()
