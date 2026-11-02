"""Validate SDL resources: pico2d can leave a null renderer without raising."""
import importlib
import pico2d as p


def ensure_renderer():
    runtime = importlib.import_module('pico2d.pico2d')
    if not runtime.window:
        raise RuntimeError('게임 창을 만들지 못했습니다: '+p.SDL_GetError().decode(errors='replace'))
    if not runtime.renderer:
        runtime.renderer = p.SDL_CreateRenderer(runtime.window, -1, p.SDL_RENDERER_SOFTWARE)
    if not runtime.renderer:
        raise RuntimeError('화면 초기화 실패: '+p.SDL_GetError().decode(errors='replace'))
    # Keep drawing and mouse input in the same coordinate system at any DPI.
    if p.SDL_RenderSetLogicalSize(runtime.renderer, 1100, 780) != 0:
        raise RuntimeError('화면 좌표 초기화 실패: '+p.SDL_GetError().decode(errors='replace'))
    p.SDL_SetWindowTitle(runtime.window, 'SHELLBOUND | Drill_Project'.encode())
