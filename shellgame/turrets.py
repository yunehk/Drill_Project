import math
from .entities import Bullet
from .geometry import unit, clear_path


def update_turrets(world, dt):
    p = world.player
    for turret in world.turrets:
        ux, uy = unit(p.x - turret.x, p.y - turret.y)
        turret.angle = math.atan2(uy, ux)
        turret.timer -= dt
        if turret.timer <= 0:
            turret.timer = 1.65
            if clear_path((turret.x, turret.y), (p.x, p.y), 3, world.walls):
                world.bullets.append(Bullet(turret.x + ux * 27,
                                            turret.y + uy * 27,
                                            ux * 275, uy * 275))
                world.emit('shot', turret.x, turret.y)
