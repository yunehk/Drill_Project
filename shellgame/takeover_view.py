"""Campaign rendering: illustrated chassis, readable puzzle wiring and overlays."""
import ctypes
import importlib
import math
import unicodedata
import pico2d as p
from .drawing import BG,WHITE,MUTED,CYAN,ORANGE,RED,GOLD,GREEN
from .takeover import GATE,GATE_OPEN
from .takeover_levels import STAGES,WEIGHTS,BODY_NAMES

PURPLE=(174,143,246)
BLUE=(96,173,241)
rt=importlib.import_module('pico2d.pico2d')

def ring(d,x,y,r,c):d.circle(x,y,r,c,False)
def dotted(d,a,b,c,spacing=16):
    length=math.dist(a,b);n=max(1,int(length/spacing))
    for i in range(n):
        if i%2==0:
            d.line(a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n,
                   a[0]+(b[0]-a[0])*(i+1)/n,a[1]+(b[1]-a[1])*(i+1)/n,c)

def sprite(d,kind,x,y,size,angle=0,opacity=1):
    fn=getattr(d,'sprite',None)
    return bool(fn and fn(kind,x,y,size,angle,opacity))

def glow(d,x,y,r,color):
    fn=getattr(d,'glow',None)
    if fn:fn(x,y,r,color)
    else:ring(d,x,y,r,color)

def short(text,units=110):
    count=0;out=''
    for ch in text:
        count+=2 if unicodedata.east_asian_width(ch) in 'WF' else 1
        if count>units:return out+'…'
        out+=ch
    return out

def wrap(text,units=110):
    result=[];line='';count=0
    for ch in text:
        width=2 if unicodedata.east_asian_width(ch) in 'WF' else 1
        if count+width>units:result.append(line);line='';count=0
        line+=ch;count+=width
    if line:result.append(line)
    return result

def core(d,x,y,t,small=False):
    bob=math.sin(t*5)*1.2
    if not sprite(d,'core',x,y+bob,20 if small else 31):
        d.circle(x,y,9 if small else 12,CYAN)
        d.circle(x-4,y+3,2,BG);d.circle(x+4,y+3,2,BG)
    if not small:ring(d,x,y-1,15,(28,89,88))

def mech(d,m,active,t):
    x,y=m.pos
    if m.state=='wreck':
        if not sprite(d,m.kind,x,y,65,0,.25):d.rect(x-25,y-15,50,30,(45,47,52))
        d.line(x-20,y-20,x+20,y+20,RED);d.line(x-20,y+20,x+20,y-20,RED)
        if m.respawn>0:d.text(x-28,y-45,'파손',MUTED,14)
        return
    color=CYAN if active else GOLD if m.state in ('empty','stun') else RED
    if m.invuln>0 and int(t*16)%2:color=WHITE
    glow(d,x,y,31 if active else 27,color)
    ux,uy=m.direction
    if m.kind=='gun' and m.state=='windup' and not active:ux,uy=ux-x,uy-y
    angle=math.atan2(uy,ux)
    if m.kind=='spider':angle+=math.sin(t*13)*.03
    if not sprite(d,m.kind,x,y,76 if m.kind=='spider' else 72,angle,1 if active else .83):
        d.rect(x-28,y-20,56,40,(37,54,65));d.rect(x-28,y-20,56,40,color,False)
        d.circle(x,y,6,color)
    if active:
        core(d,x-ux*7,y-uy*7,t,True)
        for j in range(4):d.rect(x-24+j*13,y+48,9,4,CYAN if j<m.hp else (54,65,75))
    elif m.state=='stun':
        for j in range(3):
            a=t*4+j*math.tau/3;d.circle(x+math.cos(a)*23,y+46+math.sin(a)*4,3,GOLD)
        d.text(x-34,y-51,f'기절 {m.timer:.1f}s',GOLD,14)
    else:
        label=BODY_NAMES[m.kind]+' · '+str(WEIGHTS[m.kind])
        d.text(x-34,y-49,label,GOLD if m.state=='empty' else MUTED,14)

