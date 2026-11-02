"""Frame input independent of SDL, also usable in automated playthroughs."""
from dataclasses import dataclass


@dataclass
class Controls:
    dx: float = 0
    dy: float = 0
    aim: tuple = (850, 350)
    shed: bool = False
    equip: bool = False
    direction: object = None
