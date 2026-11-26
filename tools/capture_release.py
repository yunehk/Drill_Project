"""Capture the actual SDL renderer during automated normal-mode QA."""
import ctypes
import importlib
from pathlib import Path
import pico2d as p
import pygame
from shellgame.takeover import W,H
from shellgame.takeover_app import TakeoverApp
from shellgame import takeover_view as view
from tools.playthrough_campaign import run_stage

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'screenshots'/'release'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    p.open_canvas(W,H)
    try:
        app=TakeoverApp(save_path=ROOT/'.cache'/'capture-progress.json')
        app.audio.muted=True
        app.progress.records={};app.progress.highest=2
        runtime=importlib.import_module('pico2d.pico2d')
        def save(name):
            pixels=ctypes.create_string_buffer(W*H*4)
            assert p.SDL_RenderReadPixels(runtime.renderer,None,p.SDL_PIXELFORMAT_ABGR8888,pixels,W*4)==0
            surf=pygame.image.frombuffer(bytes(pixels),(W,H),'RGBA')
            pygame.image.save(surf,str(OUT/(name+'.png')))
            p.update_canvas()
        app.render();save('00_menu')
        app.level_select=True;app.render();save('00_stages')
        saved=set()
        for stage in range(8):
            def observe(w,c):
                tags=[]
                if w.time<.05:tags.append(f'{stage+1:02d}_overview')
                if stage==3 and w.host=='mag' and w.magnet_active and any(.5<b.timer<1 for b in w.bombs):tags.append('04_combo')
                if stage==4 and w.power_ready and w.host=='gun':tags.append('05_leave_a_body')
                if stage==5 and w.web_flash>0 and w.relay_on:tags.append('06_web_relay')
                if stage==6 and w.power_ready:tags.append('07_power_connected')
                if stage==7 and w.boss.exposed>9 and w.host=='gun':tags.append('08_guardian_exposed')
                for tag in tags:
                    if tag in saved:continue
                    p.clear_canvas();view.arena(app.draw,w,c.aim);view.hud(app.draw,w)
                    save(tag);saved.add(tag)
            w,frames=run_stage(stage,observe)
            print('VERIFIED',stage+1,round(w.time,2),'seconds','HP',w.hp)
            app.completed[stage]=w.time;app.progress.complete(w)
        app.world=w;app.screen='ending';app.render();save('09_ending')
        app.screen='menu';app.level_select=True;app.render();save('10_completed_map')
        print('Captured',len(list(OUT.glob('*.png'))),'real game screenshots')
    finally:p.close_canvas()

if __name__=='__main__':main()
