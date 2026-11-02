import math
from .drawing import CYAN, ORANGE, GOLD, WHITE, RED, BG


def armor(draw, x, y, kind, hollow=False, flash=False):
    radius = 30 if kind == 2 else 20
    color = WHITE if flash else (ORANGE if kind == 2 else GOLD)
    draw.circle(x, y-5, radius+3, (9, 15, 22))
    draw.circle(x, y, radius, (125, 71, 40))
    draw.circle(x, y+3, radius-3, color)
    for side in (-1, 1):
        draw.circle(x+side*radius*.75, y+5, 7 if kind == 2 else 4, color)
    draw.line(x, y-radius+6, x, y+radius-3, (150, 88, 48))
    draw.line(x-radius+6, y, x+radius-6, y, (150, 88, 48))
    if hollow:
        draw.circle(x, y-5, radius*.49, BG)
        draw.line(x-5, y+radius-4, x+1, y+9, BG)
        draw.line(x+1, y+9, x-3, y+2, BG)


def monster(draw, player, clock):
    x, y = player.x, player.y
    if player.invincible > 0 and int(clock*18) % 2:
        return
    draw.circle(x, y-13, 18 if player.form else 12, (9, 16, 24))
    if player.form:
        armor(draw, x, y+4, player.form)
    radius = 12 if player.form == 0 else 14
    dx, dy = player.facing
    head_x, head_y = x+dx*8, y+dy*8-4
    draw.circle(x-dx*13, y-dy*13, 7, (35, 140, 132))
    draw.circle(head_x, head_y, radius, CYAN)
    for side in (-1, 1):
        ex, ey = head_x-dy*side*5+dx*4, head_y+dx*side*5+dy*4
        draw.circle(ex, ey, 4, WHITE)
        draw.circle(ex+dx, ey+dy, 2, BG)
    wiggle = math.sin(clock*8)*2
    draw.circle(x-10, y-13+wiggle, 4, CYAN)
    draw.circle(x+10, y-13-wiggle, 4, CYAN)


def enemy(draw, entity, clock):
    x, y = entity.x, entity.y
    draw.circle(x, y-9, 20, (9, 16, 24))
    color = WHITE if entity.flash else RED
    draw.circle(x, y, 18, color)
    draw.rect(x-16, y+12, 7, 11, color)
    draw.rect(x+9, y+12, 7, 11, color)
    draw.circle(x-6, y+3, 4, BG)
    draw.circle(x+6, y+3, 4, BG)
    draw.line(x-5, y-6, x+5, y-6, BG)
