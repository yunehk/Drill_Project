"""Small, serializable simulation entities used by campaign puzzles."""
from dataclasses import dataclass

@dataclass
class Bomb:
    x: float
    y: float
    timer: float = 5.
    team: str = 'player'
    owner: str = 'gun'
    radius: float = 108.
    total: float = 5.
    tick: int = 5
    @property
    def pos(self):return self.x,self.y

@dataclass
class Drone:
    x: float
    y: float
    armor: bool = False
    mode: str = 'patrol'
    hp: int = 1
    stun: float = 0.
    cooldown: float = 4.
    phase: float = 0.
    vx: float = 0.
    vy: float = 0.
    anchor: tuple = ()
    radius: float = 17.
    kind: str = 'drone'
    @property
    def pos(self):return self.x,self.y

@dataclass
class Crate:
    x: float
    y: float
    weight: int = 1
    conductive: bool = False
    alive: bool = True
    radius: float = 17.
    vx: float = 0.
    vy: float = 0.
    kind: str = 'crate'
    @property
    def pos(self):return self.x,self.y

@dataclass
class Guardian:
    x: float = 755.
    y: float = 390.
    hp: int = 3
    exposed: float = 0.
    cooldown: float = 3.8
    flash: float = 0.
    radius: float = 48.
    @property
    def pos(self):return self.x,self.y
