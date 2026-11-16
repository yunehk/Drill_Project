"""Deterministic body-takeover arena. No rendering or SDL dependency.

All inputs, including QA replays, go through Arena.update/Input. Fixed substeps
keep fast charges and shells from crossing walls between collision checks.
"""
from dataclasses import dataclass, field
import math
import random
from .geometry import unit, distance, clear_at, clear_path, circle_rect
from .takeover_levels import STAGES

W, H = 1100, 780
BOUNDS = (48, 148, 1004, 498)
SOLIDS = [(105, 310, 34, 160), (970, 148, 25, 218), (970, 410, 25, 236)]
GATE = (854, 148, 28, 498)
GATE_OPEN = [(854, 148, 28, 174), (854, 454, 28, 192)]
SPAWNS = {'ram': (580, 390), 'gun': (745, 505)}

@dataclass
class Input:
    move: tuple = (0, 0)
    aim: tuple = (800, 400)
    attack: bool = False
    interact: bool = False
    dodge: bool = False

@dataclass
class Machine:
    kind: str
    x: float
    y: float
    state: str = 'idle'
    timer: float = 1.2
    direction: tuple = (1., 0.)
    hp: int = 4
    cooldown: float = 0.
    invuln: float = 0.
    radius: float = 25.
    armor: bool = True
    respawn: float = 0.

    @property
    def pos(self): return self.x, self.y

@dataclass
class Shot:
    x: float
    y: float
    vx: float
    vy: float
    team: str
    owner: str
    radius: float = 6.
    life: float = 4.
    explosive: bool = False
    target: tuple = None
    age: float = 0.
    flight: float = 0.
    start: tuple = None

@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    color: tuple

