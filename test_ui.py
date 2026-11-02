"""Optional SDL integration checks; enable with SDL_VIDEODRIVER=dummy."""
import os
import unittest
from types import SimpleNamespace


@unittest.skipUnless(os.environ.get('SDL_VIDEODRIVER') == 'dummy',
                     'SDL UI 검사는 SDL_VIDEODRIVER=dummy 환경에서 실행')
class InterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import pico2d
        from shellgame.app import WIDTH, HEIGHT
        cls.p = pico2d
        cls.p.open_canvas(WIDTH, HEIGHT)

    @classmethod
    def tearDownClass(cls):
        cls.p.close_canvas()

    def setUp(self):
        from shellgame.app import App
        self.app = App()
        self.app.audio.muted = True

    def press(self, key):
        self.app.event(SimpleNamespace(type=self.p.SDL_KEYDOWN, key=key))
        self.app.update(.016)
        self.app.event(SimpleNamespace(type=self.p.SDL_KEYUP, key=key))

    def test_menu_and_all_rooms_render_with_valid_renderer(self):
        import importlib
        from shellgame.world import World
        self.assertTrue(importlib.import_module('pico2d.pico2d').renderer)
        self.app.render()
        self.press(self.p.SDLK_RETURN)
        for index in range(3):
            self.app.world = World(index)
            self.app.render()

    def test_real_input_sheds_and_re_equips(self):
        self.press(self.p.SDLK_RETURN)
        self.press(self.p.SDLK_SPACE)
        self.assertEqual(self.app.world.player.form, 1)
        for _ in range(25):
            self.app.update(.016)
        self.press(self.p.SDLK_e)
        self.assertEqual(self.app.world.player.form, 2)
        self.assertEqual(self.app.world.stats['equips'], 1)

    def test_help_and_focus_loss_freeze_simulation(self):
        self.press(self.p.SDLK_RETURN)
        self.press(self.p.SDLK_h)
        before = self.app.world.time
        self.app.update(.05)
        self.assertEqual(self.app.world.time, before)
        self.app.render()
        self.press(self.p.SDLK_h)
        self.app.event(SimpleNamespace(type=self.p.SDL_WINDOWEVENT,
                                       event=self.p.SDL_WINDOWEVENT_FOCUS_LOST))
        before = self.app.world.time
        self.app.update(.05)
        self.assertEqual(self.app.world.time, before)
        self.assertTrue(self.app.paused)
        self.app.render()

    def test_campaign_completion_and_restart(self):
        from shellgame.world import World
        self.press(self.p.SDLK_RETURN)
        for index in range(3):
            self.app.world = World(index)
            self.app.world.result = 'clear'
            self.press(self.p.SDLK_RETURN)
            self.app.render()
        self.assertEqual(self.app.screen, 'complete')
        self.press(self.p.SDLK_r)
        self.assertEqual(self.app.screen, 'play')
        self.assertIsNone(self.app.world.result)


if __name__ == '__main__':
    unittest.main()