def wall(d,rect,color=(73,96,114)):
    x,y,w,h=rect
    d.rect(x,y,w,h,(29,43,57));d.rect(x+3,y+3,w-6,h-6,(42,59,75))
    d.rect(x,y,w,h,color,False)
    d.line(x+2,y+h-2,x+w-2,y+h-2,(114,137,151))
    for yy in range(int(y+14),int(y+h),28):d.line(x+5,yy,x+w-5,yy,(56,78,94))

def arena(d,w,aim):
    t=w.time
    d.rect(0,0,1100,780,BG)
    d.rect(42,142,1016,510,(15,26,38))
    clip=p.SDL_Rect(48,134,1004,498)
    p.SDL_RenderSetClipRect(rt.renderer,ctypes.byref(clip))
    try:
        for x in range(48,1050,34):d.line(x,148,x,646,(22,37,50))
        for y in range(148,647,34):d.line(48,y,1052,y,(22,37,50))
        # Floor conduits connect mechanisms without hiding their states.
        for i,(px,py,minimum) in enumerate(w.level.plates):
            active=w.plate_weights[i]>=minimum;c=GREEN if active else (61,79,88)
            d.line(px,py,px,610,c);d.line(px,610,868,610,c)
        for i,(rx,ry) in enumerate(w.level.relays):
            c=GREEN if i in w.relay_on else (51,71,82)
            d.line(rx,ry,900,ry,c);d.line(900,ry,900,390,c)
        for pit in w.level.pits:
            x,y,b,h=pit;d.rect(x,y,b,h,(3,9,16));d.rect(x,y,b,h,(78,97,112),False)
            for yy in range(y+8,int(y+h),24):
                d.line(x+4,yy,x+13,yy+8,ORANGE);d.line(x+b-13,yy,x+b-4,yy+8,ORANGE)
            d.text(x-5,min(625,y+h-20),'정비 구덩이',MUTED,14)
        for rect in w.solids:wall(d,rect)
        for i,door in enumerate(w.level.doors):
            x,y,b,h,_=door
            if not w.door_is_open(i):
                d.rect(x,y,b,h,(24,52,72));d.rect(x,y,b,h,BLUE,False)
                for yy in range(y+10,int(y+h),22):d.line(x+3,yy,x+b-3,yy+10,BLUE)
                d.text(x-20,625,'압력문',BLUE,14)
            else:
                dotted(d,(x+b/2,y),(x+b/2,y+h),(36,95,99),12)
        security=w.level.goal in ('purge','boss')
        for x,y,b,h in w.gate_panels:
            color=BLUE if security else ORANGE
            d.rect(x,y,b,h,(24,44,64) if security else (68,44,32))
            d.rect(x,y,b,h,color,False)
            for yy in range(int(y+10),int(y+h),24):d.line(x+2,yy,x+b-2,yy+10,color)
        if security and not w.gate_open:
            d.text(813,425,'관리자 잠금' if w.level.boss else '경비 잠금',BLUE,14)
        if w.level.powered_gate and not w.gate_open:
            ring(d,868,390,26,GREEN if w.power_ready else BLUE)
            d.text(816,435,'전원 ON' if w.power_ready else '전원 필요',GREEN if w.power_ready else BLUE,14)
        for i,(px,py,minimum) in enumerate(w.level.plates):
            amount=w.plate_weights[i];c=GREEN if amount>=minimum else GOLD
            d.circle(px,py,32,(29,45,49));ring(d,px,py,32,c);ring(d,px,py,26,c)
            d.text(px-16,py-5,f'{amount}/{minimum}',c,16)
            if amount<minimum:d.text(px-30,py-51,'압력판',MUTED,14)
        for i,(rx,ry) in enumerate(w.level.relays):
            c=GREEN if i in w.relay_on else PURPLE
            d.rect(rx-16,ry-16,32,32,(27,44,47));d.rect(rx-16,ry-16,32,32,c,False)
            d.circle(rx,ry,7,c);d.text(rx-28,ry-36,'웹 릴레이',c,14)
        for ax,ay in w.level.anchors:
            ring(d,ax,ay,14,PURPLE);ring(d,ax,ay,8,PURPLE)
            d.line(ax-18,ay,ax+18,ay,PURPLE);d.line(ax,ay-18,ax,ay+18,PURPLE)
        for crate in w.crates:
            if not crate.alive:continue
            c=BLUE if crate.conductive else GOLD
            d.rect(crate.x-15,crate.y-15,30,30,(40,51,64));d.rect(crate.x-15,crate.y-15,30,30,c,False)
            if crate.conductive:
                d.line(crate.x+3,crate.y+11,crate.x-5,crate.y,c)
                d.line(crate.x-5,crate.y,crate.x+5,crate.y,c)
                d.line(crate.x+5,crate.y,crate.x-3,crate.y-11,c)
            else:d.text(crate.x-5,crate.y-6,str(crate.weight),c,16)
        # The exit socket and small-body-only passage stay visually consistent.
        d.rect(1005,352,39,70,(18,61,54));d.rect(1005,352,39,70,GREEN,False)
        d.text(1008,390,'출구',GREEN,14);d.text(933,440,'본체만',MUTED,14)
        if w.level.turret_interval:
            c=MUTED if w.hazards_disabled else RED
            d.circle(705,185,23,(40,43,58));ring(d,705,185,23,c);d.circle(705,185,8,c)
            if w.turret_aim and not w.hazards_disabled:
                dotted(d,(705,185),w.turret_aim,RED);ring(d,*w.turret_aim,19,RED)
        if w.level.laser:
            lx,ly,lw,lh=w.level.laser
            c=RED if w.laser_state=='active' else GOLD if w.laser_state=='warning' else (43,63,77)
            d.rect(lx,ly,lw,lh,c,False)
            for yy in range(ly,ly+lh,14):d.line(lx+lw/2-2,yy,lx+lw/2+2,yy+8,c)
            if w.laser_state=='active':d.rect(lx+8,ly,max(3,lw-16),lh,RED)
            d.text(lx-25,min(625,ly+lh+18),'정지됨' if w.hazards_disabled else '레이저',c,14)
        for b in w.bombs:
            c=ORANGE if b.team=='player' else RED
            if b.timer<1:c=GOLD if b.team=='player' else RED
            ring(d,b.x,b.y,b.radius,c);ring(d,b.x,b.y,b.radius-5,tuple(int(v*.4) for v in c))
            ring(d,b.x,b.y,max(6,b.radius*b.timer/b.total),c)
            d.line(b.x-9,b.y,b.x+9,b.y,c);d.line(b.x,b.y-9,b.x,b.y+9,c)
            d.text(max(55,min(990,b.x-25)),max(180,min(620,b.y+b.radius+8)),f'{b.timer:.1f}s',c,20)
        for enemy in w.drones:
            if enemy.hp<=0:
                d.rect(enemy.x-9,enemy.y-5,18,10,(54,48,48));continue
            c=BLUE if enemy.armor else RED
            d.circle(enemy.x,enemy.y,18,(70,44,58));ring(d,enemy.x,enemy.y,19,c)
            d.line(enemy.x-8,enemy.y+4,enemy.x-1,enemy.y,c);d.line(enemy.x+1,enemy.y,enemy.x+8,enemy.y+4,c)
            if enemy.armor:ring(d,enemy.x,enemy.y,23,BLUE)
            if enemy.stun>0:ring(d,enemy.x,enemy.y,26,PURPLE)
        if w.boss:
            boss=w.boss;c=ORANGE if boss.exposed>0 else RED
            if boss.hp<=0:c=MUTED
            glow(d,*boss.pos,57,c)
            if not sprite(d,'boss',*boss.pos,136,0,1 if boss.hp>0 else .4):d.circle(*boss.pos,48,c)
            if boss.hp>0 and boss.exposed<=0:ring(d,*boss.pos,69,BLUE);ring(d,*boss.pos,73,(43,72,94))
            if boss.exposed>0:d.text(boss.x-50,boss.y+89,f'방패 해제 {boss.exposed:.1f}s',ORANGE,16)
        for m in w.machines.values():
            if w.host!=m.kind and m.state=='windup' and m.kind=='ram':
                end=(m.x+m.direction[0]*750,m.y+m.direction[1]*750)
                dotted(d,m.pos,end,RED,12)
                if m.timer<=.35:d.text(m.x-25,m.y+66,'방향 고정',RED,14)
            if m.state in ('dash','charge','dash_empty','grapple','grapple_empty'):
                for j in range(5):
                    ring(d,m.x-m.direction[0]*(42+j*14),m.y-m.direction[1]*(42+j*14),8-j,CYAN if w.host==m.kind else ORANGE)
            mech(d,m,w.host==m.kind,t)
        # Weight counters must remain visible when a chassis sits on a plate.
        for i,(px,py,minimum) in enumerate(w.level.plates):
            weight=w.plate_weights[i]
            color=GREEN if weight>=minimum else GOLD
            d.rect(px+29,py+23,47,24,(15,29,38));d.rect(px+29,py+23,47,24,color,False)
            d.text(px+34,py+28,f'{weight}/{minimum}',color,14)
        for a,b in w.beams:
            d.line(*a,*b,PURPLE)
            for j in range(3):
                u=(t*2+j/3)%1;d.circle(b[0]+(a[0]-b[0])*u,b[1]+(a[1]-b[1])*u,3,PURPLE)
        if w.web_line and w.web_flash>0:d.line(*w.web_line[0],*w.web_line[1],PURPLE)
        if w.host:
            if w.host=='gun':
                target=w.bomb_target(aim);dotted(d,w.pos,target,(53,96,99));ring(d,*target,27,CYAN)
                d.text(max(55,min(955,target[0]-30)),max(175,min(620,target[1]-40)),'5초 뒤 폭격',CYAN,14)
            elif w.host in ('ram','mag','spider'):
                dx,dy=aim[0]-w.x,aim[1]-w.y;l=math.hypot(dx,dy) or 1
                reach=210 if w.host=='mag' else 110
                dotted(d,w.pos,(w.x+dx/l*reach,w.y+dy/l*reach),PURPLE if w.host in ('mag','spider') else CYAN)
        else:
            if not(w.invuln>0 and int(t*15)%2):core(d,w.x,w.y,t)
            if w.dodge_time>0:
                for j in range(4):ring(d,w.x-w.dodge_dir[0]*j*10,w.y-w.dodge_dir[1]*j*10,7-j,CYAN)
            target=w.candidate()
            if target:
                ring(d,*target.pos,45+math.sin(t*7)*3,CYAN);dotted(d,w.pos,target.pos,CYAN)
                d.text(target.x-38,target.y+68,'E 몸 탈취',CYAN,16)
        for shot in w.shots:
            d.line(shot.x-shot.vx*.04,shot.y-shot.vy*.04,shot.x,shot.y,RED)
            d.circle(shot.x,shot.y,5,RED);d.circle(shot.x,shot.y,2,GOLD)
        for x,y,r,lifetime,team in w.detonations:
            c=ORANGE if team=='player' else RED
            ring(d,x,y,r*(1.1-lifetime*.3),c)
            for j in range(12):
                a=j*2.399;rr=r*(1-lifetime*.9)
                d.circle(x+math.cos(a)*rr,y+math.sin(a)*rr,max(1,int(lifetime*9)),c)
        for particle in w.particles:d.circle(particle.x,particle.y,max(1,int(particle.life*6)),particle.color)
        ring(d,*aim,8,MUTED)
        for dx,dy in ((-13,0),(13,0),(0,-13),(0,13)):d.line(aim[0]+dx*.7,aim[1]+dy*.7,aim[0]+dx,aim[1]+dy,MUTED)
    finally:p.SDL_RenderSetClipRect(rt.renderer,None)
    d.offset=(0,0)
    d.rect(42,142,1016,510,(62,85,101),False)

