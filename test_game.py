import unittest

from game import Game


class RulesTest(unittest.TestCase):
    def test_swap_redirects_locked_attack(self):
        game = Game()
        game.update(1.01)
        target = game.target
        game.click((2, 3))
        self.assertTrue(game.click((5, 3)))
        self.assertEqual(game.target, target)
        game.update(1.6)
        self.assertEqual(game.boss.hp, 5)
        self.assertEqual(game.hero.hp, 1)

    def test_cooldown_and_cancel(self):
        game = Game()
        game.click((2, 3))
        game.click((0, 0))
        game.click((1, 1))
        self.assertIsNone(game.selected)
        game.update(2.1)
        game.click((1, 1))
        self.assertEqual(game.selected, (1, 1))
        game.click((1, 1))
        self.assertIsNone(game.selected)

    def test_defeated_hero_respawns_off_boss(self):
        game = Game()
        game.hero.hp = 1
        game.target = (game.hero.col, game.hero.row)
        game.warning = .01
        game.update(.02)
        self.assertEqual(game.kills, 1)
        self.assertEqual(game.hero.hp, 2)
        self.assertNotEqual((game.hero.col, game.hero.row),
                            (game.boss.col, game.boss.row))

    def test_idle_player_loses(self):
        game = Game()
        game.update(30)
        self.assertEqual(game.result, 'BOSS DOWN - FIRED!')
        elapsed = game.elapsed
        game.update(10)
        self.assertEqual(game.elapsed, elapsed)

    def test_survival_wins(self):
        game = Game()
        game.elapsed = 89.9
        game.next_attack = 10
        game.update(.2)
        self.assertEqual(game.result, 'SHIFT COMPLETE!')


if __name__ == '__main__':
    unittest.main()
