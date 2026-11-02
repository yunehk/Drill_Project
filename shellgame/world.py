import copy
from .entities import Player, Enemy, Turret
from .levels import ROOMS, BOUNDS
from .geometry import unit
from .movement import move_player
from .shedding import shed
from .shells import update_shells
from .equipment import equip, update_equip


class World:
    def __init__(self, room=0):
        self.index = room
        self.room = copy.deepcopy(ROOMS[room])
        self.player = Player(*self.room['spawn'])
        self.shells = []
        self.bullets = []
        self.enemies = [Enemy(*pos) for pos in self.room['enemies']]
        self.turrets = [Turret(*pos) for pos in self.room['turrets']]
        self.time = 0.0
        self.key = False
        self.gate_open = self.room['gate'] is None
        self.result = None
        self.events = []
        self.message = self.room['hint']
        self.message_time = 7.0
        self.stats = dict(blocked=0, hits=0, equips=0)

    @property
    def walls(self):
        walls = BOUNDS + self.room['walls']
        if not self.gate_open:
            walls = walls + [self.room['gate']]
        return walls

    def say(self, text):
        self.message = text
        self.message_time = 3.0

    def emit(self, name, x=None, y=None):
        self.events.append((name, self.player.x if x is None else x,
                            self.player.y if y is None else y))

    def update(self, dt, controls):
        self.events.clear()
        if self.result:
            return
        dt = min(.05, max(0, dt))
        self.time += dt
        self.message_time = max(0, self.message_time - dt)
        p = self.player
        p.cooldown = max(0, p.cooldown - dt)
        p.invincible = max(0, p.invincible - dt)
        p.facing = unit(controls.aim[0] - p.x, controls.aim[1] - p.y)
        if controls.shed:
            shed(self)
        if controls.equip:
            equip(self, controls.aim)
        move_player(self, controls.dx, controls.dy, dt)
        update_shells(self, dt)
        update_equip(self, dt)
