from .geometry import distance, clear_path, clear_at
from .entities import RADII

EQUIP_RANGE = 340


def candidates(world):
    p = world.player
    return [shell for shell in world.shells
            if shell.kind == p.form + 1 and not shell.flying
            and distance((p.x, p.y), (shell.x, shell.y)) <= EQUIP_RANGE
            and clear_at(shell.x, shell.y, RADII[shell.kind], world.walls)
            and clear_path((p.x, p.y), (shell.x, shell.y), p.radius, world.walls)]


def equip(world, aim):
    p = world.player
    if p.dash or p.cooldown > 0:
        return False
    available = candidates(world)
    if not available:
        world.say('회수 불가: 중간 → 무거운 순서, 거리 340 이내, 벽 없는 경로가 필요해.')
        return False
    shell = min(available, key=lambda s: distance((s.x, s.y), aim))
    p.dash = shell
    p.invincible = max(p.invincible, .4)
    world.emit('dash')
    return True


def update_equip(world, dt):
    p = world.player
    if p.dash is None:
        return
    shell = p.dash
    gap = distance((p.x, p.y), (shell.x, shell.y))
    if not clear_path((p.x, p.y), (shell.x, shell.y), p.radius, world.walls):
        p.dash = None
        return
    if gap <= 1300 * dt:
        p.x, p.y = shell.x, shell.y
        p.form = shell.kind
        world.shells.remove(shell)
        p.dash = None
        p.cooldown = .22
        p.invincible = max(p.invincible, .35)
        world.stats['equips'] += 1
        world.emit('equip')
    else:
        p.x += (shell.x - p.x) / gap * 1300 * dt
        p.y += (shell.y - p.y) / gap * 1300 * dt
