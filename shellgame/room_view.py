import math
from .drawing import CYAN, GOLD, GREEN, RED, MUTED, WHITE


def draw_room(draw, world):
    draw.rect(30, 110, 1040, 590, (23, 37, 49))
    for x in range(45, 1055, 40):
        draw.line(x, 125, x, 685, (30, 46, 58))
    for y in range(125, 685, 40):
        draw.line(45, y, 1055, y, (30, 46, 58))
    for x, y, w, h in world.walls:
        draw.rect(x+3, y-5, w, h, (10, 20, 28))
        draw.rect(x, y, w, h, (65, 87, 102))
        draw.rect(x, y+h-5, w, 5, (105, 131, 142))
    gate = world.room['gate']
    if gate:
        x, y, w, h = gate
        color = GREEN if world.gate_open else RED
        draw.rect(x, y, w, h, color, False)
        if not world.gate_open:
            for yy in range(y+5, y+h, 14):
                draw.line(x+2, yy, x+w-2, yy+8, RED)
    switch = world.room['switch']
    if switch:
        x, y = switch
        color = GREEN if world.gate_open else GOLD
        draw.circle(x, y, 24, color, False)
        draw.circle(x, y, 14, color)
        draw.text(x-55, y+45, '갑옷으로 타격', color, 14)
    if not world.key:
        x, y = world.room['key']
        y += math.sin(world.time*4)*4
        draw.circle(x, y, 18, GOLD, False)
        draw.circle(x-7, y+2, 6, GOLD, False)
        draw.rect(x-1, y-1, 20, 5, GOLD)
        draw.rect(x+12, y-6, 5, 8, GOLD)
        draw.text(x-20, y+32, '열쇠', GOLD, 14)
    x, y = world.room['exit']
    draw.rect(x-25, y-30, 50, 60, (27, 65, 58))
    draw.rect(x-25, y-30, 50, 60, GREEN if world.key else MUTED, False)
    draw.text(x-20, y+42, '출구', GREEN, 17)
    if world.key:
        draw.circle(x+13, y, 4, GREEN)
    for turret in world.turrets:
        x, y = turret.x, turret.y
        draw.circle(x, y, 23, (80, 58, 68))
        draw.circle(x, y, 16, RED)
        dx, dy = math.cos(turret.angle), math.sin(turret.angle)
        for offset in (-2, 0, 2):
            draw.line(x-dy*offset, y+dx*offset,
                      x+dx*31-dy*offset, y+dy*31+dx*offset, WHITE)
        if turret.timer < .45:
            draw.circle(x, y, 28, GOLD, False)
    for bullet in world.bullets:
        draw.circle(bullet.x, bullet.y, 8, (100, 45, 48))
        draw.circle(bullet.x, bullet.y, 5, RED)