def hud(d,w,paused=False,help_open=False,muted=False,shake=True):
    d.offset=(0,0)
    d.text(40,742,'SHELLBOUND',CYAN,38)
    d.text(40,702,f'{w.stage_index+1:02d} / 08   {w.level.name}',WHITE,20)
    name=BODY_NAMES.get(w.host,'작은 본체')
    d.text(465,742,name,ORANGE if w.host else CYAN,24)
    for j in range(5):d.circle(580+j*20,745,5,CYAN if j<w.hp else (44,61,75))
    ability={'ram':'조준 + 클릭: 돌진 / 무게 3','gun':'조준 + 클릭: 5초 예약 폭격 / 무게 2',
             'mag':'클릭 유지: 당기기 · 우클릭: 밀기 / 무게 2','spider':'고리·릴레이·적 조준 + 클릭: 웹 / 무게 1'}.get(w.host,'Space: 짧은 스텝 / E: 기체 탑승 / 무게 0')
    d.text(465,707,ability,MUTED,14)
    d.text(950,742,f'{w.time:05.1f}s',MUTED,18)
    if w.boss and w.boss.hp>0:
        d.text(770,678,'관리자',RED,14)
        for i in range(3):d.rect(835+i*55,673,47,9,ORANGE if i<w.boss.hp else (45,54,65))
    else:d.text(465,678,short(w.level.subtitle,80),MUTED,14)
    n,objective=w.objective
    d.text(43,111,n,CYAN,14);d.text(125,111,short(objective,104),WHITE,18)
    if w.message_time>0:
        for i,line in enumerate(wrap(w.message,118)[:2]):d.text(43,80-i*22,line,GOLD,16)
    elif w.host:
        m=w.machines[w.host]
        text='공격 준비 완료' if m.cooldown<=0 else f'다음 공격 {m.cooldown:.1f}초 · 몸을 바꿔도 명령은 유지됩니다'
        d.text(43,80,text,CYAN,16)
    d.text(40,32,'WASD 이동   마우스 조준   클릭/Space 능력   E 탑승·하차   Tab 전술 정지   Z 되돌리기   R 재시작',MUTED,14)
    d.text(40,12,f'H 도움말   F1 단계 힌트   Esc 일시정지   F11 전체화면   F2 연습 {"ON" if w.practice else "OFF"}   M 소리 {"OFF" if muted else "ON"}',GOLD if w.practice else MUTED,14)

