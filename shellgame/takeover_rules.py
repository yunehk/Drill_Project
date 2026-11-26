"""Campaign abilities and mechanisms. No rendering, files, or SDL here."""
import math
from .geometry import unit, distance, clear_at, clear_path, circle_rect, clamp
from .takeover_entities import Bomb, Drone, Crate, Guardian
from .takeover_levels import WEIGHTS

class CampaignRules:
    def init_devices(self):
        self.bombs=[]
        self.drones=[Drone(x,y,armor,mode,anchor=(x,y),phase=i*2)
                     for i,(x,y,armor,mode) in enumerate(self.level.drones)]
        self.crates=[Crate(*entry) for entry in self.level.crates]
        self.relay_on=set()
        self.boss=Guardian() if self.level.boss else None
        self.magnet_active=False
        self.beams=[]
        self.web_line=None
        self.web_flash=0.
        self.detonations=[]
        self.stats.update({'bombs':0,'kills':0,'relays':0,'bodies_lost':0})
        self.used_practice=self.practice
        for kind in self.level.empty:
            self.machines[kind].state='empty'

    @property
    def plate_weights(self):
        values=[]
        for px,py,minimum in self.level.plates:
            total=sum(WEIGHTS[m.kind] for m in self.machines.values()
                      if m.state!='wreck' and distance(m.pos,(px,py))<=34)
            total+=sum(c.weight for c in self.crates if c.alive and distance(c.pos,(px,py))<=34)
            values.append(total)
        return values

    @property
    def power_ready(self):
        return (all(w>=p[2] for w,p in zip(self.plate_weights,self.level.plates))
                and len(self.relay_on)==len(self.level.relays))

    @property
    def hazards_disabled(self):
        return self.level.boss and bool(self.level.relays) and len(self.relay_on)==len(self.level.relays)

    def door_is_open(self,index):
        x,y,w,h,plate=self.level.doors[index]
        if self.plate_weights[plate]>=self.level.plates[plate][2]:return True
        # A released pressure plate must never close a wall through an actor.
        entities=[(self.x,self.y,self.radius)]+[(m.x,m.y,m.radius) for m in self.machines.values() if m.state!='wreck']
        return any(circle_rect(px,py,r,(x,y,w,h)) for px,py,r in entities)

    def navigation_walls(self,kind='core'):
        return self.walls+(list(self.level.pits) if kind not in ('spider','projectile') else [])

    @property
    def campaign_objective(self):
        if self.level.goal=='boss':
            if self.boss.hp<=0:return 'EXIT','관리자 정지! 본체로 오른쪽 출구를 통과하세요'
            if self.boss.exposed>0:return 'HIT',f'방패 해제 {self.boss.exposed:.1f}초 · 예약 폭격을 명중시키세요'
            return 'BOSS','돌진 또는 전지로 방패 해제 → 예약 폭격 / 웹 릴레이로 방해 장치 정지'
        if self.level.goal=='purge':
            alive=sum(d.hp>0 for d in self.drones)
            if alive:return 'COMBO',f'예약 폭격 + 자석 연계 · 움직이는 경비 드론 {alive}기 남음'
        if self.level.powered_gate and not self.power_ready:
            plate_missing=sum(w<p[2] for w,p in zip(self.plate_weights,self.level.plates))
            relay_missing=len(self.level.relays)-len(self.relay_on)
            return 'POWER',f'전원 연결 · 미충족 압력판 {plate_missing}개 / 꺼진 웹 릴레이 {relay_missing}개'
        if not self.gate_open:return 'GATE','포격형으로 주황 차단벽을 조준하고 5초 뒤 폭격'
        return 'EXIT','E로 하차 → 본체로 오른쪽 좁은 틈 → 초록 출구'

    def bomb_target(self,aim):
        ux,uy=unit(aim[0]-self.x,aim[1]-self.y)
        length=min(620,distance(self.pos,aim))
        return clamp(self.x+ux*length,60,1040),clamp(self.y+uy*length,160,634)

    def reserve_bomb(self,start,target,team='player',delay=5.,radius=108.):
        # One outstanding player order per artillery chassis. Switching bodies
        # never creates extra orders or cancels an existing reservation.
        if team=='player' and any(b.team=='player' for b in self.bombs):
            self.message='폭격 예약이 이미 진행 중입니다. 다른 몸으로 연계하세요';self.message_time=2
            return False
        if team=='player':target=self.bomb_target(target)
        self.bombs.append(Bomb(*target,delay,team,'gun',radius,delay,math.ceil(delay)))
        self.emit('reserve',*target,message='5초 뒤 폭격! 내려도 유지됩니다. 자석으로 적을 모으거나 안전지대로 이동하세요' if team=='player' else None)
        if team=='player':self.stats['shots']+=1;self.stats['bombs']+=1
        return True

    def perform_ability(self,m,c):
        if m.kind=='ram':
            m.direction=unit(c.aim[0]-m.x,c.aim[1]-m.y)
            m.state,m.timer,m.cooldown='dash',.56,1.45
            self.emit('throw',message='돌진! 방향 변경 불가 · 내리면 남은 돌진을 계속합니다')
        elif m.kind=='gun':
            if self.reserve_bomb(m.pos,c.aim):m.cooldown=5.4
        elif m.kind=='spider':
            # Web relays are persistent, readable puzzle state.
            for i,p in enumerate(self.level.relays):
                if distance(c.aim,p)<42 and distance(m.pos,p)<=350 and clear_path(m.pos,p,1,self.walls):
                    self.relay_on.add(i);m.cooldown=.4
                    self.web_line=(m.pos,p);self.web_flash=.45
                    self.stats['relays']=len(self.relay_on)
                    self.emit('relay',*p,message='웹 릴레이 연결! 이 전원은 몸을 바꿔도 유지됩니다')
                    return
            for p in self.level.anchors:
                if distance(c.aim,p)<42 and distance(m.pos,p)<=365 and clear_path(m.pos,p,m.radius,self.walls):
                    m.direction=unit(p[0]-m.x,p[1]-m.y);m.target=p
                    m.timer=distance(m.pos,p)/650+.04;m.state='grapple';m.cooldown=.8
                    self.web_line=(m.pos,p);self.web_flash=.5
                    self.emit('web',*p);return
            for enemy in self.drones:
                if enemy.hp>0 and distance(c.aim,enemy.pos)<42 and distance(m.pos,enemy.pos)<330 and clear_path(m.pos,enemy.pos,1,self.walls):
                    enemy.stun=3.2;m.cooldown=.7;self.web_line=(m.pos,enemy.pos);self.web_flash=.4
                    self.emit('web',*enemy.pos);return
            self.message='거미형: 고리·초록 릴레이·경비 드론을 조준하세요';self.message_time=2

    def magnetic_field(self,m,aim,repel=False):
        direction=unit(aim[0]-m.x,aim[1]-m.y)
        candidates=[d for d in self.drones if d.hp>0 and not d.armor]
        candidates += [c for c in self.crates if c.alive]
        candidates += [a for a in self.machines.values() if a is not m and a.state in ('empty','stun')]
        for obj in candidates:
            dist=distance(m.pos,obj.pos)
            if not 35<dist<290:continue
            ux,uy=unit(obj.x-m.x,obj.y-m.y)
            if ux*direction[0]+uy*direction[1]<.57:continue
            if not clear_path(m.pos,obj.pos,2,self.walls):continue
            self.beams.append((m.pos,obj.pos))
            if repel:
                dx,dy=ux*265,uy*265
                if hasattr(obj,'vx'):obj.vx,obj.vy=dx,dy
                else:self.move(obj,ux*48,uy*48,obj.radius)
            elif dist>m.radius+obj.radius+10:
                mass=WEIGHTS.get(getattr(obj,'kind',''),getattr(obj,'weight',1)) or 1
                self.move(obj,-ux*220/max(1,mass)*self.step_dt,-uy*220/max(1,mass)*self.step_dt,obj.radius)
            if not repel and hasattr(obj,'stun'):obj.stun=max(obj.stun,.08)

    def ram_contacts(self,m):
        hit=False
        if self.level.gate_weapon=='ram' and not self.gate_open:
            from .takeover import GATE
            if circle_rect(m.x+m.direction[0]*8,m.y+m.direction[1]*8,m.radius,GATE):
                self.gate_open=True;hit=True
                self.emit('break',868,390,message='균열벽 돌파! 본체로 좁은 틈을 지나세요')
        for crate in self.crates:
            if crate.alive and distance(m.pos,crate.pos)<m.radius+crate.radius+5:
                crate.vx,crate.vy=m.direction[0]*400,m.direction[1]*400
                hit=True
        for d in self.drones:
            if d.hp>0 and d.stun<=0 and distance(m.pos,d.pos)<m.radius+d.radius+5:
                if d.armor:d.armor=False;d.stun=3.5
                else:d.hp=0;self.stats['kills']+=1
                self.emit('impact',*d.pos);hit=True
        if self.boss and self.boss.hp>0 and distance(m.pos,self.boss.pos)<m.radius+self.boss.radius+5:
            self.expose_boss();hit=True
        return hit

    def expose_boss(self):
        if self.boss.exposed<=0:
            self.boss.exposed=12.
            self.emit('impact',*self.boss.pos,message='관리자 방패 해제! 12초 안에 예약 폭격을 명중시키세요')

    def detonate(self,b):
        self.emit('blast',b.x,b.y)
        self.detonations.append([b.x,b.y,b.radius,.65,b.team])
        if b.team=='enemy':
            if distance(self.pos,b.pos)<b.radius+self.radius:self.hurt()
            return
        # Every bomb is useful, but not every target is expendable.
        for d in self.drones:
            if d.hp>0 and distance(d.pos,b.pos)<b.radius+d.radius:
                if d.armor:self.emit('block',*d.pos)
                else:d.hp=0;self.stats['kills']+=1;self.emit('break',*d.pos)
        for m in self.machines.values():
            if m.state=='wreck' or distance(m.pos,b.pos)>=b.radius+m.radius:continue
            if self.host==m.kind:self.hurt()
            elif m.state in ('empty','stun','dash_empty','grapple_empty') or not m.armor:
                m.hp=0;m.state='wreck';m.respawn=5.;self.stats['bodies_lost']+=1
                self.emit('break',*m.pos,message='남겨 둔 기체가 폭격에 파괴됐습니다. Z로 되돌릴 수 있습니다')
            else:self.emit('block',*m.pos)
        if self.host is None and distance(self.pos,b.pos)<b.radius+11:self.hurt()
        for crate in self.crates:
            if crate.alive and distance(crate.pos,b.pos)<b.radius+crate.radius:crate.alive=False
        if self.boss and self.boss.hp>0 and distance(self.boss.pos,b.pos)<b.radius+self.boss.radius:
            if self.boss.exposed>0:
                self.boss.hp-=1;self.boss.exposed=0;self.boss.flash=.6
                self.emit('break',*self.boss.pos,message=f'관리자 손상! 남은 장갑 {self.boss.hp}')
                if self.boss.hp<=0:self.gate_open=True;self.emit('key',*self.boss.pos,message='정원 정지. 이제 껍질을 내려놓고 출구로 향하세요')
            else:self.emit('block',*self.boss.pos,message='관리자 방패가 닫혀 있습니다. 돌진 또는 전지로 먼저 여세요')
        if self.level.goal not in ('purge','boss') and not self.gate_open:
            from .takeover import GATE
            if self.level.gate_weapon=='gun' and circle_rect(b.x,b.y,b.radius,GATE):
                if self.level.powered_gate and not self.power_ready:
                    self.emit('block',868,390,message='출구 전원이 부족합니다. 압력판과 웹 릴레이 상태를 확인하세요')
                else:
                    self.gate_open=True
                    self.emit('break',868,390,message='차단벽 파괴! 본체로 좁은 틈을 지나 탈출하세요')

    def campaign_step(self,dt,c):
        self.step_dt=dt;self.beams=[];self.magnet_active=False
        self.web_flash=max(0,self.web_flash-dt)
        self.used_practice |= self.practice
        for burst in self.detonations:burst[3]-=dt
        self.detonations=[b for b in self.detonations if b[3]>0]
        if self.host=='mag':
            m=self.machines['mag']
            if c.held or c.attack:
                self.magnet_active=True;self.magnetic_field(m,c.aim)
            if c.secondary and m.cooldown<=0:
                self.magnetic_field(m,c.aim,True);m.cooldown=.8;self.emit('magnet',*m.pos)
        for m in self.machines.values():
            if m.state not in ('dash_empty','grapple_empty'):continue
            m.timer-=dt
            speed=820 if m.state=='dash_empty' else 650
            ok=self.move(m,m.direction[0]*speed*dt,m.direction[1]*speed*dt,m.radius)
            if m.kind=='ram' and self.ram_contacts(m):m.timer=0
            if not ok or m.timer<=0:m.state='empty'
        for d in self.drones:
            if d.hp<=0:continue
            d.stun=max(0,d.stun-dt);d.cooldown-=dt;d.phase+=dt
            if abs(d.vx)+abs(d.vy)>1:
                self.move(d,d.vx*dt,d.vy*dt,d.radius);d.vx*=max(0,1-3*dt);d.vy*=max(0,1-3*dt)
            if d.stun<=0:
                target=(d.anchor[0]+math.cos(d.phase*1.3)*42,d.anchor[1]+math.sin(d.phase*1.3)*32)
                if d.mode=='seek':target=self.pos
                speed=68
                threats=[b for b in self.bombs if b.team=='player' and b.timer<1.8 and distance(d.pos,b.pos)<b.radius+45]
                if threats:
                    bomb=min(threats,key=lambda b:b.timer)
                    ax,ay=unit(d.x-bomb.x,d.y-bomb.y)
                    target=(d.x+ax*160,d.y+ay*160);speed=88
                ux,uy=unit(target[0]-d.x,target[1]-d.y)
                if distance(target,d.pos)>3:self.move(d,ux*speed*dt,uy*speed*dt,d.radius)
                if distance(self.pos,d.pos)<self.radius+d.radius:self.hurt()
                if d.cooldown<=0:
                    self.fire(d.pos,self.pos,'enemy','drone');d.cooldown=4.2
        for crate in self.crates:
            if not crate.alive:continue
            if abs(crate.vx)+abs(crate.vy)>1:
                self.move(crate,crate.vx*dt,crate.vy*dt,crate.radius)
                crate.vx*=max(0,1-2*dt);crate.vy*=max(0,1-2*dt)
            if crate.conductive and self.boss and self.boss.hp>0 and distance(crate.pos,self.boss.pos)<85:
                crate.alive=False;self.expose_boss();self.emit('relay',*crate.pos)
        for b in self.bombs[:]:
            b.timer-=dt
            if math.ceil(b.timer)<b.tick:
                b.tick=math.ceil(b.timer)
                if b.team=='player' and b.tick>0:self.events.append(('tick',b.x,b.y))
            if b.timer<=0:self.bombs.remove(b);self.detonate(b)
        if self.level.goal=='purge' and self.drones and all(d.hp<=0 for d in self.drones) and not self.gate_open:
            self.gate_open=True;self.emit('key',868,390,message='경비 드론 정리! 출구가 열렸습니다')
        if self.boss and self.boss.hp>0:
            boss=self.boss;boss.exposed=max(0,boss.exposed-dt);boss.flash=max(0,boss.flash-dt);boss.cooldown-=dt
            if boss.cooldown<=0:
                self.reserve_bomb(boss.pos,self.pos,'enemy',2.8,65)
                if boss.hp<3:
                    # A second delayed target makes positioning matter, with
                    # generous warning rather than a denser bullet curtain.
                    p=(clamp(self.x+90,80,1030),clamp(self.y+60,180,620))
                    self.reserve_bomb(boss.pos,p,'enemy',3.5,60)
                boss.cooldown=5.5
