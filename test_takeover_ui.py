import os
import unittest
from types import SimpleNamespace

@unittest.skipUnless(os.environ.get('SDL_VIDEODRIVER')=='dummy','requires SDL dummy')
class TakeoverUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import pico2d as p
        cls.p=p;p.open_canvas(1100,780)
    @classmethod
    def tearDownClass(cls):cls.p.close_canvas()
    def setUp(self):
        from shellgame.takeover_app import TakeoverApp
        self.app=TakeoverApp();self.app.audio.muted=True
    def press(self,key):
        self.app.event(SimpleNamespace(type=self.p.SDL_KEYDOWN,key=key))
        self.app.update(.016)
        self.app.event(SimpleNamespace(type=self.p.SDL_KEYUP,key=key))
    def test_menu_real_start_pause_restart_help_and_focus(self):
        p=self.p;a=self.app;a.render();self.press(p.SDLK_RETURN)
        self.assertEqual(a.screen,'play');a.render()
        self.press(p.SDLK_h);before=a.world.time;a.update(.1)
        self.assertEqual(a.world.time,before);a.render()
        self.press(p.SDLK_h)
        a.event(SimpleNamespace(type=p.SDL_WINDOWEVENT,event=p.SDL_WINDOWEVENT_FOCUS_LOST))
        before=a.world.time;a.update(.1);self.assertEqual(a.world.time,before)
        self.press(p.SDLK_RETURN);self.assertFalse(a.paused)
        self.press(p.SDLK_r);self.assertIsNone(a.world.host);self.assertFalse(a.world.gate_open)
    def test_real_E_and_attack_pipeline(self):
        p=self.p;a=self.app;self.press(p.SDLK_RETURN)
        m=a.world.machines['ram'];a.world.x,a.world.y=m.x-40,m.y;a.world.stun(m)
        self.press(p.SDLK_e);self.assertEqual(a.world.host,'ram');a.render()
        a.world.update(.4);a.aim=(745,505)
        self.press(p.SDLK_SPACE);self.assertEqual(m.state,'dash')
        a.world.update(.6);a.render()
        self.press(p.SDLK_e);self.assertIsNone(a.world.host)
    def test_practice_and_result_screens_are_explicit(self):
        a=self.app;p=self.p;self.press(p.SDLK_p)
        self.assertTrue(a.world.practice);a.render()
        a.world.result='dead';a.render()
        self.press(p.SDLK_r);self.assertIsNone(a.world.result)
        a.world.result='clear';a.render()
        self.press(p.SDLK_RETURN);self.assertEqual(a.world.stage_index,1)
        self.assertEqual(a.screen,'play')
        a.world.result='clear';self.press(p.SDLK_RETURN)
        self.assertEqual(a.world.stage_index,2)
        a.world.result='clear';self.press(p.SDLK_RETURN)
        self.assertEqual(a.screen,'menu')

    def test_stage_selection_and_current_room_restart(self):
        a=self.app;p=self.p
        self.press(p.SDLK_2);self.assertEqual(a.world.stage_index,1)
        a.completed[0]=12.3
        a.world.gate_open=True
        self.press(p.SDLK_r)
        self.assertEqual(a.world.stage_index,1)
        self.assertEqual(a.completed,{0:12.3})
        self.assertFalse(a.world.gate_open)
        a.render()

    def test_failure_does_not_advance_and_all_rooms_render(self):
        from shellgame.takeover import Arena
        a=self.app;p=self.p;self.press(p.SDLK_RETURN)
        a.world.result='dead';self.press(p.SDLK_RETURN)
        self.assertEqual(a.screen,'menu');self.assertEqual(a.completed,{})
        for stage in range(3):
            a.start(stage=stage)
            a.world.time=2.8
            a.render()
            a.world.result='clear';a.render()

    def test_complete_campaign_through_real_keyboard_pipeline(self):
        from tools.verify_takeover import playthrough
        a=self.app;p=self.p;a.start()
        for stage in range(3):
            _,records=playthrough(stage=stage)
            self.assertEqual(a.world.stage_index,stage)
            for _,move,aim,attack,interact,dodge in records:
                a.keys=set()
                if move[0]>0:a.keys.add(p.SDLK_d)
                if move[0]<0:a.keys.add(p.SDLK_a)
                if move[1]>0:a.keys.add(p.SDLK_w)
                if move[1]<0:a.keys.add(p.SDLK_s)
                a.aim=aim
                if attack or dodge:a.pressed.add(p.SDLK_SPACE)
                if interact:a.pressed.add(p.SDLK_e)
                a.update(1/60)
                if a.world.result:break
            self.assertEqual(a.world.result,'clear')
            a.keys.clear();a.render()
            self.press(p.SDLK_RETURN)
        self.assertEqual(a.screen,'menu')
        self.assertEqual(set(a.completed),{0,1})

if __name__=='__main__':unittest.main()
