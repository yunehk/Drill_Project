import unittest
from shellgame.takeover import Arena,Input
from shellgame.takeover_levels import STAGES
from tools.verify_takeover import playthrough

class StageTests(unittest.TestCase):
    def test_three_different_authored_layouts_and_increasing_hazards(self):
        self.assertEqual(len(STAGES),3)
        self.assertEqual(len({s.solids for s in STAGES}),3)
        self.assertEqual(set(Arena(stage=0).machines),{'ram'})
        self.assertFalse(STAGES[0].turret_interval)
        self.assertFalse(STAGES[1].laser)
        self.assertTrue(STAGES[2].turret_interval)
        self.assertTrue(STAGES[2].laser)

    def test_all_machine_and_core_spawns_are_valid_in_every_room(self):
        for stage in range(3):
            w=Arena(stage=stage)
            self.assertTrue(w.allowed(*w.pos,w.radius))
            for m in w.machines.values():self.assertTrue(w.allowed(*m.pos,m.radius))

    def test_every_stage_has_input_only_normal_mode_escape(self):
        for stage in range(3):
            with self.subTest(stage=stage):
                w,r=playthrough(stage=stage)
                self.assertEqual(w.result,'clear')
                self.assertFalse(w.practice)
                self.assertGreater(w.hp,0)
                self.assertEqual(w.boarded,w.required_bodies)

    def test_intro_requires_actual_ram_impact_not_just_boarding(self):
        w=Arena(stage=0);w.boarded.add('ram')
        w.fire((700,390),(868,390),'player','gun',True)
        w.update(1)
        self.assertFalse(w.gate_open)

    def test_laser_warning_is_safe_but_active_hurts_core_and_machine(self):
        w=Arena(stage=2);w.x,w.y=622,490;w.time=1.9
        w.update(.05);self.assertEqual(w.hp,5)
        w.time=2.5;w.update(.05);self.assertEqual(w.hp,4)
        w.board(w.machines['ram']);m=w.machines['ram'];m.x,m.y=622,490
        w.time=2.6;w.update(.05);self.assertEqual(m.hp,3)

    def test_laser_cycles_and_only_exists_in_final_room(self):
        w=Arena(stage=2)
        for t,state in [(1,'off'),(1.9,'warning'),(2.8,'active'),(3.5,'off'),(6.8,'active')]:
            w.time=t;self.assertEqual(w.laser_state,state)
        w=Arena(stage=0);w.time=2.8;self.assertEqual(w.laser_state,'off')

    def test_no_core_only_exit_in_any_stage(self):
        for stage in range(3):
            w=Arena(stage=stage);w.x,w.y=1026,390
            w.update(.01);self.assertIsNone(w.result)

if __name__=='__main__':unittest.main()
