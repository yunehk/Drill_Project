from .geometry import distance


def update_objectives(world):
    if world.result:
        return
    p = world.player
    if not world.key and distance((p.x, p.y), world.room['key']) < p.radius + 15:
        world.key = True
        world.say('열쇠 획득! 초록색 출구로 가자.')
        world.emit('key', *world.room['key'])
    if distance((p.x, p.y), world.room['exit']) < 31:
        if world.key:
            world.result = 'clear'
            world.emit('clear', *world.room['exit'])
        else:
            world.say('출구가 잠겨 있어. 노란 열쇠를 먼저 찾자.')
