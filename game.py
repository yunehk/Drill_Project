"""Deterministic game rules, independent of pico2d rendering."""
from dataclasses import dataclass

COLS, ROWS = 8, 6
DURATION = 90.0


@dataclass
class Actor:
    col: int
    row: int
    hp: int


class Game:
    def __init__(self):
        self.boss = Actor(2, 3, 5)
        self.hero = Actor(5, 3, 2)
        self.elapsed = 0.0
        self.cooldown = 0.0
        self.selected = None
        self.target = None
        self.warning = 0.0
        self.next_attack = 1.0
        self.kills = 0
        self.flash = 0.0
        self.impact = None
        self.result = None

    def click(self, cell):
        if self.result or self.cooldown > 0 or cell is None:
            return False
        if not (0 <= cell[0] < COLS and 0 <= cell[1] < ROWS):
            return False
        if self.selected is None:
            self.selected = cell
            return False
        first, self.selected = self.selected, None
        if first == cell:
            return False
        for actor in (self.boss, self.hero):
            pos = (actor.col, actor.row)
            if pos == first:
                actor.col, actor.row = cell
            elif pos == cell:
                actor.col, actor.row = first
        self.cooldown = 2.0
        return True

    def update(self, dt):
        if self.result:
            return
        # Small substeps keep attack and cooldown timing stable after slow frames.
        remaining = max(0.0, dt)
        while remaining > 0 and not self.result:
            step = min(remaining, 1 / 120)
            remaining -= step
            self._step(step)

    def _step(self, dt):
        self.elapsed += dt
        self.cooldown = max(0.0, self.cooldown - dt)
        self.flash = max(0.0, self.flash - dt)
        if self.target is not None:
            self.warning -= dt
            if self.warning <= 0:
                self.impact = self.target
                self.flash = 0.3
                for actor in (self.boss, self.hero):
                    if (actor.col, actor.row) == self.target:
                        actor.hp -= 1
                self.target = None
                self.next_attack = 1.25
                if self.hero.hp <= 0:
                    self.kills += 1
                    spawn = ((self.kills * 3 + 4) % COLS,
                             (self.kills * 2 + 1) % ROWS)
                    if spawn == (self.boss.col, self.boss.row):
                        spawn = ((spawn[0] + 1) % COLS, spawn[1])
                    self.hero = Actor(*spawn, 2)
        else:
            self.next_attack -= dt
            if self.next_attack <= 0:
                self.target = (self.boss.col, self.boss.row)
                self.warning = max(0.8, 1.5 - self.elapsed / 180)
        if self.boss.hp <= 0:
            self.result = 'BOSS DOWN - FIRED!'
        elif self.elapsed >= DURATION:
            self.result = 'SHIFT COMPLETE!'
