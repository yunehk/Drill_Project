from .entities import Shell
from .aiming import THROW_SPEED


def shed(world):
    p = world.player
    if p.dash or p.cooldown > 0:
        return False
    if p.form == 0:
        world.say('이미 작은 본체야! E로 중간 갑옷을 다시 입자.')
        return False
    kind = p.form
    shell = Shell(kind, p.x, p.y)
    if kind == 1:
        shell.vx, shell.vy = p.facing[0] * THROW_SPEED, p.facing[1] * THROW_SPEED
        shell.flying = True
        world.say('던진 갑옷을 조준하고 E: 그 자리로 돌진해서 합체!')
    else:
        world.say('무거운 껍질은 이 자리에 남아 탄을 막아줘.')
    world.shells.append(shell)
    p.form -= 1
    p.cooldown = .28
    world.emit('shed' if kind == 2 else 'throw')
    return True
