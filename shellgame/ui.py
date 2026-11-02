from .drawing import WHITE, MUTED, CYAN, GOLD, GREEN, RED, ORANGE

FORM_NAMES = {2: '무거운 갑옷 / 방패 설치', 1: '중간 갑옷 / 투척 가능', 0: '작은 본체 / 좁은 틈 통과'}


def draw_hud(draw, world):
    p = world.player
    draw.text(30, 752, 'SHELLBOUND', CYAN, 26)
    draw.text(275, 752, world.room['name'], WHITE, 20)
    draw.text(815, 752, f'{world.time:05.1f}s', MUTED, 20)
    for i in range(5):
        draw.circle(43+i*24, 720, 7, RED if i < p.hp else (56, 65, 79))
    draw.text(185, 720, FORM_NAMES[p.form], ORANGE if p.form else CYAN, 17)
    draw.text(735, 720, '열쇠 획득' if world.key else '목표: 열쇠 → 출구', GREEN if world.key else GOLD, 17)
    draw.text(32, 82, 'WASD 이동   마우스 조준   클릭/Space 투척   E 합체', WHITE, 20)
    draw.text(32, 48, 'R 재시작   Esc 정지   H 도움말   M 음소거', MUTED, 17)
    draw.text(980, 752, '연습' if world.practice else '일반', GOLD if world.practice else MUTED, 17)
    if world.message_time > 0:
        draw.rect(45, 130, 1010, 34, (12, 25, 35))
        draw.text(58, 151, world.message, GOLD, 17)


def panel(draw, title, subtitle):
    draw.rect(200, 260, 700, 235, (13, 27, 39))
    draw.rect(200, 260, 700, 235, CYAN, False)
    draw.text(245, 425, title, CYAN, 38)
    draw.text(245, 370, subtitle, WHITE, 20)
    draw.text(245, 315, 'Enter 진행 / R 다시 하기', MUTED, 17)
