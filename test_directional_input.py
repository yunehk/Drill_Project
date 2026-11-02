import unittest
import os
from types import SimpleNamespace
from shellgame.world import World
from shellgame.controls import Controls
from shellgame.entities import Enemy


class StraightThrowTests(unittest.TestCase):
    def test_four_directions_ignore_mouse_and_auto_aim(self):
        for direction in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            with self.subTest(direction=direction):
                w = World()
                w.turrets = []
                w.enemies = []
                w.player.x, w.player.y, w.player.form = 300, 400, 1
                w.update(.01, Controls(aim=(302, 403), shed=True, direction=direction))
                shell = w.shells[0]
                self.assertEqual(w.player.facing, direction)
                if direction[0] == 0:
                    self.assertEqual(shell.vx, 0)
                    self.assertEqual(shell.x, 300)
                else:
                    self.assertEqual(shell.vy, 0)
                    self.assertEqual(shell.y, 400)

    def test_straight_throw_hits_gap_enemy_with_mouse_pointing_up(self):
        w = World()
        w.turrets = []
        w.practice = True
        w.player.x, w.player.y, w.player.form = 553, 390, 1
        w.enemies = [Enemy(607, 390)]
        w.update(.016, Controls(aim=(579, 468), shed=True, direction=(1, 0)))
        for _ in range(40):
            w.update(.016, Controls(aim=(579, 468), direction=(1, 0)))
        self.assertEqual(w.stats['hits'], 1)
        self.assertEqual(w.enemies, [])


@unittest.skipUnless(os.environ.get('SDL_VIDEODRIVER') == 'dummy',
                     'SDL 방향 입력 검사는 dummy 드라이버로 실행')
class DirectionalInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import pico2d as p
        cls.p = p
        p.open_canvas(1100, 780)

    @classmethod
    def tearDownClass(cls):
        cls.p.close_canvas()

    def test_mouse_arrow_click_pipeline_hits_first_room_enemy(self):
        from shellgame.app import App
        p = self.p
        app = App()
        app.audio.muted = True
        app.screen = 'play'
        app.world.practice = True
        app.world.turrets = []
        app.world.player.x, app.world.player.y, app.world.player.form = 553, 390, 1
        app.world.enemies = [Enemy(607, 390)]
        app.event(SimpleNamespace(type=p.SDL_MOUSEMOTION, x=579, y=311))
        app.event(SimpleNamespace(type=p.SDL_KEYDOWN, key=p.SDLK_RIGHT))
        app.event(SimpleNamespace(type=p.SDL_MOUSEBUTTONDOWN,
                                  button=p.SDL_BUTTON_LEFT, x=579, y=311))
        app.update(.016)
        self.assertEqual(app.world.player.facing, (1, 0))
        app.render()
        for _ in range(40):
            app.update(.016)
        self.assertEqual(app.world.stats['hits'], 1)

    def test_mouse_coordinate_conversion_at_150_percent_size(self):
        import importlib
        from shellgame.app import App
        from shellgame.pointer import logical_pointer
        App()
        p = self.p
        runtime = importlib.import_module('pico2d.pico2d')
        try:
            p.SDL_SetWindowSize(runtime.window, 1650, 1170)
            p.SDL_RenderSetLogicalSize(runtime.renderer, 1100, 780)
            x, y = logical_pointer(900, 600)
            self.assertAlmostEqual(x, 600, places=2)
            self.assertAlmostEqual(y, 379, places=2)
        finally:
            p.SDL_SetWindowSize(runtime.window, 1100, 780)
            p.SDL_RenderSetLogicalSize(runtime.renderer, 1100, 780)


if __name__ == '__main__':
    unittest.main()
