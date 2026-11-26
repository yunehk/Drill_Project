"""Interactive complete campaign. Rendering and storage stay outside simulation."""
import math
import time
import pico2d as p
from .takeover import Arena, Input, W, H
from .takeover_levels import STAGES
from .takeover_progress import Progress,Undo
from .takeover_art import GamePainter
from .runtime import ensure_renderer
from .pointer import current_pointer,logical_pointer
from .audio import Audio
from . import takeover_view as view

class TakeoverApp:
    def __init__(self,save_path=None):
        ensure_renderer()
        self.draw=GamePainter();self.audio=Audio()
        self.progress=Progress(save_path)
        self.audio.muted=self.progress.muted;self.shake=self.progress.shake
        self.world=Arena(stage=0);self.completed={}
        self.keys=set();self.pressed=set();self.aim=(745,505)
        self.click=False;self.secondary=False;self.mouse_held=False
        self.screen='menu';self.paused=False;self.help=False;self.planning=False
        self.running=True;self.clock=0.;self.selection=0;self.level_select=False
        self.fullscreen=False;self.practice_menu=False;self.hint_index=0;self.history=Undo();self.last_snapshot=0.
        self.saved_room=False;self.menu_message=''

    def start(self,practice=False,stage=0):
        self.completed={};self.load(stage,practice)

    def load(self,stage,practice):
        self.world=Arena(practice,stage)
        self.screen='play';self.paused=False;self.help=False;self.planning=False
        self.history=Undo();self.last_snapshot=0.;self.saved_room=False;self.hint_index=0
        self.mouse_held=False;self.click=False;self.secondary=False
        self.selection=stage

    def event(self,event):
        if event.type==p.SDL_QUIT:self.running=False
        elif event.type==p.SDL_KEYDOWN:
            if event.key not in self.keys:self.pressed.add(event.key)
            self.keys.add(event.key)
        elif event.type==p.SDL_KEYUP:self.keys.discard(event.key)
        elif event.type in (p.SDL_MOUSEMOTION,p.SDL_MOUSEBUTTONDOWN,p.SDL_MOUSEBUTTONUP):
            self.aim=logical_pointer(event.x,event.y)
            button=getattr(event,'button',0)
            if event.type==p.SDL_MOUSEBUTTONDOWN:
                if button==p.SDL_BUTTON_LEFT:self.click=True;self.mouse_held=True
                if button==p.SDL_BUTTON_RIGHT:self.secondary=True
            elif event.type==p.SDL_MOUSEBUTTONUP and button==p.SDL_BUTTON_LEFT:self.mouse_held=False
        elif event.type==p.SDL_WINDOWEVENT and event.event==p.SDL_WINDOWEVENT_FOCUS_LOST:
            self.keys.clear();self.pressed.clear();self.click=False;self.mouse_held=False;self.secondary=False
            if self.screen=='play':self.paused=True

    def select_stage(self,index,practice=False):
        if index<=self.progress.highest or practice:self.start(practice,index)
        else:
            self.level_select=True
            self.menu_message=f'{index}번 방을 먼저 클리어하거나, P로 선택한 방을 연습해보세요'

    def update(self,dt):
        self.clock+=dt
        if p.SDLK_m in self.pressed:
            self.audio.muted=not self.audio.muted;self.progress.muted=self.audio.muted;self.progress.save()
        if p.SDLK_F4 in self.pressed:
            self.shake=not self.shake;self.progress.shake=self.shake;self.progress.save()
        if p.SDLK_F11 in self.pressed:
            import importlib
            runtime=importlib.import_module('pico2d.pico2d')
            self.fullscreen=not self.fullscreen
            p.SDL_SetWindowFullscreen(runtime.window,p.SDL_WINDOW_FULLSCREEN_DESKTOP if self.fullscreen else 0)
        if p.SDLK_h in self.pressed:self.help=not self.help
        if p.SDLK_ESCAPE in self.pressed:
            if self.help:self.help=False
            elif self.screen=='menu' and self.level_select:self.level_select=False
            elif self.screen=='menu':self.running=False
            elif self.screen=='ending':self.screen='menu'
            else:self.paused=not self.paused
        if self.screen=='menu':
            if p.SDLK_l in self.pressed:self.level_select=not self.level_select
            if p.SDLK_c in self.pressed:self.start(stage=self.progress.next_stage)
            elif p.SDLK_RETURN in self.pressed:self.select_stage(self.selection if self.level_select else 0)
            elif p.SDLK_p in self.pressed:self.start(True,self.selection if self.level_select else 0)
            else:
                for index,key in enumerate((p.SDLK_1,p.SDLK_2,p.SDLK_3,p.SDLK_4,p.SDLK_5,p.SDLK_6,p.SDLK_7,p.SDLK_8)):
                    if key in self.pressed:
                        self.selection=index;self.select_stage(index,self.practice_menu)
                if p.SDLK_LEFT in self.pressed:self.selection=(self.selection-1)%8
                if p.SDLK_RIGHT in self.pressed:self.selection=(self.selection+1)%8
                if self.click:
                    action=view.menu_hit(self.aim,self.level_select)
                    if action=='start':self.start()
                    elif action=='continue':self.start(stage=self.progress.next_stage)
                    elif action=='levels':self.level_select=True
                    elif isinstance(action,int):self.selection=action;self.select_stage(action,self.practice_menu)
        elif self.screen=='ending':
            if p.SDLK_RETURN in self.pressed:self.screen='menu'
        else:
            if p.SDLK_TAB in self.pressed:self.planning=not self.planning
            if p.SDLK_F1 in self.pressed:
                hints=self.world.level.hints
                if hints:
                    self.world.message=hints[self.hint_index%len(hints)]
                    self.world.message_time=12.;self.hint_index+=1
            if p.SDLK_z in self.pressed:
                restored=self.history.restore()
                if restored:
                    self.world=restored;self.world.result=None
                    self.world.message='이전 행동으로 되돌렸습니다. 다른 배치를 시험해보세요';self.world.message_time=3.
                    self.keys.clear();self.mouse_held=False;self.saved_room=False
            elif p.SDLK_r in self.pressed:self.load(self.world.stage_index,self.world.practice)
            elif p.SDLK_RETURN in self.pressed:
                if self.world.result=='clear':
                    self.completed[self.world.stage_index]=self.world.time
                    if self.world.stage_index<len(STAGES)-1:self.load(self.world.stage_index+1,self.world.practice)
                    else:self.screen='ending'
                elif self.world.result:self.screen='menu';self.paused=False
                elif self.paused:self.paused=False
            if p.SDLK_BACKSPACE in self.pressed:self.screen='menu';self.paused=False
        if p.SDLK_F2 in self.pressed:
            if self.screen=='menu':self.practice_menu=not self.practice_menu
            else:
                self.world.practice=not self.world.practice
                self.world.used_practice |= self.world.practice
        if self.screen=='play' and not(self.paused or self.help or self.planning or self.world.result):
            move=(int(p.SDLK_d in self.keys)-int(p.SDLK_a in self.keys),int(p.SDLK_w in self.keys)-int(p.SDLK_s in self.keys))
            attack=p.SDLK_SPACE in self.pressed or self.click
            interact=p.SDLK_e in self.pressed
            if attack or interact or self.secondary or (any(move) and self.world.time-self.last_snapshot>2.):
                self.history.take(self.world);self.last_snapshot=self.world.time
            self.world.update(dt,Input(move,self.aim,attack,interact,attack,
                                      p.SDLK_SPACE in self.keys or self.mouse_held,self.secondary))
            remap={'impact':'block','break':'blast','clear':'key','dead':'hurt','relay':'key','web':'throw','magnet':'shed'}
            self.audio.receive([(remap.get(n,n),x,y) for n,x,y in self.world.events])
        if self.screen=='play' and self.world.result=='clear' and not self.saved_room:
            self.progress.complete(self.world);self.saved_room=True
        self.pressed.clear();self.click=False;self.secondary=False

    def render(self):
        p.clear_canvas();d=self.draw
        if self.screen=='menu':view.menu(d,self.clock,self.progress,self.selection,self.level_select,self.practice_menu,self.menu_message)
        elif self.screen=='ending':view.ending(d,self.clock,self.progress,self.completed,self.world)
        else:
            shake=self.world.shake*7 if self.shake and not self.planning else 0
            d.offset=(math.sin(self.clock*95)*shake,math.cos(self.clock*83)*shake)
            view.arena(d,self.world,self.aim)
            view.hud(d,self.world,self.paused,self.help,self.audio.muted,self.shake)
            if self.planning:view.planner(d,self.world)
            if self.world.result:
                clear=self.world.result=='clear';final=self.world.stage_index==len(STAGES)-1
                view.panel(d,'정원의 문이 열렸습니다' if clear and final else '스테이지 클리어' if clear else '다시 배치해볼까요?',[
                    f'{self.world.stage_index+1}/8  {self.world.level.name}  ·  {self.world.time:.1f}초',
                    '연습 기록 · 진행 저장 없음' if self.world.used_practice else '진행과 기체 보존 메달을 저장했습니다' if clear else 'Z  직전 행동 되돌리기',
                    'R  현재 방 재시작',
                    'Enter  엔딩 보기' if clear and final else 'Enter  다음 스테이지' if clear else 'Enter  시작 화면'])
            elif self.paused:view.panel(d,'일시정지',['Esc / Enter  계속하기','R  현재 방 재시작','Backspace  시작 화면','H  조작 도움말'])
        if self.help:view.help_screen(d)
        p.update_canvas()

def run(max_frames=None,stage=None):
    p.open_canvas(W,H)
    try:
        app=TakeoverApp()
        if stage is not None:app.start(stage=stage)
        previous=time.perf_counter();frames=0
        while app.running and (max_frames is None or frames<max_frames):
            now=time.perf_counter();dt=min(.05,now-previous);previous=now
            for event in p.get_events():app.event(event)
            pointer=current_pointer()
            if pointer is not None:app.aim=pointer
            app.update(dt);app.render();frames+=1
            time.sleep(.006)
    finally:p.close_canvas()
