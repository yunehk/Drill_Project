import math
import random

COLORS = dict(shed=(255, 182, 70), throw=(255, 220, 130),
              equip=(80, 245, 210), dash=(70, 210, 235),
              block=(255, 235, 160), enemy=(240, 95, 115),
              hurt=(255, 70, 90), key=(255, 218, 80),
              switch=(100, 250, 150), clear=(110, 250, 195),
              wall=(130, 160, 190), shot=(250, 135, 100))


class Effects:
    def __init__(self):
        self.items = []

    def receive(self, events):
        for name, x, y in events:
            count = 5 if name in ('shot', 'wall') else 18
            for _ in range(count):
                angle = random.random() * math.tau
                speed = random.uniform(50, 240)
                self.items.append([x, y, math.cos(angle)*speed,
                                   math.sin(angle)*speed,
                                   random.uniform(.2, .5), COLORS[name]])

    def update(self, dt):
        for item in self.items:
            item[0] += item[2] * dt
            item[1] += item[3] * dt
            item[4] -= dt
        self.items = [item for item in self.items if item[4] > 0]

    def draw(self, painter):
        for x, y, _, _, life, color in self.items:
            painter.circle(x, y, max(1, life*7), color)
