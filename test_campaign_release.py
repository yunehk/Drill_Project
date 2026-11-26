import tempfile
import unittest
from pathlib import Path
from shellgame.takeover import Arena,Input
from shellgame.takeover_entities import Bomb
from shellgame.takeover_progress import Progress,Undo
from tools.playthrough_campaign import run_stage

class AbilityTests(unittest.TestCase):
    def test_reservation_waits_five_seconds_and_survives_body_exit(self):
        w=Arena(stage=3);w.board(w.machines['gun']);w.machines['gun'].cooldown=0
        w.update(.01,Input(aim=(760,390),attack=True))
        self.assertEqual(len(w.bombs),1);self.assertGreater(w.bombs[0].timer,4.9)
        w.update(.4);w.update(.01,Input((1,0),interact=True))
        self.assertIsNone(w.host);self.assertEqual(len(w.bombs),1)
        w.update(3.5);self.assertEqual(len(w.bombs),1)
        w.update(1.2);self.assertEqual(len(w.bombs),0)

    def test_only_one_player_reservation_is_outstanding(self):
        w=Arena(stage=3)
        self.assertTrue(w.reserve_bomb(w.pos,(750,390)))
        self.assertFalse(w.reserve_bomb(w.pos,(800,390)))
        self.assertEqual(len(w.bombs),1)

    def test_bomb_destroys_empty_essential_body_and_closes_power(self):
        w=Arena(stage=4);m=w.machines['ram'];m.state='empty';m.x,m.y=420,535
        self.assertTrue(w.power_ready)
        w.detonate(Bomb(420,535))
        self.assertEqual(m.state,'wreck');self.assertFalse(w.power_ready)
        w.update(6);self.assertEqual(m.state,'wreck')

    def test_powered_gate_rejects_blast_until_real_plate_is_occupied(self):
        w=Arena(stage=4);w.detonate(Bomb(868,390));self.assertFalse(w.gate_open)
        m=w.machines['ram'];m.state='empty';m.x,m.y=420,535
        w.detonate(Bomb(868,390));self.assertTrue(w.gate_open)

    def test_living_core_has_no_plate_weight(self):
        w=Arena(stage=4);w.x,w.y=420,535
        self.assertEqual(w.plate_weights,[0]);self.assertFalse(w.power_ready)

    def test_gun_can_replace_magnet_on_second_plate(self):
        w=Arena(stage=6)
        ram=w.machines['ram'];ram.x,ram.y=410,535
        gun=w.machines['gun'];gun.x,gun.y=755,245
        w.relay_on.add(0);self.assertTrue(w.power_ready)
        gun.x=700;self.assertFalse(w.power_ready)

    def test_magnet_holds_nearby_enemy_but_not_armored_enemy(self):
        w=Arena(stage=3);w.board(w.machines['mag'])
        a,b=w.drones;a.x,a.y=705,390;b.x,b.y=780,390;b.armor=True
        w.update(.4,Input(aim=(850,390),held=True))
        self.assertGreater(a.stun,0);self.assertLess(a.x,710)
        self.assertGreater(b.x,760);self.assertTrue(b.armor)

    def test_magnet_respects_walls(self):
        w=Arena(stage=3);w.board(w.machines['mag']);m=w.machines['mag']
        m.x,m.y=650,230;w.x,w.y=m.pos
        a=w.drones[0];a.x,a.y=420,230;a.anchor=a.pos;a.stun=5
        before=a.pos;w.update(.4,Input(aim=(400,230),held=True))
        self.assertEqual(a.pos,before)

    def test_drone_evades_unattended_reserved_blast(self):
        w=Arena(stage=3);d=w.drones[0];d.x,d.y=780,350;d.anchor=d.pos
        w.bombs=[Bomb(750,390,1.7)]
        before=((d.x-750)**2+(d.y-390)**2)**.5;w.update(.7)
        after=((d.x-750)**2+(d.y-390)**2)**.5
        self.assertGreater(after,before+30)

    def test_spider_crosses_pit_but_cannot_eject_core_over_it(self):
        w=Arena(stage=5)
        self.assertFalse(w.allowed(600,390,11,'core'))
        self.assertTrue(w.allowed(600,390,22,'spider'))
        m=w.machines['spider'];m.x,m.y=600,390;w.board(m)
        self.assertFalse(w.eject((1,0)));self.assertEqual(w.host,'spider')

    def test_web_relay_remains_on_after_ejection(self):
        w=Arena(stage=5);m=w.machines['spider'];m.x,m.y=730,390
        w.board(m);m.cooldown=0
        w.update(.01,Input(aim=(730,235),attack=True));self.assertIn(0,w.relay_on)
        w.update(.4);w.update(.01,Input((1,0),interact=True))
        self.assertIn(0,w.relay_on);self.assertTrue(w.power_ready)

    def test_ejected_ram_completes_last_command_and_breaks_wall(self):
        w=Arena(stage=0);m=w.machines['ram'];m.x,m.y=720,390
        w.board(m);m.cooldown=0;w.interact_cd=0
        w.update(.01,Input(aim=(950,390),attack=True))
        w.interact_cd=0;w.update(.01,Input((0,1),interact=True))
        self.assertEqual(m.state,'dash_empty');self.assertIsNone(w.host)
        w.update(.5);self.assertTrue(w.gate_open)

    def test_guardian_shield_requires_exposure_before_bomb_damage(self):
        w=Arena(stage=7);w.detonate(Bomb(*w.boss.pos));self.assertEqual(w.boss.hp,3)
        w.expose_boss();w.detonate(Bomb(*w.boss.pos))
        self.assertEqual(w.boss.hp,2);self.assertEqual(w.boss.exposed,0)
        w.detonate(Bomb(*w.boss.pos));self.assertEqual(w.boss.hp,2)

    def test_safety_relays_disable_both_final_room_hazards(self):
        w=Arena(stage=7);w.time=2.8;self.assertEqual(w.laser_state,'active')
        w.relay_on={0,1};self.assertEqual(w.laser_state,'off');self.assertTrue(w.hazards_disabled)

    def test_undo_restores_placement_and_destroyed_bodies(self):
        w=Arena(stage=4);m=w.machines['ram'];m.x,m.y=420,535;m.state='empty'
        history=Undo();history.take(w);w.detonate(Bomb(420,535));restored=history.restore()
        self.assertEqual(restored.machines['ram'].state,'empty');self.assertTrue(restored.power_ready)
        self.assertEqual(w.machines['ram'].state,'wreck')

    def test_magnetic_battery_is_an_alternative_guardian_shield_solution(self):
        from tools.playthrough_campaign import Driver
        d=Driver(7);w=d.w
        d.board('mag');d.walk((420,210))
        d.tick(Input(aim=(570,285),secondary=True));d.wait(2)
        self.assertGreater(w.boss.exposed,0)
        self.assertTrue(any(not crate.alive for crate in w.crates))

    def test_upper_wall_hit_does_not_open_unhit_middle(self):
        w=Arena(stage=1);w.detonate(Bomb(868,610))
        self.assertTrue(w.gate_open);self.assertTrue(w.broken_gate)
        self.assertTrue(w.allowed(868,610,11))
        self.assertFalse(w.allowed(868,390,11))

    def test_repeated_blasts_can_destroy_all_remaining_wall_parts(self):
        w=Arena(stage=1)
        for y in (610,390,180):w.detonate(Bomb(868,y))
        self.assertEqual(len(w.broken_gate),12)
        self.assertEqual(w.gate_walls,[]);self.assertEqual(w.gate_panels,[])

    def test_unpowered_wall_loses_no_segments(self):
        w=Arena(stage=4);w.detonate(Bomb(868,610))
        self.assertEqual(w.broken_gate,set());self.assertFalse(w.gate_open)

    def test_undo_restores_wall_shape_and_collision(self):
        w=Arena(stage=1);history=Undo();history.take(w)
        w.detonate(Bomb(868,610));restored=history.restore()
        self.assertTrue(w.allowed(868,610,11))
        self.assertFalse(restored.allowed(868,610,11))
        self.assertEqual(restored.broken_gate,set())

