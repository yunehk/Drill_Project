from .drawing import CYAN, WHITE, MUTED, GOLD
from .characters import armor


def draw_help(draw):
    draw.rect(95, 175, 910, 440, (14, 28, 40))
    draw.rect(95, 175, 910, 440, CYAN, False)
    draw.text(135, 565, '핵심은 갑옷을 어디에 남길지!', CYAN, 38)
    rows = [
        ('WASD / 마우스', '이동 / 발사 방향 조준'),
        ('Space: 무거운 몸', '제자리에 무거운 껍질을 벗어 탄을 막아.'),
        ('Space: 중간 몸', '중간 껍질을 발사해 적과 스위치를 맞혀.'),
        ('작은 몸', '빠르고 좁은 틈 통과! 대신 피격 피해 2배.'),
        ('E: 다시 입기', '340 이내, 벽이 없는 갑옷으로 돌진해서 합체.'),
        ('입는 순서', '작은 몸 → 중간 갑옷 → 무거운 갑옷'),
    ]
    for i, (key, desc) in enumerate(rows):
        y = 500-i*43
        draw.text(135, y, key, GOLD, 17)
        draw.text(355, y, desc, WHITE, 17)
    draw.text(135, 208, 'H / Enter로 닫기. 막혔다면 R로 현재 방을 다시 시작해.', MUTED, 17)
