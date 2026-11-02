import math
from .geometry import clear_at, distance
from .aiming import (displacement, landing_point, DRAG, STOP_SPEED,
                     SHELL_RADIUS, REST_RADIUS, HIT_RADIUS)


def update_shells(world, dt):
    for shell in world.shells:
        shell.hit_flash = max(0, shell.hit_flash - dt)
        if not shell.flying:
            continue
        if clear_at(shell.x, shell.y, REST_RADIUS, world.walls):
            shell.safe_pos = (shell.x, shell.y)
        steps = max(1, math.ceil(math.hypot(shell.vx, shell.vy) * dt / 4))
        for _ in range(steps):
            dx, dy = displacement(shell.vx, shell.vy, dt / steps)
            nx = shell.x + dx
            ny = shell.y + dy
            if not clear_at(nx, ny, SHELL_RADIUS, world.walls):
                shell.flying = False
                world.emit('wall', shell.x, shell.y)
                break
            shell.x, shell.y = nx, ny
            if clear_at(nx, ny, REST_RADIUS, world.walls):
                shell.safe_pos = (nx, ny)
            switch = world.room['switch']
            if switch and not world.gate_open and distance((nx, ny), switch) < 36:
                world.gate_open = True
                world.say('스위치 작동! 초록 문이 열렸어.')
                world.emit('switch', *switch)
            hit = next((e for e in world.enemies if e.hp > 0 and
                        distance((nx, ny), (e.x, e.y)) < HIT_RADIUS), None)
            if hit:
                hit.hp -= 2
                hit.stun = 1.2
                hit.flash = .2
                shell.flying = False
                world.stats['hits'] += 1
                world.emit('enemy', hit.x, hit.y)
                break
            decay = math.exp(-DRAG * dt / steps)
            shell.vx *= decay
            shell.vy *= decay
        if math.hypot(shell.vx, shell.vy) < STOP_SPEED:
            shell.flying = False
        if not shell.flying:
            shell.x, shell.y = landing_point(shell.x, shell.y,
                                            shell.safe_pos, world.walls)
            shell.vx = shell.vy = 0
