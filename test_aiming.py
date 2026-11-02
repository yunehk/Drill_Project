import unittest
from shellgame.world import World
from shellgame.controls import Controls
from shellgame.entities import Enemy, Shell
from shellgame.aiming import aim, preview, THROW_SPEED
from shellgame.shells import update_shells
from shellgame.geometry import distance


class AimingTests(unittest.TestCase):
    def setUp(self):
        self.w = World()
        self.w.turrets = []
        self.w.enemies = []
        self.w.player.x, self.w.player.y = 200, 260
        self.w.player.form = 1
        self.w.practice = True

    def test_near_miss_gets_assisted_and_hits_moving_enemy(self):
        w = self.w
        enemy = Enemy(400, 300)
        w.enemies = [enemy]
        direction, target = aim(w, (410, 340))
        self.assertIs(target[1], enemy)
        self.assertAlmostEqual(direction[1]/direction[0], .2)
        w.update(.016, Controls(aim=(410, 340), shed=True))
        for _ in range(80):
            w.update(.016, Controls(aim=(410, 340)))
        self.assertEqual(w.stats['hits'], 1)

    def test_no_lock_through_wall(self):
        w = self.w
        w.player.x = 500
        w.enemies = [Enemy(650, 260)]
        _, target = aim(w, (650, 260))
        self.assertIsNone(target)

    def test_no_lock_far_from_cursor_or_outside_cone(self):
        self.w.enemies = [Enemy(400, 300)]
        self.assertIsNone(aim(self.w, (900, 400))[1])
        self.assertIsNone(aim(self.w, (400, 230))[1])

    def test_switch_can_be_targeted(self):
        w = World(1)
        w.player.form = 1
        w.player.x, w.player.y = 300, 575
        direction, target = aim(w, (445, 585))
        self.assertEqual(target[0], 'switch')
        self.assertEqual(direction, (1, 0))

    def test_preview_stops_where_live_throw_hits_wall(self):
        w = self.w
        w.player.x = 500
        _, end, hit = preview(w, (1, 0))
        self.assertEqual(hit, 'wall')
        w.shells = [Shell(1, 500, 260, THROW_SPEED, 0, True)]
        for _ in range(40):
            update_shells(w, .016)
        shell = w.shells[0]
        self.assertLess(distance(end, (shell.x, shell.y)), 5)

    def test_max_range_and_preview_match_across_frame_rates(self):
        w = self.w
        w.room['walls'] = []
        _, end, _ = preview(w, (1, 0))
        stops = []
        for dt in (.008, .016, .033):
            w.shells = [Shell(1, 200, 260, THROW_SPEED, 0, True)]
            for _ in range(250):
                update_shells(w, dt)
            stops.append(w.shells[0].x)
        self.assertLess(max(stops)-min(stops), 4)
        self.assertTrue(all(abs(x-end[0]) < 4 for x in stops))


if __name__ == '__main__':
    unittest.main()
