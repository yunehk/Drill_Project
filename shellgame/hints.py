from .equipment import candidates, EQUIP_RANGE
from .geometry import distance
from .drawing import CYAN, GOLD, MUTED


def draw_context(draw, world, mouse):
    p = world.player
    options = candidates(world)
    if options:
        shell = min(options, key=lambda s: distance((s.x, s.y), mouse))
        for i in range(1, 16):
            ratio = i/16
            draw.circle(p.x+(shell.x-p.x)*ratio, p.y+(shell.y-p.y)*ratio, 1, CYAN)
        draw.text(650, 48, 'E: 표시된 갑옷으로 합체', CYAN, 17)
    elif p.form < 2:
        matching = [s for s in world.shells if s.kind == p.form+1]
        if matching:
            shell = min(matching, key=lambda s: distance((s.x, s.y), (p.x, p.y)))
            if shell.flying:
                hint = '갑옷이 멈추면 E로 합체 가능'
            elif distance((shell.x, shell.y), (p.x, p.y)) > EQUIP_RANGE:
                hint = '갑옷 가까이 이동하면 E 표시가 떠'
            else:
                hint = '벽을 피해 갑옷과 일직선으로 서자'
            draw.text(650, 48, hint, GOLD, 14)
    if p.cooldown > 0:
        draw.rect(500, 715, 95, 5, (45, 70, 80))
        draw.rect(500, 715, 95*(1-p.cooldown/.28), 5, CYAN)
