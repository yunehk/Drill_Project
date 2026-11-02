"""Small pico2d painter; all visual assets are drawn locally from shapes."""
import os
import pico2d as p

BG = (13, 21, 33)
WHITE = (231, 240, 245)
MUTED = (133, 156, 178)
CYAN = (75, 227, 210)
ORANGE = (241, 157, 65)
RED = (252, 100, 113)
GOLD = (255, 213, 103)
GREEN = (103, 235, 151)


class Painter:
    def __init__(self):
        root = os.environ.get('WINDIR', 'C:/Windows')
        options = [os.path.join(root, 'Fonts', 'malgun.ttf'),
                   os.path.join(root, 'Fonts', 'arial.ttf')]
        path = next((path for path in options if os.path.exists(path)), None)
        if path is None:
            raise RuntimeError('Windows Fonts 폴더에서 malgun.ttf를 찾을 수 없습니다.')
        self.fonts = {size: p.load_font(path, size) for size in (14, 17, 20, 26, 38, 58)}
        self.offset = (0, 0)

    def rect(self, x, y, w, h, color, fill=True):
        ox, oy = self.offset
        p.draw_rectangle(x+ox, y+oy, x+w+ox, y+h+oy, *color, filled=fill)

    def circle(self, x, y, radius, color, fill=True):
        ox, oy = self.offset
        p.draw_circle(x+ox, y+oy, max(1, int(radius)), *color, filled=fill)

    def line(self, x1, y1, x2, y2, color):
        ox, oy = self.offset
        p.draw_line(x1+ox, y1+oy, x2+ox, y2+oy, *color)

    def text(self, x, y, text, color=WHITE, size=20):
        self.fonts[size].draw(x, y, str(text), color)
