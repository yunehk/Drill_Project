"""Interactive pico2d launcher. --frames is a bounded smoke-test only."""
import math
import time
import pico2d as p
from .takeover import Arena, Input, W, H
from .takeover_levels import STAGES
from .drawing import Painter
from .runtime import ensure_renderer
from .pointer import current_pointer, logical_pointer
from .audio import Audio
from . import takeover_view as view

class TakeoverApp:
    def __init__(self):
        ensure_renderer()
        self.draw=Painter()
        self.audio=Audio()
        self.world=Arena(stage=0)
        self.completed={}
        self.keys=set();self.pressed=set()
        self.aim=(745,505)
        self.click=False
        self.screen='menu';self.paused=False;self.help=False
        self.running=True;self.shake=True;self.clock=0

    def start(self,practice=False,stage=0):
        self.completed={}
        self.world=Arena(practice,stage)
        self.screen='play';self.paused=False;self.help=False

    def event(self,event):
        if event.type==p.SDL_QUIT:self.running=False
        elif event.type==p.SDL_KEYDOWN:
            if event.key not in self.keys:self.pressed.add(event.key)
            self.keys.add(event.key)
        elif event.type==p.SDL_KEYUP:self.keys.discard(event.key)
        elif event.type in (p.SDL_MOUSEMOTION,p.SDL_MOUSEBUTTONDOWN):
            self.aim=logical_pointer(event.x,event.y)
            if event.type==p.SDL_MOUSEBUTTONDOWN and getattr(event,'button',0)==p.SDL_BUTTON_LEFT:self.click=True
        elif event.type==p.SDL_WINDOWEVENT and event.event==p.SDL_WINDOWEVENT_FOCUS_LOST:
            self.keys.clear();self.pressed.clear();self.click=False
            if self.screen=='play':self.paused=True

    def update(self,dt):
        self.clock+=dt
        if p.SDLK_m in self.pressed:self.audio.muted=not self.audio.muted
        if p.SDLK_F4 in self.pressed:self.shake=not self.shake
        if p.SDLK_h in self.pressed:self.help=not self.help
        if p.SDLK_ESCAPE in self.pressed:
            if self.help:self.help=False
            elif self.screen=='menu':self.running=False
            else:self.paused=not self.paused
        if self.screen=='menu':
            if p.SDLK_RETURN in self.pressed:self.start()
            elif p.SDLK_p in self.pressed:self.start(True)
            else:
                for index,key in enumerate((p.SDLK_1,p.SDLK_2,p.SDLK_3)):
                    if key in self.pressed:self.start(stage=index)
        elif p.SDLK_r in self.pressed:
            self.world=Arena(self.world.practice,self.world.stage_index)
            self.paused=False;self.help=False
        elif p.SDLK_RETURN in self.pressed:
            if self.world.result == 'clear' and self.world.stage_index < len(STAGES)-1:
                self.completed[self.world.stage_index] = self.world.time
                self.world=Arena(self.world.practice,self.world.stage_index+1)
                self.paused=False;self.help=False
            elif self.world.result:self.screen='menu';self.paused=False
            elif self.paused:self.paused=False
        if p.SDLK_F2 in self.pressed:self.world.practice=not self.world.practice
        if self.screen=='play' and not self.paused and not self.help and not self.world.result:
            move=(int(p.SDLK_d in self.keys)-int(p.SDLK_a in self.keys),
                  int(p.SDLK_w in self.keys)-int(p.SDLK_s in self.keys))
            attack=p.SDLK_SPACE in self.pressed or self.click
            self.world.update(dt,Input(move,self.aim,attack,p.SDLK_e in self.pressed,attack))
            # Existing generated sounds, reused for all new state transitions.
            remap={'impact':'block','break':'block','clear':'key','dead':'hurt'}
            self.audio.receive([(remap.get(n,n),x,y) for n,x,y in self.world.events])
        self.pressed.clear();self.click=False

    def render(self):
        p.clear_canvas()
        d=self.draw
        if self.screen=='menu':view.menu(d,self.clock)
        else:
            s=self.world.shake*8 if self.shake else 0
            d.offset=(math.sin(self.clock*95)*s,math.cos(self.clock*83)*s)
            view.arena(d,self.world,self.aim)
            view.hud(d,self.world,self.paused,self.help,self.audio.muted,self.shake)
            if self.world.result:
                clear=self.world.result=='clear'
                final = self.world.stage_index == len(STAGES)-1
                title = ('3스테이지 탈출 성공!' if {0,1} <= set(self.completed) else '최종 스테이지 클리어!') if final else '스테이지 클리어!'
                view.panel(d,title if clear else '본체가 쓰러졌습니다',[
                    f'기록 {self.world.time:.1f}초 · 몸 탈취 {self.world.stats["swaps"]}회 · 피격 {self.world.stats["hits"]}회',
                    '연습 모드 기록 (피해 없음)' if self.world.practice else '실전 모드 기록',
                    'R  현재 방 재도전    Enter  다음 스테이지' if clear and not final else 'R  현재 방 재도전    Enter  시작 화면',
                    f'현재 방 {self.world.stage_index+1}/3 · 누적 {sum(self.completed.values())+self.world.time:.1f}초'])
            elif self.paused:view.panel(d,'일시정지',['Esc / Enter  계속하기','R  현재 방 재시작','H  도움말'])
        if self.help:view.panel(d,'조작과 몸 탈취',[
            'WASD 이동 · 본체 상태 Space: 짧은 스텝 (무적 없음)',
            'E: 가까운 기절/빈 기체에 탑승 · 다시 E: 하차',
            '탑승 중 마우스 조준 + Space / 클릭: 기체 공격',
            '돌진형은 벽에 충돌하면 기절 · 포격형은 돌진에 약함',
            'R 재시작 · F2 피해 없는 연습 · H 닫기'])
        p.update_canvas()

def run(max_frames=None):
    p.open_canvas(W,H)
    try:
        app=TakeoverApp();last=time.perf_counter();frames=0
        while app.running and (max_frames is None or frames<max_frames):
            now=time.perf_counter();dt=min(.05,now-last);last=now
            for event in p.get_events():app.event(event)
            pointer=current_pointer()
            if pointer is not None:app.aim=pointer
            app.update(dt);app.render();frames+=1
            time.sleep(.006)
    finally:p.close_canvas()
