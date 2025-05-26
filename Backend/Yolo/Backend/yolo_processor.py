import os
import cv2
import json
from ultralytics import YOLO

def process_video_and_get_metadata(video_path, output_dir="temp/crops", frame_interval=30):
    os.makedirs(output_dir, exist_ok=True)
    model = YOLO("yolov8n.pt")

    cap = cv2.VideoCapture(video_path)
    metadata = []
    frame_id = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_id % frame_interval == 0:
            results = model(frame)
            frame_name = f"frame_{frame_id}.jpg"
            frame_path = os.path.join(output_dir, frame_name)
            cv2.imwrite(frame_path, frame)

            frame_meta = {
                "frame": frame_name,
                "objects": []
            }

            for i, box in enumerate(results[0].boxes):
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                crop = frame[y1:y2, x1:x2]
                crop_name = f"obj_{frame_id}_{i}.jpg"
                crop_path = os.path.join(output_dir, crop_name)
                cv2.imwrite(crop_path, crop)

                frame_meta["objects"].append({
                    "id": i,
                    "crop": crop_name,
                    "bbox": [x1, y1, x2, y2]
                })

            metadata.append(frame_meta)

        frame_id += 1

    cap.release()
    return metadata
