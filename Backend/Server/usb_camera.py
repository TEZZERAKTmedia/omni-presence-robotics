import cv2

class USBCamera:
    def __init__(self, device_index=0, width=640, height=480):
        self.cap = cv2.VideoCapture(device_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def capture_frame(self) -> bytes:
        ret, frame = self.cap.read()
        if not ret:
            return b""
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            return b""
        return jpeg.tobytes()

    def release(self):
        self.cap.release()
 