import time
import pico2d as p
from .world import World
from .controls import Controls
from .drawing import Painter, BG
from .view import draw_world, draw_menu
from .ui import draw_hud, panel
from .effects import Effects
from .help_view import draw_help

WIDTH, HEIGHT = 1100, 780


class App:
    def __init__(self):
        self.draw = Painter()
        self.world = World()
        self.effects = Effects()
        self.keys = set()
        self.pressed = set()
        self.mouse = (800, 400)
        self.screen = 'menu'
        self.running = True
        self.clock = 0
        self.help = False

    def event(self, event):
        if event.type == p.SDL_QUIT:
            self.running = False
        elif event.type == p.SDL_KEYDOWN:
            if event.key not in self.keys:
                self.pressed.add(event.key)
            self.keys.add(event.key)
        elif event.type == p.SDL_KEYUP:
            self.keys.discard(event.key)
        elif event.type in (p.SDL_MOUSEMOTION, p.SDL_MOUSEBUTTONDOWN):
            self.mouse = (event.x, HEIGHT-1-event.y)
            if event.type == p.SDL_MOUSEBUTTONDOWN and self.screen == 'menu':
                self.screen = 'play'
        elif event.type == p.SDL_WINDOWEVENT:
            if event.event == p.SDL_WINDOWEVENT_FOCUS_LOST:
                self.keys.clear()

    def update(self, dt):
        self.clock += dt
        if p.SDLK_h in self.pressed:
            self.help = not self.help
        if self.help:
            if p.SDLK_RETURN in self.pressed:
                self.help = False
            self.pressed.clear()
            return
        if p.SDLK_ESCAPE in self.pressed:
            if self.screen == 'menu':
                self.running = False
            else:
                self.screen = 'menu'
        if p.SDLK_RETURN in self.pressed:
            self.screen = 'play'
        if p.SDLK_r in self.pressed:
            self.world = World(self.world.index)
            self.effects = Effects()
        if self.screen == 'play':
            controls = Controls(
                int(p.SDLK_d in self.keys)-int(p.SDLK_a in self.keys),
                int(p.SDLK_w in self.keys)-int(p.SDLK_s in self.keys),
                self.mouse, p.SDLK_SPACE in self.pressed,
                p.SDLK_e in self.pressed)
            self.world.update(dt, controls)
            self.effects.receive(self.world.events)
            self.effects.update(dt)
        self.pressed.clear()

    def render(self):
        p.clear_canvas()
        self.draw.rect(0, 0, WIDTH, HEIGHT, BG)
        if self.screen == 'menu':
            draw_menu(self.draw, self.clock)
        else:
            draw_world(self.draw, self.world, self.mouse)
            self.effects.draw(self.draw)
            draw_hud(self.draw, self.world)
            if self.world.result:
                panel(self.draw,
                      '방 탈출 성공!' if self.world.result == 'clear' else '본체가 쓰러졌어!',
                      'R을 눌러 현재 방을 다시 플레이할 수 있어.')
        if self.help:
            draw_help(self.draw)
        p.update_canvas()


def run(max_frames=None):
    p.open_canvas(WIDTH, HEIGHT)
    try:
        app = App()
        previous = time.perf_counter()
        frames = 0
        while app.running and (max_frames is None or frames < max_frames):
            now = time.perf_counter()
            dt = min(.05, now-previous)
            previous = now
            for event in p.get_events():
                app.event(event)
            app.update(dt)
            app.render()
            frames += 1
            time.sleep(.006)
    finally:
        p.close_canvas()
