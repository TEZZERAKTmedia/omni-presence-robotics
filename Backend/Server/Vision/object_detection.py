# vision/object_detection.py
from ultralytics import YOLO
import numpy as np

class ObjectDetector:
    def __init__(self, model_path="yolov8n.pt"):
        self.model = YOLO(model_path)

    def detect(self, frame):
        results = self.model.predict(source=frame, verbose=False)[0]
        detections = []
        for r in results.boxes.data.tolist():
            x1, y1, x2, y2, conf, cls = r
            label = self.model.names[int(cls)]
            detections.append({
                "label": label,
                "confidence": conf,
                "bbox": [x1, y1, x2, y2]
            })
        return detections
