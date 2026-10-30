"""Run with: python main.py (requires pico2d)."""
import math
import os
import time

from pico2d import (open_canvas, close_canvas, clear_canvas, update_canvas,
                    get_events, load_font, draw_rectangle, SDL_QUIT,
                    SDL_KEYDOWN, SDL_MOUSEBUTTONDOWN, SDLK_ESCAPE, SDLK_r,
                    SDL_BUTTON_LEFT)
from game import Game, COLS, ROWS, DURATION

WIDTH, HEIGHT = 960, 720
SIZE, LEFT, BOTTOM = 92, 112, 100


def cell_at(x, y):
    col, row = int((x - LEFT) // SIZE), int((y - BOTTOM) // SIZE)
    return (col, row) if 0 <= col < COLS and 0 <= row < ROWS else None


def center(cell):
    return LEFT + (cell[0] + .5) * SIZE, BOTTOM + (cell[1] + .5) * SIZE


def run():
    open_canvas(WIDTH, HEIGHT)
    try:
        font_path = os.path.join(os.environ.get('WINDIR', 'C:/Windows'),
                                 'Fonts', 'consola.ttf')
        font = load_font(font_path, 19)
        title = load_font(font_path, 30)
        game = Game()
        running = True
        previous = time.perf_counter()
        while running:
            now = time.perf_counter()
            dt, previous = min(now - previous, .25), now
            for event in get_events():
                if event.type == SDL_QUIT:
                    running = False
                elif event.type == SDL_KEYDOWN:
                    if event.key == SDLK_ESCAPE:
                        running = False
                    elif event.key == SDLK_r:
                        game = Game()
                elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
                    game.click(cell_at(event.x, HEIGHT - 1 - event.y))
            game.update(dt)
            clear_canvas()
            title.draw(LEFT, 685, 'KEEP THE BOSS ALIVE', (35, 45, 65))
            font.draw(LEFT, 650,
                      f'BOSS HP: {game.boss.hp}/5   TIME: {max(0, DURATION-game.elapsed):04.1f}   KILLS: {game.kills}',
                      (40, 55, 75))
            for col in range(COLS):
                for row in range(ROWS):
                    x, y = LEFT + col * SIZE, BOTTOM + row * SIZE
                    draw_rectangle(x + 2, y + 2, x + SIZE - 2, y + SIZE - 2, 160, 170, 185)
            if game.target is not None:
                x, y = center(game.target)
                pulse = 28 + 5 * math.sin(now * 18)
                for inset in range(4):
                    draw_rectangle(x-pulse-inset, y-pulse-inset,
                                   x+pulse+inset, y+pulse+inset, 230, 45, 40)
                font.draw(x-35, y+27, 'DANGER', (220, 40, 40))
                font.draw(x-23, y-6, f'{game.warning:.1f}', (220, 40, 40))
            if game.flash > 0:
                x, y = center(game.impact)
                title.draw(x-30, y, 'BOOM', (230, 60, 20))
            for actor, label, color in ((game.boss, 'BOSS', (45, 90, 200)),
                                         (game.hero, 'HERO', (180, 65, 35))):
                x, y = center((actor.col, actor.row))
                font.draw(x-25, y-23, label, color)
                font.draw(x-17, y-42, f'HP {actor.hp}', color)
            if game.selected is not None:
                x, y = center(game.selected)
                title.draw(x-10, y+10, '+', (20, 160, 70))
            status = 'READY: click two cells' if game.cooldown <= 0 else f'SWAP RECHARGING: {game.cooldown:.1f}s'
            font.draw(LEFT, 65, status, (30, 110, 60))
            font.draw(LEFT, 35, 'Red target stays fixed!  R: restart  ESC: quit', (60, 60, 60))
            if game.result:
                title.draw(LEFT+100, 380, game.result, (130, 30, 160))
                font.draw(LEFT+170, 345, 'Press R to play again', (130, 30, 160))
            update_canvas()
            time.sleep(.005)
    finally:
        close_canvas()


if __name__ == '__main__':
    run()
