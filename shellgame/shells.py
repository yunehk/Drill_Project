import math
from .geometry import clear_at, distance


def update_shells(world, dt):
    for shell in world.shells:
        shell.hit_flash = max(0, shell.hit_flash - dt)
        if not shell.flying:
            continue
        steps = max(1, math.ceil(math.hypot(shell.vx, shell.vy) * dt / 4))
        for _ in range(steps):
            nx = shell.x + shell.vx * dt / steps
            ny = shell.y + shell.vy * dt / steps
            if not clear_at(nx, ny, 17, world.walls):
                shell.flying = False
                world.emit('wall', shell.x, shell.y)
                break
            shell.x, shell.y = nx, ny
            switch = world.room['switch']
            if switch and not world.gate_open and distance((nx, ny), switch) < 36:
                world.gate_open = True
                world.say('스위치 작동! 초록 문이 열렸어.')
                world.emit('switch', *switch)
            hit = next((e for e in world.enemies if e.hp > 0 and
                        distance((nx, ny), (e.x, e.y)) < 35), None)
            if hit:
                hit.hp -= 2
                hit.stun = 1.2
                hit.flash = .2
                shell.flying = False
                world.stats['hits'] += 1
                world.emit('enemy', hit.x, hit.y)
                break
        shell.vx *= math.exp(-1.7 * dt)
        shell.vy *= math.exp(-1.7 * dt)
        if math.hypot(shell.vx, shell.vy) < 100:
            shell.flying = False
        if not shell.flying:
            shell.vx = shell.vy = 0
