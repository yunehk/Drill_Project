from .geometry import distance, unit, clear_at
from .combat import damage


def update_enemies(world, dt):
    p = world.player
    living = []
    for enemy in world.enemies:
        if enemy.hp <= 0:
            continue
        living.append(enemy)
        enemy.flash = max(0, enemy.flash - dt)
        enemy.stun = max(0, enemy.stun - dt)
        if enemy.stun > 0 or distance((p.x, p.y), (enemy.x, enemy.y)) > 380:
            continue
        dx, dy = unit(p.x - enemy.x, p.y - enemy.y)
        nx, ny = enemy.x + dx * 90 * dt, enemy.y + dy * 90 * dt
        if clear_at(nx, enemy.y, 17, world.walls):
            enemy.x = nx
        if clear_at(enemy.x, ny, 17, world.walls):
            enemy.y = ny
        if distance((p.x, p.y), (enemy.x, enemy.y)) < p.radius + 18:
            damage(world, 2 if p.form == 0 else 1)
    world.enemies = living
