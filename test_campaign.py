import unittest
from collections import deque
from shellgame.world import World
from shellgame.campaign import Campaign
from shellgame.controls import Controls
from shellgame.geometry import clear_at, clear_path, distance
from shellgame.levels import ROOMS
from shellgame.entities import RADII


def route_exists(start, target, walls, radius=9):
    # Check a navigable 10-pixel lattice including each short connecting segment.
    node = (round(start[0]/10)*10, round(start[1]/10)*10)
    if not clear_path(start, node, radius, walls):
        return False
    queue, seen = deque([node]), {node}
    while queue:
        x, y = queue.popleft()
        if distance((x, y), target) < 16 and clear_path((x, y), target, radius, walls):
            return True
        for dx, dy in ((10, 0), (-10, 0), (0, 10), (0, -10)):
            other = (x+dx, y+dy)
            if other in seen or not (45 <= other[0] <= 1055 and 125 <= other[1] <= 685):
                continue
            if clear_path((x, y), other, radius, walls):
                seen.add(other)
                queue.append(other)
    return False


class CampaignTests(unittest.TestCase):
    def test_all_rooms_have_key_and_return_routes(self):
        for index, room in enumerate(ROOMS):
            with self.subTest(room=index):
                world = World(index)
                world.gate_open = True
                self.assertTrue(route_exists(room['spawn'], room['key'], world.walls))
                self.assertTrue(route_exists(room['key'], room['exit'], world.walls))

    def test_first_room_requires_shedding(self):
        world = World()
        self.assertFalse(route_exists(world.room['spawn'], world.room['key'], world.walls, 17))

    def test_spawn_accepts_heavy_armor(self):
        for index, room in enumerate(ROOMS):
            self.assertTrue(clear_at(*room['spawn'], RADII[2], World(index).walls))

    def test_campaign_keeps_best_and_finishes(self):
        campaign = Campaign()
        world = World()
        self.assertIs(campaign.advance(world), world)
        for index in range(3):
            world = World(index)
            world.time = 30+index
            world.result = 'clear'
            following = campaign.advance(world)
            self.assertEqual(following.index, index+1) if index < 2 else self.assertIsNone(following)
        retry = World()
        retry.result, retry.time = 'clear', 45
        campaign.advance(retry)
        self.assertEqual(campaign.records[0]['time'], 30)

    def test_restart_resets_every_gameplay_resource(self):
        world = World(1)
        world.key = True
        world.gate_open = True
        world.player.hp = 1
        world = World(world.index)
        self.assertFalse(world.key)
        self.assertFalse(world.gate_open)
        self.assertEqual(world.player.hp, 5)
        self.assertEqual(world.shells, [])


if __name__ == '__main__':
    unittest.main()
