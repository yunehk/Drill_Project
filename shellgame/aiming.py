"""Shared throw aiming and preview: assist only near the mouse cursor."""
import math
from .geometry import unit, distance, clear_path, clear_at

THROW_SPEED = 820
DRAG = 1.7
STOP_SPEED = 100
# A thrown shell turns edge-on. Worn armor still needs a radius of 17.
SHELL_RADIUS = 8
REST_RADIUS = 17
HIT_RADIUS = 35
MAX_DISTANCE = (THROW_SPEED - STOP_SPEED) / DRAG


def aim(world, mouse):
    p = world.player
    raw = unit(mouse[0]-p.x, mouse[1]-p.y)
    targets = [('enemy', e, (e.x, e.y)) for e in world.enemies if e.hp > 0]
    if world.room['switch'] and not world.gate_open:
        pos = world.room['switch']
        targets.append(('switch', pos, pos))
    choices = []
    for kind, target, pos in targets:
        gap = distance((p.x, p.y), pos)
        cursor_gap = distance(mouse, pos)
        dx, dy = unit(pos[0]-p.x, pos[1]-p.y)
        if (gap <= MAX_DISTANCE-12 and cursor_gap <= 75
                and raw[0]*dx + raw[1]*dy >= math.cos(math.radians(12))
                and clear_path((p.x, p.y), pos, SHELL_RADIUS, world.walls)):
            choices.append((cursor_gap, gap, dx, dy, kind, target))
    if choices:
        best = min(choices, key=lambda choice: choice[:2])
        return (best[2], best[3]), (best[4], best[5])
    return raw, None


def displacement(vx, vy, dt):
    factor = (1-math.exp(-DRAG*dt))/DRAG
    return vx*factor, vy*factor


def landing_point(x, y, safe_pos, walls):
    if clear_at(x, y, REST_RADIUS, walls) or safe_pos is None:
        return x, y
    return safe_pos


def preview(world, direction):
    """Same radius, drag and collision order as the live thrown shell."""
    x, y = world.player.x, world.player.y
    vx, vy = direction[0]*THROW_SPEED, direction[1]*THROW_SPEED
    points = [(x, y)]
    travelled = 0
    safe_pos = (x, y) if clear_at(x, y, REST_RADIUS, world.walls) else None
    while math.hypot(vx, vy) >= STOP_SPEED:
        step = min(.008, math.log(math.hypot(vx, vy)/STOP_SPEED)/DRAG)
        if step < .000001:
            break
        dx, dy = displacement(vx, vy, step)
        nx, ny = x+dx, y+dy
        if not clear_at(nx, ny, SHELL_RADIUS, world.walls):
            return points, landing_point(x, y, safe_pos, world.walls), 'wall'
        x, y = nx, ny
        if clear_at(x, y, REST_RADIUS, world.walls):
            safe_pos = (x, y)
        travelled += math.hypot(dx, dy)
        if travelled >= 16:
            points.append((x, y))
            travelled = 0
        if any(e.hp > 0 and distance((x, y), (e.x, e.y)) < HIT_RADIUS
               for e in world.enemies):
            return points, (x, y), 'enemy'
        switch = world.room['switch']
        if switch and not world.gate_open and distance((x, y), switch) < 36:
            # The actual shell activates the switch and continues flying.
            points.append((x, y))
        decay = math.exp(-DRAG*step)
        vx, vy = vx*decay, vy*decay
    return points, landing_point(x, y, safe_pos, world.walls), 'end'
