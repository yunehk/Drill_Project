from dataclasses import dataclass

RADII = {2: 25, 1: 17, 0: 9}
SPEEDS = {2: 175, 1: 235, 0: 305}


@dataclass
class Player:
    x: float
    y: float
    form: int = 2
    hp: int = 5
    invincible: float = 0
    cooldown: float = 0
    dash: object = None
    facing: tuple = (1, 0)

    @property
    def radius(self):
        return RADII[self.form]


@dataclass
class Shell:
    kind: int
    x: float
    y: float
    vx: float = 0
    vy: float = 0
    flying: bool = False
    hit_flash: float = 0


@dataclass
class Bullet:
    x: float
    y: float
    vx: float
    vy: float


@dataclass
class Enemy:
    x: float
    y: float
    hp: int = 2
    stun: float = 0
    flash: float = 0


@dataclass
class Turret:
    x: float
    y: float
    timer: float = 1.2
    angle: float = 0