class ProgressTests(unittest.TestCase):
    def test_corrupt_save_is_ignored_and_normal_clear_is_saved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'save.json';path.write_text('{broken',encoding='utf-8')
            p=Progress(path);self.assertEqual(p.highest,2)
            w=Arena(stage=3);w.result='clear';w.time=15
            self.assertTrue(p.complete(w));q=Progress(path)
            self.assertEqual(q.highest,4);self.assertEqual(q.records[3]['stars'],3)

    def test_practice_used_then_disabled_never_saves_normal_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Progress(Path(tmp)/'save.json');w=Arena(True,3)
            w.practice=False;w.result='clear';w.time=15
            self.assertFalse(p.complete(w));self.assertEqual(p.records,{})

    def test_progress_tracks_best_preservation_not_only_speed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Progress(Path(tmp)/'save.json');w=Arena(stage=3)
            w.result='clear';w.time=25;p.complete(w)
            w.time=20;w.hp=3;w.stats['bodies_lost']=1;p.complete(w)
            self.assertEqual(p.records[3],{'time':20,'stars':3})

class FullCampaignTests(unittest.TestCase):
    def test_all_eight_stages_finish_in_normal_mode(self):
        for stage in range(8):
            with self.subTest(stage=stage):
                w,frames=run_stage(stage)
                self.assertEqual(w.result,'clear');self.assertFalse(w.used_practice)
                self.assertGreater(w.hp,0);self.assertTrue(w.required_bodies<=w.boarded)

if __name__=='__main__':unittest.main()
