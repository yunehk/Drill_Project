"""Renderer assets and typography. Art is optional; logic never depends on it."""
import math
import os
from pathlib import Path
import pico2d as p
from .drawing import Painter

class GamePainter(Painter):
    def __init__(self):
        super().__init__()
        font=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/malgun.ttf'
        if not font.exists():font=font.with_name('arial.ttf')
        for size in (16,18,24,32,48):self.fonts[size]=p.load_font(str(font),size)
        self.images={}
        root=Path(__file__).resolve().parent.parent/'assets/characters'
        for kind in ('core','ram','gun','mag','spider','boss'):
            file=root/(kind+'.png')
            try:self.images[kind]=p.load_image(str(file))
            except Exception:pass

    def sprite(self,kind,x,y,size,angle=0,opacity=1):
        im=self.images.get(kind)
        if im is None:return False
        scale=size/max(im.w,im.h)
        im.opacify(opacity)
        ox,oy=self.offset
        im.composite_draw(angle,'',x+ox,y+oy,im.w*scale,im.h*scale)
        im.opacify(1.)
        return True

    def glow(self,x,y,r,color):
        self.circle(x,y,r+10,tuple(round(a*.96+b*.04) for a,b in zip((15,26,38),color)))
        self.circle(x,y,r+5,tuple(round(a*.90+b*.10) for a,b in zip((15,26,38),color)))
        self.circle(x,y,r,color,False)
