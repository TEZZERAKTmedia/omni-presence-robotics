from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import time

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'temp')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload-video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video = request.files['video']
    filename = secure_filename(video.filename)
    timestamped = f"{int(time.time())}_{filename}"
    save_path = os.path.join(UPLOAD_FOLDER, timestamped)

    video.save(save_path)

    return jsonify({
        "message": "uploaded",
        "path": f"temp/{timestamped}"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
