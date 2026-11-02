from .world import World
from .levels import ROOMS


class Campaign:
    def __init__(self):
        self.records = {}

    def advance(self, world):
        if world.result != 'clear':
            return world
        record = dict(time=world.time, hp=world.player.hp, **world.stats)
        old = self.records.get(world.index)
        if old is None or record['time'] < old['time']:
            self.records[world.index] = record
        if world.index+1 < len(ROOMS):
            return World(world.index+1)
        return None
