import math
from .geometry import clear_at, distance
from .entities import SPEEDS


def move_player(world, dx, dy, dt):
    p = world.player
    if p.dash is not None:
        return
    length = math.hypot(dx, dy)
    if length:
        dx, dy = dx / length, dy / length
    speed = SPEEDS[p.form]
    # Substeps prevent crossing a wall after a long frame.
    steps = max(1, math.ceil(speed * dt / 4))
    for _ in range(steps):
        nx, ny = p.x + dx * speed * dt / steps, p.y + dy * speed * dt / steps
        if clear_at(nx, p.y, p.radius, world.walls):
            p.x = nx
        if clear_at(p.x, ny, p.radius, world.walls):
            p.y = ny
