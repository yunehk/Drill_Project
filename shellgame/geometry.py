"""Collision helpers shared by physics, targeting and tests."""
import math


def unit(x, y):
    length = math.hypot(x, y)
    return (x / length, y / length) if length > .001 else (1.0, 0.0)


def clamp(value, low, high):
    return max(low, min(high, value))


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def circle_rect(x, y, radius, rect):
    rx, ry, width, height = rect
    nearest_x = clamp(x, rx, rx + width)
    nearest_y = clamp(y, ry, ry + height)
    return math.hypot(x - nearest_x, y - nearest_y) < radius


def clear_at(x, y, radius, walls):
    return not any(circle_rect(x, y, radius, wall) for wall in walls)


def clear_path(start, end, radius, walls):
    # Sample at most every 4 pixels so a dash cannot tunnel through thin walls.
    count = max(1, math.ceil(distance(start, end) / 4))
    return all(clear_at(start[0] + (end[0]-start[0])*i/count,
                        start[1] + (end[1]-start[1])*i/count,
                        radius, walls) for i in range(count + 1))
