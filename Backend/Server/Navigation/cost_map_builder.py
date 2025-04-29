# cost_map_builder.py
import numpy as np

def build_cost_map(landmarks, resolution=0.1, map_size=(500, 500)):
    cost_map = np.zeros(map_size, dtype=np.uint8)
    for landmark in landmarks:
        x, y, _ = landmark
        grid_x = int((x / resolution) + map_size[0] // 2)
        grid_y = int((y / resolution) + map_size[1] // 2)
        if 0 <= grid_x < map_size[0] and 0 <= grid_y < map_size[1]:
            cost_map[grid_x, grid_y] = 100
    return cost_map
