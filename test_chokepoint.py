import unittest
from shellgame.world import World
from shellgame.entities import Enemy, Shell
from shellgame.controls import Controls
from shellgame.aiming import aim, THROW_SPEED
from shellgame.geometry import clear_at
from shellgame.shells import update_shells
from shellgame.equipment import candidates


class ChokepointTests(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.world.turrets = []
        self.world.practice = True
        p = self.world.player
        p.x, p.y, p.form = 500, 390, 1

    def test_throw_hits_enemy_camping_at_first_room_gap(self):
        w = self.world
        w.enemies = [Enemy(620, 390)]
        self.assertIsNotNone(aim(w, (620, 390))[1])
        w.update(.016, Controls(aim=(620, 390), shed=True))
        for _ in range(100):
            w.update(.016, Controls(aim=(620, 390)))
        self.assertEqual(w.stats['hits'], 1)
        self.assertEqual(w.enemies, [])
        self.assertTrue(candidates(w))

    def test_thrown_shell_passes_but_worn_armor_cannot(self):
        w = self.world
        w.enemies = []
        w.shells = [Shell(1, 500, 390, THROW_SPEED, 0, True)]
        for _ in range(200):
            update_shells(w, .016)
        self.assertGreater(w.shells[0].x, 650)
        self.assertFalse(clear_at(580, 390, 17, w.walls))
        self.assertTrue(clear_at(580, 390, 9, w.walls))

    def test_shell_stopping_in_gap_returns_to_safe_landing(self):
        w = self.world
        w.enemies = []
        # Just enough speed to stop inside the slit, not past it.
        w.shells = [Shell(1, 540, 390, 167, 0, True)]
        for _ in range(100):
            update_shells(w, .016)
        shell = w.shells[0]
        self.assertFalse(shell.flying)
        self.assertTrue(clear_at(shell.x, shell.y, 17, w.walls))
        self.assertLess(shell.x, 565)
        w.player.form = 0
        self.assertIn(shell, candidates(w))

    def test_solid_wall_still_blocks_projectile(self):
        w = self.world
        w.enemies = []
        w.shells = [Shell(1, 500, 300, THROW_SPEED, 0, True)]
        for _ in range(100):
            update_shells(w, .016)
        self.assertLess(w.shells[0].x, 565)
        self.assertFalse(w.shells[0].flying)


if __name__ == '__main__':
    unittest.main()
