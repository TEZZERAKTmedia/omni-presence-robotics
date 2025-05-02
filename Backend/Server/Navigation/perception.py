from math import cos, sin, radians

def estimate_object_world_position(pose, bbox_center, depth, fov=60, img_width=640):
    x, y, heading = pose
    cx = bbox_center[0]

    angle_offset = (cx - img_width / 2) / img_width * fov
    angle_rad = radians(heading + angle_offset)

    dx = depth * cos(angle_rad)
    dy = depth * sin(angle_rad)

    return (x + dx, y + dy)
