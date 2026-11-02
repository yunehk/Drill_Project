from .drawing import BG, CYAN, GOLD, MUTED, WHITE
from .characters import armor, monster, enemy
from .room_view import draw_room
from .ui import draw_hud
from .equipment import candidates


def draw_world(draw, world, mouse):
    draw_room(draw, world)
    available = candidates(world)
    for shell in world.shells:
        if shell in available:
            draw.circle(shell.x, shell.y, 39 if shell.kind == 2 else 29, CYAN, False)
            draw.text(shell.x-8, shell.y+49, 'E', CYAN, 20)
        armor(draw, shell.x, shell.y, shell.kind, True, shell.hit_flash > 0)
    p = world.player
    if p.dash:
        draw.line(p.x, p.y, p.dash.x, p.dash.y, CYAN)
    for entity in world.enemies:
        enemy(draw, entity, world.time)
    monster(draw, p, world.time)
    if p.form == 1 and p.dash is None:
        dx, dy = p.facing
        for length in range(38, 145, 15):
            draw.circle(p.x+dx*length, p.y+dy*length, 2, GOLD)
    draw.circle(*mouse, 7, CYAN, False)
    draw.line(mouse[0]-12, mouse[1], mouse[0]+12, mouse[1], CYAN)
    draw.line(mouse[0], mouse[1]-12, mouse[0], mouse[1]+12, CYAN)


def draw_menu(draw, clock):
    from .entities import Player
    draw.text(95, 650, 'SHELLBOUND', CYAN, 58)
    draw.text(100, 590, '벗고, 던지고, 다시 입어!', WHITE, 26)
    for index, form in enumerate((2, 1, 0)):
        x = 235 + index*300
        monster(draw, Player(x, 410, form=form), clock)
        draw.text(x-65, 340, ('방패 남기기', '갑옷 던지기', '빠르게 탈출')[index], GOLD, 20)
        if index < 2:
            draw.text(x+115, 412, '→', MUTED, 26)
    draw.text(235, 240, 'Enter / 클릭 : 시작하기', CYAN, 26)
    draw.text(235, 185, 'E로 벗어놓은 갑옷에 날아가 합체할 수 있어.', WHITE, 20)
    draw.text(235, 145, '1 / 2 / 3: 방 선택   F2: 무적 연습 모드   F4: 화면 흔들림', MUTED, 17)
    draw.text(235, 110, '게임 중 H: 도움말   Esc: 일시정지   M: 음소거', MUTED, 17)
