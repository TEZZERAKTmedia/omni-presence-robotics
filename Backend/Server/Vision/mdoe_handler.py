# vision/mode_handler.py
import json
import os

MODE_FILE = os.path.join(os.path.dirname(__file__), "../config/system_mode.json")

def get_mode():
    try:
        with open(MODE_FILE, "r") as f:
            return json.load(f).get("mode", "home")
    except FileNotFoundError:
        return "home"

def set_mode(mode):
    with open(MODE_FILE, "w") as f:
        json.dump({"mode": mode}, f)

def is_away_mode():
    return get_mode() == "away"
