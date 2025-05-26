# cost_map_builder.py
import numpy as np
from scipy.ndimage import gaussian_filter

UNKNOWN = -1
FREE = 0
OCCUPIED = 100

def build_cost_map(
    landmarks, 
    visited=None, 
    resolution=0.1, 
    map_size=(500, 500), 
    inflation_radius=3
):
    """
    Builds a cost map from landmarks and optionally visited points.
    """
    cost_map = np.full(map_size, UNKNOWN, dtype=np.int16)

    # Map landmarks as occupied
    for landmark in landmarks:
        x, y, _ = landmark
        grid_x = int((x / resolution) + map_size[0] // 2)
        grid_y = int((y / resolution) + map_size[1] // 2)
        if 0 <= grid_x < map_size[0] and 0 <= grid_y < map_size[1]:
            cost_map[grid_x, grid_y] = OCCUPIED

    # Optional: mark visited locations as free
    if visited:
        for vx, vy in visited:
            grid_x = int((vx / resolution) + map_size[0] // 2)
            grid_y = int((vy / resolution) + map_size[1] // 2)
            if 0 <= grid_x < map_size[0] and 0 <= grid_y < map_size[1]:
                cost_map[grid_x, grid_y] = FREE

    # Inflate obstacles
    binary_obstacles = (cost_map == OCCUPIED).astype(np.float32)
    inflated = gaussian_filter(binary_obstacles, sigma=inflation_radius)
    cost_map[inflated > 0.01] = OCCUPIED

    return cost_map
