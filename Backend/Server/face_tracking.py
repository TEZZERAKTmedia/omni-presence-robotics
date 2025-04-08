# face_tracking.py
import cv2

class FaceTracker:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.running = False

    def start_tracking(self, camera):
        self.running = True
        print("[FaceTracker] Started")

        while self.running:
            frame = camera.capture_array()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # Optional: stream or save
            # yield frame or stream via WebSocket here

    def stop_tracking(self):
        self.running = False
        print("[FaceTracker] Stopped")
