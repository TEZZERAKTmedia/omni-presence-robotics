# path_planner.py
import heapq

def a_star(cost_map, start, goal):
    rows, cols = cost_map.shape
    open_set = [(0, start)]
    came_from = {}
    g_score = {start: 0}

    def heuristic(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]

        x, y = current
        for neighbor in [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]:
            nx, ny = neighbor
            if 0 <= nx < rows and 0 <= ny < cols and cost_map[nx, ny] < 50:
                tentative = g_score[current] + 1
                if neighbor not in g_score or tentative < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative
                    heapq.heappush(open_set, (tentative + heuristic(neighbor, goal), neighbor))
    return None
