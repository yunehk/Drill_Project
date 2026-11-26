"""Deterministic QA solutions using only public movement/ability inputs.

No positions, health, enemy timers, plate states or relay states are modified.
These are automated test inputs, not human play footage.
"""
from shellgame.takeover import Arena,Input
from shellgame.geometry import distance

class Driver:
    def __init__(self,stage,observer=None):
        self.w=Arena(stage=stage);self.frames=[];self.observer=observer
    def tick(self,c=None):
        c=c or Input();self.w.update(1/60,c);self.frames.append(c)
        if self.observer:self.observer(self.w,c)
        if self.w.result=='dead':raise AssertionError(('Died',self.w.stage_index,self.w.time,self.w.pos,self.w.log[-10:]))
    def wait(self,seconds,c=None):
        c=c or Input()
        for _ in range(max(1,round(seconds*60))):
            self.tick(c);c=Input(c.move,c.aim,held=c.held)
            if self.w.result:return
    def until(self,predicate,timeout=12,c=None):
        for _ in range(round(timeout*60)):
            if predicate():return
            self.tick(c)
        raise AssertionError(('Timed out',self.w.stage_index,self.w.time,self.w.pos,self.w.objective))
    def walk(self,target,aim=None,held=False):
        for _ in range(1800):
            if distance(self.w.pos,target)<5 or self.w.result=='clear':return
            dx,dy=target[0]-self.w.x,target[1]-self.w.y
            move=((1 if dx>0 else -1) if abs(dx)>3 else 0,(1 if dy>0 else -1) if abs(dy)>3 else 0)
            self.tick(Input(move,aim or target,held=held))
        raise AssertionError(('Blocked',self.w.stage_index,self.w.pos,target,self.w.host))
    def board(self,kind):
        self.walk(self.w.machines[kind].pos)
        if self.w.interact_cd>0:self.wait(self.w.interact_cd+.02)
        self.tick(Input(interact=True))
        assert self.w.host==kind,('Board',kind,self.w.pos,self.w.candidate())
        self.wait(.35)
    def leave(self,direction=(0,-1)):
        if self.w.interact_cd>0:self.wait(self.w.interact_cd+.02)
        self.tick(Input(move=direction,interact=True))
        assert self.w.host is None,('Cannot eject',self.w.pos)
        self.wait(.36)
    def attack(self,target):
        m=self.w.machines[self.w.host]
        if m.cooldown>0:self.wait(m.cooldown+.02)
        self.tick(Input(aim=target,attack=True))
    def exit(self):
        if self.w.host:self.leave((1,0))
        self.walk((805,388));self.walk((930,388));self.walk((1027,388))
        assert self.w.result=='clear',('Exit',self.w.stage_index,self.w.pos,self.w.objective,self.w.boarded)
    def dodge_and_take_ram(self,final=False):
        self.wait(2.3);self.wait(.18,Input((0,-1),dodge=True));self.wait(.5)
        if final:self.walk((400,455));self.walk((550,455))
        else:self.walk((225,365))
        m=self.w.machines['ram']
        # Walk to the chassis only after it has stopped. Intro pillar locations
        # differ, so the final short approach follows actual collision results.
        self.board('ram')
    def bombard_gate(self,safe=None):
        self.attack((868,390))
        if safe:self.walk(safe)
        self.until(lambda:self.w.gate_open,timeout=7)

def run_stage(stage,observer=None):
    d=Driver(stage,observer);w=d.w
    if stage==0:
        d.dodge_and_take_ram();d.walk((650,390));d.attack((868,390));d.wait(.6)
        d.walk((930,388));d.leave((1,0));d.walk((1027,388))
    elif stage in (1,2):
        d.dodge_and_take_ram(stage==2)
        if stage==2:d.walk((550,455))
        d.walk((385,455));d.attack(w.machines['gun'].pos);d.wait(.6)
        assert w.machines['gun'].state=='stun'
        d.leave((1,0));d.board('gun')
        d.attack((868,390));d.leave((0,-1))
        d.walk((760,550) if stage==2 else (760,230))
        d.until(lambda:w.gate_open,timeout=7);d.exit()
    elif stage==3:
        d.board('gun');d.attack((750,390));d.leave((1,0));d.board('mag')
        d.until(lambda:any(b.team=='player' and b.timer<.85 for b in w.bombs),timeout=6,c=Input(aim=(800,390),held=True))
        d.walk((610,390),aim=(800,390),held=True)
        d.until(lambda:w.gate_open,timeout=3,c=Input(aim=(800,390),held=True))
        d.exit()
    elif stage==4:
        d.dodge_and_take_ram();d.attack(w.machines['gun'].pos);d.wait(.6)
        assert w.machines['gun'].state=='stun'
        d.walk((420,535));d.leave((0,-1));d.board('gun')
        assert w.power_ready
        d.bombard_gate((720,460));d.exit()
    elif stage==5:
        d.board('spider');d.attack((740,390));d.wait(.65)
        d.attack((730,235));d.walk((700,390));d.leave((0,1))
        d.board('gun');assert w.power_ready
        d.bombard_gate((715,500));d.exit()
    elif stage==6:
        d.board('ram');d.walk((410,535));d.leave((0,-1))
        d.board('gun');d.walk((690,390));d.walk((755,245));d.leave((0,1))
        d.board('spider');d.attack((735,560));d.leave((0,-1))
        d.board('gun');assert w.power_ready
        d.attack((868,390));d.leave((0,1));d.until(lambda:w.gate_open,timeout=7);d.exit()
    else:
        d.board('spider');d.walk((480,390));d.attack((470,200));d.wait(.45)
        d.attack((740,565));d.leave((0,-1));assert w.hazards_disabled
        for _ in range(3):
            d.board('ram');d.attack(w.boss.pos);d.wait(.6)
            assert w.boss.exposed>0
            d.walk((570,390))
            d.leave((-1,1));d.board('gun');d.attack(w.boss.pos)
            # Keep moving in a generous rectangle while delayed enemy strikes
            # land at previously occupied positions. No damage immunity used.
            for point in ((380,540),(540,540),(540,330),(380,330)):
                if not any(b.team=='player' for b in w.bombs):break
                d.walk(point)
            d.until(lambda:not any(b.team=='player' for b in w.bombs),timeout=7)
            if w.boss.hp>0:d.leave((1,0))
        assert w.boss.hp==0
        d.exit()
    assert w.result=='clear',(stage,w.pos,w.objective)
    assert not w.practice and w.hp>0
    return w,d.frames

if __name__=='__main__':
    for stage in range(8):
        w,frames=run_stage(stage)
        print('CLEAR',stage+1,round(w.time,2),'HP',w.hp,'hits',w.stats['hits'],'inputs',len(frames))
