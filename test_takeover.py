"""Behavioral tests for the new arena, including a full input-only escape."""
import unittest
from shellgame.takeover import Arena, Input, Shot, GATE, SOLIDS
from shellgame.geometry import distance

class TakeoverTests(unittest.TestCase):
    def test_only_stunned_or_empty_nearby_body_can_be_boarded(self):
        w=Arena();m=w.machines['ram'];w.x,w.y=m.x-40,m.y
        w.update(.01,Input(interact=True));self.assertIsNone(w.host)
        w.stun(m);w.update(.4);w.update(.01,Input(interact=True))
        self.assertEqual(w.host,'ram');self.assertIn('ram',w.boarded)

    def test_wall_collision_stuns_enemy_without_teleport(self):
        w=Arena(True);w.update(3)
        m=w.machines['ram'];self.assertEqual(m.state,'stun')
        self.assertTrue(w.allowed(*m.pos,m.radius))
        self.assertGreater(m.x,139)

    def test_ejection_searches_safe_position_and_cannot_reboard_same_press(self):
        w=Arena();m=w.machines['ram'];m.x,m.y=164,390
        w.board(m);w.interact_cd=0
        w.update(.01,Input(move=(-1,0),interact=True))
        self.assertIsNone(w.host);self.assertEqual(m.state,'empty')
        self.assertTrue(w.allowed(*w.pos,11))
        self.assertGreaterEqual(distance(w.pos,m.pos),40)

    def test_dash_has_no_damage_immunity(self):
        w=Arena();w.board(w.machines['ram']);m=w.machines['ram']
        m.cooldown=0;w.update(.01,Input(aim=(800,390),attack=True))
        self.assertEqual(m.state,'dash')
        w.hurt();self.assertEqual(m.hp,3)

    def test_enemy_dash_and_player_dash_do_not_tunnel_through_gate(self):
        w=Arena(True);m=w.machines['ram'];m.x,m.y=800,390
        w.board(m);m.cooldown=0
        w.update(.8,Input(aim=(1000,390),attack=True))
        self.assertLessEqual(m.x+m.radius,854)

    def test_charge_breaks_artillery_armor_and_creates_boarding_window(self):
        w=Arena(True);m=w.machines['ram'];m.x,m.y=450,505;w.board(m)
        m.cooldown=0;w.update(.6,Input(aim=(745,505),attack=True))
        gun=w.machines['gun'];self.assertFalse(gun.armor)
        self.assertEqual(gun.state,'stun');self.assertGreater(gun.timer,5)

    def test_only_player_artillery_opens_gate(self):
        w=Arena();w.fire((700,390),(868,390),'enemy','gun',True);w.update(1)
        self.assertFalse(w.gate_open)
        w.fire((700,390),(868,390),'player','gun',True);w.update(1)
        self.assertTrue(w.gate_open)

    def test_destroyed_essential_body_respawns_without_resetting_progress(self):
        w=Arena();w.board(w.machines['ram']);m=w.machines['ram']
        m.hp=1;w.hurt();self.assertIsNone(w.host)
        self.assertEqual(m.state,'wreck');w.update(5.2)
        self.assertNotEqual(m.state,'wreck');self.assertIn('ram',w.boarded)

    def test_small_gap_rejects_machine_but_accepts_core(self):
        w=Arena();self.assertTrue(w.allowed(982,388,11))
        self.assertFalse(w.allowed(982,388,25))

    def test_core_cannot_cheese_exit_without_objectives(self):
        w=Arena();w.x,w.y=1025,390;w.update(.01)
        self.assertIsNone(w.result)
        w.gate_open=True;w.update(.01);self.assertIsNone(w.result)
        w.boarded={'ram','gun'};w.update(.01);self.assertEqual(w.result,'clear')

    def test_restart_resets_progress_and_practice_is_explicit(self):
        w=Arena(True);w.hurt();self.assertEqual(w.hp,5)
        fresh=Arena();self.assertEqual(fresh.boarded,set())
        self.assertFalse(fresh.gate_open);self.assertFalse(fresh.practice)

    def test_input_only_walkthrough_finishes_in_normal_mode(self):
        from tools.verify_takeover import playthrough
        world,records=playthrough()
        self.assertEqual(world.result,'clear')
        self.assertFalse(world.practice)
        self.assertGreater(world.hp,0)
        self.assertEqual(world.boarded,{'ram','gun'})

if __name__=='__main__':unittest.main()
