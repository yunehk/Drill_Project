"""Input-only scripted QA, not footage to present as a human playthrough.

Run from the repository: python -m tools.verify_takeover
With --capture, renders checkpoints through the real pico2d game renderer.
"""
import math
from pathlib import Path
from shellgame.takeover import Arena, Input
from shellgame.geometry import distance

def playthrough(observer=None,stage=2):
    w=Arena(stage=stage);records=[]
    def tick(c=Input(),seconds=1/60):
        for _ in range(max(1,round(seconds*60))):
            w.update(1/60,c)
            records.append((round(w.time,4),c.move,c.aim,c.attack,c.interact,c.dodge))
            if observer:observer(w,c)
            # button presses are edge-triggered, not held every physics frame
            c=Input(c.move,c.aim)
            if w.result:return
    def walk(target):
        for _ in range(1200):
            if distance(w.pos,target)<5:return
            dx,dy=target[0]-w.x,target[1]-w.y
            move=((1 if dx>0 else -1) if abs(dx)>3 else 0,
                  (1 if dy>0 else -1) if abs(dy)>3 else 0)
            tick(Input(move,target))
            if w.result=='clear':return
            if w.result:raise AssertionError(('died',w.time,w.pos,w.log[-8:]))
        raise AssertionError(('blocked',w.pos,target))
    tick(seconds=2.3)
    tick(Input((0,-1),dodge=True),.18)
    tick(seconds=.5)
    if stage==2:
        walk((400,455));walk((550,455))
    else:
        walk((225,365))
    tick(Input(interact=True))
    assert w.host=='ram', ('first board',w.pos,[(m.kind,m.state,m.pos) for m in w.machines.values()])
    if stage==0:
        walk((650,390))
        tick(Input(aim=(868,390),attack=True),.6)
        assert w.gate_open,'ram gate not open'
        walk((930,388))
        tick(Input((1,0),interact=True),.4)
        walk((1027,388))
    else:
        gun=w.machines['gun']
        if stage==2:walk((550,455))
        walk((385,455))
        tick(Input(aim=gun.pos,attack=True),.6)
        assert gun.state=='stun',('gun not stunned',w.pos)
        tick(Input((1,0),interact=True),.4)
        walk(gun.pos)
        tick(Input(interact=True),.4)
        assert w.host=='gun',('gun board',w.pos,w.candidate())
        tick(Input(aim=(868,390),attack=True),5.1)
        assert w.gate_open,'gate not open'
        tick(Input((0,-1),interact=True),.4)
        walk((805,388));walk((930,388));walk((1027,388))
    assert w.result=='clear',('exit',w.pos,w.objective)
    return w,records

def capture():
    import ctypes, importlib
    import pico2d as p
    from shellgame.runtime import ensure_renderer
    from shellgame.takeover_art import GamePainter as Painter
    from shellgame import takeover_view as view
    from shellgame.takeover import W,H
    p.open_canvas(W,H);ensure_renderer();d=Painter()
    out=Path(__file__).resolve().parent.parent/'presentation'/'second'/'screenshots'
    out.mkdir(parents=True,exist_ok=True)
    # pygame is used only to encode raw SDL pixels; gameplay remains pico2d.
    import pygame
    runtime=importlib.import_module('pico2d.pico2d')
    saved=set()
    def observe(w,c):
        tag=None
        if 1.9<w.time<2.0:tag='01_telegraph'
        if w.machines['ram'].state=='stun' and w.host is None:tag='02_stun'
        if w.host=='ram':tag='03_pilot_ram'
        if 'gun' in w.machines and w.machines['gun'].state=='stun' and w.host=='ram':tag='04_armor_break'
        if w.host=='gun':tag='05_pilot_gun'
        if w.gate_open and w.host=='gun':tag='06_gate_open'
        if w.result=='clear':tag='07_clear'
        if tag is None or tag in saved:return
        p.clear_canvas();view.arena(d,w,c.aim);view.hud(d,w)
        pixels=ctypes.create_string_buffer(W*H*4)
        result=p.SDL_RenderReadPixels(runtime.renderer,None,p.SDL_PIXELFORMAT_ABGR8888,pixels,W*4)
        if result!=0:raise RuntimeError(p.SDL_GetError())
        surf=pygame.image.frombuffer(bytes(pixels),(W,H),'RGBA')
        pygame.image.save(surf,str(out/(tag+'.png')))
        p.update_canvas();saved.add(tag)
    try:
        for stage in range(3):
            def stage_observer(w,c):
                if w.time < .1:
                    tag=f'stage{stage+1}_overview'
                    if tag not in saved:
                        p.clear_canvas();view.arena(d,w,c.aim);view.hud(d,w)
                        pixels=ctypes.create_string_buffer(W*H*4)
                        assert p.SDL_RenderReadPixels(runtime.renderer,None,p.SDL_PIXELFORMAT_ABGR8888,pixels,W*4)==0
                        pygame.image.save(pygame.image.frombuffer(bytes(pixels),(W,H),'RGBA'),str(out/(tag+'.png')))
                        p.update_canvas();saved.add(tag)
                if stage==2:observe(w,c)
            w,records=playthrough(stage_observer,stage)
            print('STAGE',stage+1,'NORMAL CLEAR',round(w.time,2),'HP',w.hp,'stats',w.stats)
        print('screens',len(saved))
    finally:p.close_canvas()

if __name__=='__main__':
    import sys
    if '--capture' in sys.argv:capture()
    else:
        for stage in range(3):
            w,r=playthrough(stage=stage);print('STAGE',stage+1,'NORMAL CLEAR',round(w.time,2),'HP',w.hp,'frames',len(r),w.stats)