def panel(d,title,lines):
    d.offset=(0,0);d.rect(160,205,780,370,(10,19,30));d.rect(160,205,780,370,(74,113,127),False)
    d.text(205,510,title,CYAN,32)
    for i,line in enumerate(lines):d.text(205,446-i*42,short(line,82),WHITE if i==0 else MUTED,20)

def planner(d,w):
    d.rect(300,660,480,40,(23,53,64));d.rect(300,660,480,40,CYAN,False)
    d.text(321,673,'전술 일시정지 · 시간과 폭격이 멈춰 있습니다',CYAN,18)
    d.text(43,58,'Tab 계속하기   F1 다음 힌트   Z 직전 배치 되돌리기',CYAN,16)

def menu_hit(pos,levels=False):
    x,y=pos
    if levels:
        for i in range(8):
            cx=150+(i%4)*265;cy=460-(i//4)*185
            if abs(x-cx)<108 and abs(y-cy)<72:return i
        return None
    if 70<=x<=520:
        if 310<=y<=366:return 'start'
        if 238<=y<=294:return 'continue'
        if 166<=y<=222:return 'levels'

def menu(d,t,progress=None,selection=0,levels=False,practice=False,message=''):
    d.offset=(0,0);d.rect(0,0,1100,780,BG)
    for i in range(24):d.line(40,80+i*27,1060,80+i*27,(20,34,47))
    d.text(65,677,'SHELLBOUND',CYAN,58)
    d.text(68,626,'껍질을 남기고, 길을 만들다',WHITE,26)
    if levels:
        d.text(68,568,'1–8 방 선택 · ← → 선택 이동 · Enter 시작 · P 연습',MUTED,18)
        for i,stage in enumerate(STAGES):
            x=150+(i%4)*265;y=460-(i//4)*185
            locked=progress is not None and i>progress.highest and not practice
            c=MUTED if locked else CYAN if selection==i else ORANGE
            d.rect(x-108,y-72,216,144,(19,34,47));d.rect(x-108,y-72,216,144,c,False)
            d.text(x-83,y+28,f'{i+1:02d}',c,32)
            d.text(x-83,y-8,stage.name,MUTED if locked else WHITE,18)
            record=progress.records.get(i) if progress else None
            label='잠김 · P로 연습 가능' if locked else '● '*record['stars'] if record else '플레이 가능'
            d.text(x-83,y-46,label,GOLD if record else MUTED,14)
        d.text(68,115,message or '보존 메달: 클리어 / 본체 체력 보존 / 기체 보존',GOLD,16)
        d.text(68,65,'Esc 시작 화면 · F2 연습 모드 · H 도움말',MUTED,16)
        return
    d.text(70,534,'서로 다른 몸의 능력과 무게를 연결하는',MUTED,20)
    d.text(70,498,'8스테이지 액션 퍼즐',WHITE,26)
    for y,title,key in [(338,'새로운 여정','Enter'),(266,'이어하기','C'),(194,'스테이지 선택','L')]:
        d.rect(70,y-28,450,56,(21,39,52));d.rect(70,y-28,450,56,(47,84,97),False)
        d.text(92,y-8,title,WHITE,24);d.text(431,y-7,key,CYAN,18)
    if progress:
        d.text(73,127,f'클리어 {len(progress.records)}/8  ·  보존 메달 {sum(r["stars"] for r in progress.records.values())}/24',GOLD,16)
    d.text(73,94,'P 연습 · 1–8 빠른 선택 · H 도움말 · F11 전체화면',MUTED,16)
    d.text(73,58,message or 'Tab으로 생각하고, Z로 다른 배치를 시험하세요.',GOLD if message else MUTED,16)
    d.text(998,22,'v1.0.1',MUTED,14)
    if not sprite(d,'core',827,590+math.sin(t*2)*6,116):core(d,827,550,t)
    for i,kind in enumerate(('ram','gun','mag','spider')):
        a=t*.08+i*math.tau/4;x=825+math.cos(a)*150;y=353+math.sin(a)*125
        glow(d,x,y,41,ORANGE);sprite(d,kind,x,y,100,.1*math.sin(t+i))
        d.text(x-25,y-66,BODY_NAMES[kind],MUTED,16)

def help_screen(d):
    d.offset=(0,0);d.rect(65,120,970,560,(10,20,31));d.rect(65,120,970,560,(74,113,127),False)
    d.text(105,619,'몸을 바꾸고, 상황을 바꾸세요',CYAN,32)
    lines=[
        ('기본','WASD 이동 · 마우스 조준 · E 탑승/하차 · 이동키+E로 내릴 방향 지정'),
        ('돌진형 / 3','클릭 또는 Space: 고정 방향 돌진. 장갑 파괴, 균열벽 돌파, 압력판 고정.'),
        ('포격형 / 2','위치를 지정하면 5초 뒤 폭격. 몸에서 내려도 예약은 유지됩니다.'),
        ('자석형 / 2','클릭/Space 유지: 앞쪽 적·물체 당기기. 우클릭: 밀어내기. 장갑 적은 안 끌립니다.'),
        ('거미형 / 1','구덩이를 건너고, 고리·초록 릴레이·적에 클릭해 웹 사용.'),
        ('생각할 시간','Tab: 전술 일시정지 · F1: 방별 힌트 · Z: 방 안에서 이전 행동으로 되돌리기'),
        ('다시 시도','R: 현재 방 재시작 · Esc: 일시정지 · Backspace: 메뉴 · F2: 피해 없는 연습'),
        ('중요','빈 몸도 무게가 있습니다. 폭격은 남겨 둔 기체도 파괴합니다. 배치부터 계획하세요.')]
    for i,(title,body) in enumerate(lines):
        y=553-i*46;d.text(105,y,title,ORANGE,16);d.text(255,y,body,WHITE,16)
    d.text(105,148,'H 닫기 · 진행은 일반 모드 클리어 시 자동 저장됩니다.',MUTED,16)

def ending(d,t,progress,completed,world):
    d.offset=(0,0);d.rect(0,0,1100,780,BG)
    for j in range(30):
        a=j*2.399+t*.07;r=60+j*8;d.circle(550+math.cos(a)*r,460+math.sin(a)*r*.6,2,(43,93,92))
    sprite(d,'core',550,510+math.sin(t*2)*5,140)
    d.text(285,365,'정원의 문이 열렸습니다',CYAN,38)
    d.text(267,309,'어떤 몸이었는지보다, 무엇을 남겼는지가 길을 만들었습니다.',WHITE,18)
    total=sum(completed.values())
    d.text(360,244,f'이번 여정 {total:.1f}초  ·  완료 {len(completed)}/8',GOLD,20)
    d.text(322,196,'Enter  시작 화면으로 · 더 나은 배치를 다시 찾아보세요',MUTED,18)
    d.text(338,101,'SHELLBOUND  ·  윤형균  ·  Python / pico2d',MUTED,16)
    d.text(315,72,'캐릭터 이미지: AI 생성 · 게임 규칙과 화면: 프로젝트 코드',MUTED,14)
