import unittest
from shellgame.world import World
from shellgame.controls import Controls
from shellgame.entities import Shell, Bullet, Enemy
from shellgame.shedding import shed
from shellgame.equipment import equip, update_equip, candidates
from shellgame.shells import update_shells
from shellgame.combat import damage, update_bullets
from shellgame.geometry import clear_at, clear_path
from shellgame.objectives import update_objectives


class RuleTests(unittest.TestCase):
    def setUp(self):
        self.w = World()
        self.w.enemies = []
        self.w.turrets = []

    def test_heavy_shell_stays_and_medium_flies(self):
        w = self.w
        self.assertTrue(shed(w))
        self.assertEqual(w.player.form, 1)
        self.assertFalse(w.shells[0].flying)
        self.assertEqual((w.shells[0].x, w.shells[0].y), w.room['spawn'])
        self.assertFalse(shed(w))  # one press cannot shed both layers
        w.player.cooldown = 0
        self.assertTrue(shed(w))
        self.assertEqual(w.player.form, 0)
        self.assertTrue(w.shells[1].flying)
        w.player.cooldown = 0
        self.assertFalse(shed(w))

    def test_equip_order_and_dash(self):
        w = self.w
        w.player.form = 0
        w.shells = [Shell(2, 160, 260), Shell(1, 300, 260)]
        self.assertEqual([s.kind for s in candidates(w)], [1])
        self.assertTrue(equip(w, (160, 260)))
        for _ in range(30):
            update_equip(w, 1/120)
        self.assertEqual(w.player.form, 1)
        self.assertEqual(w.player.x, 300)
        self.assertEqual(len(w.shells), 1)
        self.assertEqual(w.stats['equips'], 1)

    def test_no_equip_through_wall(self):
        w = self.w
        w.player.x, w.player.y, w.player.form = 500, 260, 0
        w.shells = [Shell(1, 650, 260)]
        self.assertFalse(equip(w, (650, 260)))

    def test_no_equip_outside_range(self):
        w = self.w
        w.player.form = 0
        w.shells = [Shell(1, 510, 260)]
        self.assertFalse(equip(w, (510, 260)))

    def test_small_body_only_fits_through_slit(self):
        self.assertTrue(clear_at(580, 390, 9, self.w.walls))
        self.assertFalse(clear_at(580, 390, 17, self.w.walls))
        self.assertFalse(clear_path((500, 260), (650, 260), 9, self.w.walls))

    def test_shield_blocks_before_player(self):
        w = self.w
        w.player.x = 200
        w.shells = [Shell(2, 250, 260)]
        w.bullets = [Bullet(320, 260, -300, 0)]
        update_bullets(w, .3)
        self.assertEqual(w.player.hp, 5)
        self.assertEqual(w.stats['blocked'], 1)
        self.assertEqual(w.bullets, [])

    def test_small_body_damage_and_invulnerability(self):
        w = self.w
        w.player.form = 0
        w.bullets = [Bullet(w.player.x+5, w.player.y, 0, 0)]
        update_bullets(w, .01)
        self.assertEqual(w.player.hp, 3)
        self.assertFalse(damage(w, 2))
        w.player.invincible = 0
        w.practice = True
        self.assertFalse(damage(w, 2))

    def test_projectile_hits_switch(self):
        w = World(1)
        w.shells = [Shell(1, 350, 575, 680, 0, True)]
        for _ in range(20):
            update_shells(w, .02)
        self.assertTrue(w.gate_open)

    def test_projectile_hits_enemy_once(self):
        w = self.w
        w.enemies = [Enemy(300, 260)]
        w.shells = [Shell(1, 200, 260, 680, 0, True)]
        for _ in range(20):
            update_shells(w, .02)
        self.assertEqual(w.enemies[0].hp, 0)
        self.assertEqual(w.stats['hits'], 1)

    def test_exit_requires_key(self):
        w = self.w
        w.player.x, w.player.y = w.room['exit']
        update_objectives(w)
        self.assertIsNone(w.result)
        w.player.x, w.player.y = w.room['key']
        update_objectives(w)
        self.assertTrue(w.key)
        w.player.x, w.player.y = w.room['exit']
        update_objectives(w)
        self.assertEqual(w.result, 'clear')

    def test_lost_world_stops(self):
        w = self.w
        w.player.hp = 1
        damage(w)
        before = (w.time, w.player.x)
        w.update(.05, Controls(dx=1))
        self.assertEqual(w.result, 'lost')
        self.assertEqual((w.time, w.player.x), before)


if __name__ == '__main__':
    unittest.main()
