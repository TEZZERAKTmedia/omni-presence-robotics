import os
import cv2
import json
from ultralytics import YOLO

# Paths
video_path = 'Yolo/videos/house_walkthrough.mp4'
frame_output_dir = 'Yolo/object_crops/frames'
json_output_path = 'Yolo/object_crops/crop_metadata.json'
os.makedirs(frame_output_dir, exist_ok=True)

# Load model
model = YOLO('yolov8n.pt')

# Video setup
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
interval = int(fps * 1)  # Every 1 second
frame_id = 0
metadata = []

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    if frame_id % interval == 0:
        frame_name = f'frame_{frame_id}.jpg'
        frame_path = os.path.join(frame_output_dir, frame_name)
        cv2.imwrite(frame_path, frame)

        results = model(frame)
        frame_meta = {
            "frame": frame_name,
            "objects": []
        }

        for i, box in enumerate(results[0].boxes):
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            crop = frame[y1:y2, x1:x2]
            crop_name = f'obj_{frame_id}_{i}.jpg'
            crop_path = os.path.join(frame_output_dir, crop_name)
            cv2.imwrite(crop_path, crop)

            frame_meta["objects"].append({
                "id": i,
                "crop": crop_name,
                "bbox": [x1, y1, x2, y2]
            })

        metadata.append(frame_meta)

    frame_id += 1

cap.release()

# Save metadata
with open(json_output_path, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"✅ Done. Metadata saved to {json_output_path}")
