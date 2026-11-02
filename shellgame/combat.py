import math
from .geometry import clear_at, distance


def damage(world, amount=1):
    p = world.player
    if world.practice or p.invincible > 0 or p.dash or world.result:
        return False
    p.hp -= amount
    p.invincible = 1.15
    world.emit('hurt')
    world.say('피격! 껍질 뒤로 피하거나 E 합체로 빠져나오자.')
    if p.hp <= 0:
        world.result = 'lost'
    return True


def update_bullets(world, dt):
    survivors = []
    p = world.player
    for bullet in world.bullets:
        steps = max(1, math.ceil(math.hypot(bullet.vx, bullet.vy) * dt / 4))
        alive = True
        for _ in range(steps):
            bullet.x += bullet.vx * dt / steps
            bullet.y += bullet.vy * dt / steps
            pos = (bullet.x, bullet.y)
            if not clear_at(*pos, 5, world.walls):
                alive = False
                break
            shield = next((s for s in world.shells if s.kind == 2 and
                           distance(pos, (s.x, s.y)) < 36), None)
            if shield:
                shield.hit_flash = .2
                world.stats['blocked'] += 1
                world.emit('block', *pos)
                alive = False
                break
            if distance(pos, (p.x, p.y)) < p.radius + 5:
                damage(world, 2 if p.form == 0 else 1)
                alive = False
                break
        if alive:
            survivors.append(bullet)
    world.bullets = survivors
