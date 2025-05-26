# frontier_finder.py

import numpy as np

# Constants for cell states
UNKNOWN = -1
FREE = 0
OCCUPIED = 1

def is_frontier_cell(grid, x, y):
    """
    A frontier cell is a FREE cell adjacent to at least one UNKNOWN cell.
    """
    if grid[x, y] != FREE:
        return False

    h, w = grid.shape
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < h and 0 <= ny < w:
                if grid[nx, ny] == UNKNOWN:
                    return True
    return False

def find_frontiers(grid):
    """
    Scans the occupancy grid and returns a list of (x, y) coordinates
    for all frontier cells.
    """
    frontiers = []
    h, w = grid.shape

    for x in range(1, h - 1):
        for y in range(1, w - 1):
            if is_frontier_cell(grid, x, y):
                frontiers.append((x, y))

    return frontiers