class Arena:
    def __init__(self, practice=False, stage=2):
        if stage not in range(len(STAGES)): raise ValueError("Invalid stage")
        self.stage_index = stage
        self.level = STAGES[stage]
        self.solids = list(self.level.solids)
        self.spawns = {kind:(x,y) for kind,x,y in self.level.spawns}
        self.required_bodies = set(self.spawns)
        self.x, self.y = 295., 390.
        self.hp = 5
        self.host = None
        self.machines = {k: Machine(k, *p) for k, p in self.spawns.items()}
        if 'gun' in self.machines: self.machines['gun'].timer = 4.0 if stage == 1 else 2.9
        self.time = 0.
        self.practice = practice
        self.result = None
        self.gate_open = False
        self.boarded = set()
        self.shots = []
        self.particles = []
        self.events = []
        self.log = []
        self.invuln = 0.
        self.dodge_cd = 0.
        self.dodge_time = 0.
        self.dodge_dir = (0., 0.)
        self.interact_cd = 0.
        self.shake = 0.
        self.flash = 0.
        self.message = '붉은 돌진 로봇을 벽으로 유도하세요'
        self.message_time = 4.
        self.turret_timer = self.level.turret_delay
        self.turret_aim = None
        self.stats = {'hits': 0, 'swaps': 0, 'shots': 0, 'dodges': 0}
        self.rng = random.Random(12)

    @property
    def pos(self): return self.x, self.y

    @property
    def radius(self): return 11. if self.host is None else 25.

    @property
    def walls(self): return self.solids + (GATE_OPEN if self.gate_open else [GATE])

    @property
    def laser_state(self):
        if not self.level.laser: return "off"
        phase = self.time % 4
        return "active" if 2.4 <= phase < 3.4 else "warning" if 1.8 <= phase < 2.4 else "off"

    @property
    def objective(self):
        if 'ram' not in self.boarded: return '01', '돌진을 벽으로 유도 → 기절한 몸에 E로 탑승'
        if self.level.gate_weapon == 'ram':
            if not self.gate_open: return '02', '돌진형으로 주황색 균열벽에 돌진'
            return '03', 'E로 하차 → 오른쪽 좁은 틈 → 초록 출구'
        if 'gun' not in self.boarded: return '02', '돌진으로 포격형의 장갑 파괴 → E로 갈아타기'
        if not self.gate_open: return '03', '포격형으로 오른쪽 주황색 차단벽을 포격'
        return '04', 'E로 하차 → 오른쪽 좁은 틈 → 초록 출구'

    def emit(self, name, x=None, y=None, message=None):
        p = (self.x if x is None else x, self.y if y is None else y)
        self.events.append((name, *p))
        self.log.append((round(self.time, 3), name, *p))
        if message:
            self.message, self.message_time = message, 3.
        if name in ('hurt', 'break', 'impact', 'equip', 'clear'):
            self.shake = max(self.shake, .22 if name != 'break' else .38)
        color = (75, 227, 210) if name in ('equip', 'shed', 'clear') else (241, 157, 65)
        for _ in range(18 if name in ('break', 'impact') else 9):
            a = self.rng.random()*math.tau
            speed = self.rng.uniform(30, 190)
            self.particles.append(Particle(*p, math.cos(a)*speed, math.sin(a)*speed,
                                           self.rng.uniform(.2, .65), color))

    def allowed(self, x, y, radius):
        bx, by, bw, bh = BOUNDS
        return (bx+radius <= x <= bx+bw-radius and by+radius <= y <= by+bh-radius
                and clear_at(x, y, radius, self.walls))

    def move(self, obj, dx, dy, radius):
        # Never more than 4px per sample, even for QA dt or charge movement.
        count = max(1, math.ceil(math.hypot(dx, dy)/4))
        ok = True
        for _ in range(count):
            nx, ny = obj.x+dx/count, obj.y+dy/count
            if self.allowed(nx, ny, radius): obj.x, obj.y = nx, ny
            else:
                ok = False
                if self.allowed(nx, obj.y, radius): obj.x = nx
                if self.allowed(obj.x, ny, radius): obj.y = ny
        return ok

    def candidate(self):
        candidates = [m for m in self.machines.values()
                      if m.state in ('stun', 'empty') and distance(self.pos, m.pos) <= 87
                      and clear_path(self.pos, m.pos, 11, self.walls)]
        return min(candidates, key=lambda m: distance(self.pos, m.pos), default=None)

    def board(self, machine):
        self.host = machine.kind
        self.x, self.y = machine.pos
        machine.state = 'piloted'
        machine.cooldown = max(machine.cooldown, .25)
        self.boarded.add(machine.kind)
        self.stats['swaps'] += 1
        self.dodge_time = 0
        self.interact_cd = .35
        self.emit('equip', message='몸 탈취! 마우스로 조준하고 Space / 클릭으로 공격')

    def eject(self, direction, destroyed=False):
        if not self.host: return False
        m = self.machines[self.host]
        ux, uy = unit(*direction)
        # Try requested direction first, then nearby alternatives. Never eject
        # through a wall, into a gate or outside the arena.
        base = math.atan2(uy, ux)
        for delta in (0, .5, -.5, 1., -1., math.pi):
            a = base+delta
            target = (m.x+math.cos(a)*46, m.y+math.sin(a)*46)
            if self.allowed(*target, 11) and clear_path(m.pos, target, 11, self.walls):
                self.x, self.y = target
                break
        else:
            self.x, self.y = m.pos
        m.state = 'wreck' if destroyed else 'empty'
        m.timer = 0
        m.respawn = 5.
        self.host = None
        self.interact_cd = .35
        self.dodge_time = 0
        self.emit('shed', message='본체로 탈출! 다른 몸에 접근해 E' if not destroyed
                  else '기체 파괴! 본체는 살아남았습니다. 5초 뒤 대체 기체 투입')
        return True

    def hurt(self):
        if self.result: return
        if self.host:
            m = self.machines[self.host]
            if m.invuln > 0: return
            m.invuln = .65
            if not self.practice: m.hp -= 1
            self.emit('hurt')
            if m.hp <= 0:
                self.emit('break', *m.pos)
                self.eject((0, -1), True)
                self.invuln = .55  # brief post-destruction protection, not dash immunity
        elif self.invuln <= 0:
            if not self.practice: self.hp -= 1
            self.invuln = 1.
            self.emit('hurt', message='피격! 공격 예고를 보고 이동하세요')
            if self.hp <= 0:
                self.result = 'dead'
                self.emit('dead')
        else: return
        self.stats['hits'] += 1
        self.flash = .12

    def stun(self, m, duration=5.):
        m.state, m.timer = 'stun', duration
        self.emit('impact', *m.pos, message='기절! 가까이 가서 E로 몸을 빼앗으세요')

    def fire(self, start, target, team, owner, explosive=False):
        ux, uy = unit(target[0]-start[0], target[1]-start[1])
        if explosive:
            # Physical landing location. Ground markers and curved rendering
            # show both the actual target and remaining flight time.
            dist = min(620, distance(start, target))
            end = (start[0]+ux*dist, start[1]+uy*dist)
            duration = max(.35, dist/520)
            self.shots.append(Shot(*start, 0, 0, team, owner, 8, duration,
                                   True, end, 0., duration, start))
        else:
            speed = 275
            self.shots.append(Shot(start[0]+ux*30, start[1]+uy*30,
                                   ux*speed, uy*speed, team, owner))
        self.emit('throw', *start)

    def explode(self, shot):
        x, y = shot.target
        self.emit('impact', x, y)
        if shot.team == 'player':
            if self.level.gate_weapon == 'gun' and not self.gate_open and circle_rect(x, y, 90, GATE):
                self.gate_open = True
                self.emit('break', 868, 390, '차단벽 파괴! 하차한 뒤 오른쪽 틈으로 탈출하세요')
            for m in self.machines.values():
                if m.kind != shot.owner and m.state not in ('wreck', 'piloted') and distance((x,y),m.pos) < 85:
                    self.stun(m, 6.)
        elif distance((x,y), self.pos) < 63+self.radius:
            self.hurt()

    def update(self, dt, controls=None):
        self.events = []
        if self.result: return
        controls = controls or Input()
        if dt <= 0: return
        steps = max(1, math.ceil(dt/(1/120)))
        for i in range(steps):
            self._step(dt/steps, Input(controls.move, controls.aim,
                controls.attack and i == 0, controls.interact and i == 0,
                controls.dodge and i == 0))
            if self.result: break

    def _step(self, dt, c):
        self.time += dt
        for name in ('invuln', 'dodge_cd', 'dodge_time', 'interact_cd', 'shake', 'flash', 'message_time'):
            setattr(self, name, max(0., getattr(self, name)-dt))
        for p in self.particles:
            p.x += p.vx*dt; p.y += p.vy*dt; p.life -= dt
        self.particles = [p for p in self.particles if p.life > 0]
        for m in self.machines.values():
            m.cooldown = max(0., m.cooldown-dt)
            m.invuln = max(0., m.invuln-dt)
        # One press cannot both eject and board. Actions target one host only.
        if c.interact and self.interact_cd <= 0:
            if self.host:
                direction = c.move if any(c.move) else (c.aim[0]-self.x,c.aim[1]-self.y)
                self.eject(direction)
            else:
                candidate = self.candidate()
                if candidate: self.board(candidate)
                else: self.emit('block', message='기절하거나 비어 있는 기체에 가까이 접근하세요')
        if self.host:
            m = self.machines[self.host]
            if c.attack and m.cooldown <= 0 and m.state != 'dash':
                m.direction = unit(c.aim[0]-m.x, c.aim[1]-m.y)
                if m.kind == 'ram':
                    m.state, m.timer, m.cooldown = 'dash', .56, 1.45
                    self.emit('throw', message='돌진! 방향 변경 불가 · 피격 가능')
                else:
                    self.fire(m.pos, c.aim, 'player', 'gun', True)
                    m.cooldown = 1.15
                    self.stats['shots'] += 1
            if m.state == 'dash':
                m.timer -= dt
                ok = self.move(m, m.direction[0]*820*dt, m.direction[1]*820*dt, m.radius)
                if (self.level.gate_weapon == 'ram' and not self.gate_open and
                    circle_rect(m.x+m.direction[0]*8, m.y+m.direction[1]*8, m.radius, GATE)):
                    self.gate_open = True
                    self.emit('break',868,390,'균열벽 돌파! 하차한 뒤 작은 틈으로 탈출하세요')
                    m.timer = 0
                for other in self.machines.values():
                    if other is not m and other.state not in ('wreck', 'piloted', 'stun', 'empty') and distance(m.pos, other.pos) < 57:
                        other.armor = False
                        self.stun(other, 7.)
                        m.timer = 0
                if not ok or m.timer <= 0:
                    m.state = 'piloted'
                    if not ok:
                        m.cooldown = max(m.cooldown, .7)
                        self.emit('impact', *m.pos, message='충돌! 돌진은 도중에 꺾을 수 없습니다')
            else:
                speed = 175 if m.kind == 'ram' else 130
                ux, uy = unit(*c.move) if any(c.move) else (0,0)
                self.move(m, ux*speed*dt, uy*speed*dt, m.radius)
                if any(c.aim): m.direction = unit(c.aim[0]-m.x,c.aim[1]-m.y)
            self.x,self.y = m.pos
        else:
            if c.dodge and self.dodge_cd <= 0 and any(c.move):
                self.dodge_dir = unit(*c.move)
                self.dodge_time, self.dodge_cd = .15, .85
                self.stats['dodges'] += 1
                self.emit('shed')
            ux,uy = self.dodge_dir if self.dodge_time > 0 else (unit(*c.move) if any(c.move) else (0,0))
            self.move(self, ux*(570 if self.dodge_time>0 else 265)*dt,
                      uy*(570 if self.dodge_time>0 else 265)*dt, 11)
        self._enemies(dt)
        self._projectiles(dt)
        if self.laser_state == 'active' and circle_rect(self.x,self.y,self.radius,self.level.laser):
            self.hurt()
        if (self.gate_open and self.required_bodies <= self.boarded and self.host is None
                and self.x > 1015 and 350 < self.y < 430):
            self.result = 'clear'
            self.emit('clear', message='스테이지 클리어! Enter로 다음 방 / R로 재도전')

    def _enemies(self, dt):
        for m in self.machines.values():
            if self.host == m.kind: continue
            if m.state == 'wreck':
                m.respawn -= dt
                if m.respawn <= 0:
                    m.x,m.y = self.spawns[m.kind];m.hp=4;m.state='stun';m.timer=6.
                    self.emit('key', *m.pos, message='대체 기체가 도착했습니다. E로 탑승 가능')
                continue
            if m.state == 'empty': continue
            m.timer -= dt
            if m.state == 'stun':
                if m.timer <= 0:
                    m.state='idle';m.timer=1.5
                continue
            if m.kind == 'ram':
                if m.state == 'idle' and m.timer<=0:
                    m.state='windup';m.timer=.95
                    m.direction=unit(self.x-m.x,self.y-m.y)
                elif m.state == 'windup':
                    # Track early; lock the line during the final .35 seconds.
                    if m.timer>.35:m.direction=unit(self.x-m.x,self.y-m.y)
                    if m.timer<=0:
                        m.state='charge';m.timer=.95
                        self.emit('throw', *m.pos)
                elif m.state == 'charge':
                    ok=self.move(m,m.direction[0]*660*dt,m.direction[1]*660*dt,m.radius)
                    if distance(self.pos,m.pos)<self.radius+m.radius:self.hurt()
                    if not ok:self.stun(m,5.5)
                    elif m.timer<=0:m.state='idle';m.timer=1.4
            else:
                if m.state=='idle' and m.timer<=0:
                    m.state='windup';m.timer=1.0
                    m.direction=self.pos  # locked landing point, not direction
                elif m.state=='windup' and m.timer<=0:
                    self.fire(m.pos,m.direction,'enemy','gun',True)
                    m.state='idle';m.timer=3.4
        # Independent fixed turret keeps exchange windows meaningful.
        if not self.level.turret_interval: return
        self.turret_timer -= dt
        if self.turret_timer < .7 and self.turret_aim is None:self.turret_aim=self.pos
        if self.turret_timer <= 0:
            self.fire((705,185),self.turret_aim or self.pos,'enemy','turret')
            self.turret_timer=self.level.turret_interval;self.turret_aim=None

    def _projectiles(self, dt):
        alive=[]
        for s in self.shots:
            s.life -= dt;s.age+=dt
            if s.explosive:
                u=min(1,s.age/s.flight)
                s.x=s.start[0]+(s.target[0]-s.start[0])*u
                s.y=s.start[1]+(s.target[1]-s.start[1])*u
                if s.life<=0:self.explode(s)
                else:alive.append(s)
                continue
            s.x+=s.vx*dt;s.y+=s.vy*dt
            if s.life<=0 or not self.allowed(s.x,s.y,s.radius):continue
            # Empty bodies remain physical cover, as in the original shells.
            blocked=any(m.state in ('empty','stun') and distance((s.x,s.y),m.pos)<m.radius+s.radius
                        for m in self.machines.values())
            if blocked:
                self.emit('block',s.x,s.y);continue
            if s.team=='enemy' and distance((s.x,s.y),self.pos)<self.radius+s.radius:
                self.hurt();continue
            alive.append(s)
        self.shots=alive
