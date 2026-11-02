"""Map the current mouse position into the renderer's logical canvas."""
import ctypes
import importlib
import pico2d as p


def logical_pointer(x, y, height=780):
    runtime = importlib.import_module('pico2d.pico2d')
    lx, ly = ctypes.c_float(), ctypes.c_float()
    p.SDL_RenderWindowToLogical(runtime.renderer, x, y,
                                ctypes.byref(lx), ctypes.byref(ly))
    return lx.value, height-1-ly.value


def current_pointer():
    runtime = importlib.import_module('pico2d.pico2d')
    focus = p.SDL_GetMouseFocus()
    if not focus or ctypes.cast(focus, ctypes.c_void_p).value != ctypes.cast(runtime.window, ctypes.c_void_p).value:
        return None
    x, y = ctypes.c_int(), ctypes.c_int()
    p.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
    return logical_pointer(x.value, y.value)
