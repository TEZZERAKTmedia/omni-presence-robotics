# object_detector.py
import cv2
from ultralytics import YOLO

class ObjectDetector:
    def __init__(self, model_path='yolov8n.pt'):
        self.model = YOLO(model_path)

    def detect(self, frame):
        results = self.model.predict(source=frame, save=False, stream=False, verbose=False)
        detections = []

        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append({
                    'class': self.model.names[cls],
                    'confidence': conf,
                    'bbox': [x1, y1, x2, y2]
                })
        return detections
