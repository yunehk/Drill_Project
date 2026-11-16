"""pico2d renderer for the takeover arena; no external art downloads."""
import math
from .drawing import BG, WHITE, MUTED, CYAN, ORANGE, RED, GOLD, GREEN
from .takeover import SOLIDS, GATE, GATE_OPEN

PURPLE=(174,143,246)
INK=(19,32,45)

def ring(d,x,y,r,c):
    d.circle(x,y,r,c,False)

def dotted(d,a,b,c,spacing=16):
    n=max(1,int(math.dist(a,b)/spacing))
    for i in range(n):
        if i%2==0:
            d.line(a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n,
                   a[0]+(b[0]-a[0])*(i+1)/n,a[1]+(b[1]-a[1])*(i+1)/n,c)

def core(d,x,y,t,small=False):
    r=8 if small else 11
    d.circle(x,y,r+4,(22,74,75))
    d.circle(x,y,r,CYAN)
    d.circle(x-4,y+3,2,BG);d.circle(x+4,y+3,2,BG)
    d.line(x-5,y+r-1,x-10,y+r+7+math.sin(t*5)*2,CYAN)
    d.line(x+5,y+r-1,x+10,y+r+7+math.sin(t*5)*2,CYAN)

def mech(d,m,active,t):
    x,y=m.pos
    if m.state=='wreck':
        for j in range(3):d.rect(x-24+j*20,y-12,12,15,(63,76,83))
        d.text(x-45,y-35,f'교체 {m.respawn:.1f}s',MUTED,14)
        return
    c=CYAN if active else GOLD if m.state in ('stun','empty') else RED if m.kind=='ram' else PURPLE
    if m.invuln>0 and int(t*18)%2:c=WHITE
    d.circle(x,y,39,(20,40,47) if active else (35,30,43))
    for sy in (-25,17):
        d.rect(x-31,y+sy,62,10,(49,65,79))
        for xx in range(-25,28,9):d.line(x+xx,y+sy+1,x+xx,y+sy+8,MUTED)
    d.rect(x-30,y-18,60,36,INK)
    d.rect(x-30,y-18,60,36,c,False)
    if m.kind=='ram':
        ux,uy=m.direction
        sx,sy=-uy,ux
        front=(x+ux*43,y+uy*43)
        for sign in (-1,1):
            d.line(x+ux*20+sx*sign*20,y+uy*20+sy*sign*20,*front,c)
            d.line(x+ux*17+sx*sign*22,y+uy*17+sy*sign*22,front[0]-ux*5,front[1]-uy*5,c)
        ring(d,x,y,15,c)
    else:
        if m.state=='windup' and not active:
            ux,uy=m.direction[0]-x,m.direction[1]-y
        else:ux,uy=m.direction
        length=math.hypot(ux,uy) or 1
        ux,uy=ux/length,uy/length
        for k in range(-5,6):d.line(x-uy*k,y+ux*k,x+ux*38-uy*k,y+uy*38+ux*k,ORANGE)
        d.circle(x,y,14,(74,65,49));ring(d,x,y,14,c)
    if active:core(d,x,y,t,True)
    else:d.circle(x,y,5,c)
    if m.state=='stun':
        for j in range(3):
            a=t*4+j*math.tau/3
            d.circle(x+math.cos(a)*25,y+43+math.sin(a)*5,3,GOLD)
        d.rect(x-27,y+54,54,4,(71,63,45))
        d.rect(x-27,y+54,54*min(1,m.timer/5.5),4,GOLD)
        d.text(x-37,y-54,f'기절 {m.timer:.1f}s',GOLD,14)
    elif m.state=='empty':d.text(x-25,y-50,'빈 기체',GOLD,14)
    elif not active:d.text(x-22,y-49,'돌진형' if m.kind=='ram' else '포격형',c,14)
    if active:
        for j in range(4):d.rect(x-27+j*14,y-48,10,4,CYAN if j<m.hp else (51,65,78))

def arena(d,w,aim):
    t=w.time
    d.rect(0,0,1100,780,BG)
    # Floor tiles + machinery around the arena perimeter.
    d.rect(42,142,1016,510,(16,27,39))
    for x in range(48,1050,34):d.line(x,148,x,646,(23,38,51))
    for y in range(148,647,34):d.line(48,y,1052,y,(23,38,51))
    d.rect(42,142,1016,510,(62,85,101),False)
    for x in range(60,1040,28):
        d.line(x,143,x+8,148,ORANGE)
        d.line(x,647,x+8,652,(72,92,104))
    for wall in w.solids:
        x,y,b,h=wall;d.rect(x,y,b,h,(41,57,72));d.rect(x,y,b,h,(88,111,129),False)
        for yy in range(y+12,int(y+h),22):d.line(x+4,yy,x+b-4,yy,(57,79,94))
    gates=GATE_OPEN if w.gate_open else [GATE]
    for x,y,b,h in gates:
        d.rect(x,y,b,h,(74,48,35));d.rect(x,y,b,h,ORANGE,False)
        for yy in range(y+10,int(y+h),24):d.line(x+2,yy,x+b-2,yy+10,ORANGE)
    if not w.gate_open:
        d.text(773,680,'돌진으로 균열벽 파괴' if w.level.gate_weapon == 'ram' else '포격으로 차단벽 파괴',ORANGE,17)
        dotted(d,(868,655),(868,635),ORANGE)
    else:d.text(820,390,'OPEN',CYAN,17)
    # Exit and narrow body-only passage.
    d.rect(1005,352,39,70,(20,69,60));d.rect(1005,352,39,70,GREEN,False)
    d.text(1008,390,'출구',GREEN,14)
    d.text(933,440,'본체만',MUTED,14)
    # Independent turret telegraph.
    if w.level.turret_interval:
        d.circle(705,185,23,(53,47,63));ring(d,705,185,23,RED)
        d.circle(705,185,9,RED)
    if w.level.laser:
        lx,ly,lw,lh=w.level.laser
        color=RED if w.laser_state=='active' else GOLD if w.laser_state=='warning' else (45,65,79)
        d.rect(lx,ly,lw,lh,color,False)
        for yy in range(ly,ly+lh,14):
            d.line(lx+lw/2-2,yy,lx+lw/2+2,yy+8,color)
        if w.laser_state=='active':
            d.rect(lx+8,ly,8,lh,RED)
            d.text(lx-26,ly+lh+20,'작동 중!',RED,17)
        elif w.laser_state=='warning':d.text(lx-30,ly+lh+20,'레이저 예고',GOLD,17)
        else:d.text(lx-30,ly+lh+20,'주기 레이저',MUTED,14)
    if w.turret_aim:
        dotted(d,(705,185),w.turret_aim,RED)
        ring(d,*w.turret_aim,19,RED)
    for m in w.machines.values():
        if w.host!=m.kind and m.state=='windup':
            if m.kind=='ram':
                ex=m.x+m.direction[0]*750;ey=m.y+m.direction[1]*750
                dotted(d,m.pos,(ex,ey),RED,12)
                if m.timer<=.35:d.text(m.x-25,m.y+70,'방향 고정!',RED,17)
            else:
                ring(d,*m.direction,62,ORANGE);ring(d,*m.direction,40,ORANGE)
                d.line(m.direction[0]-70,m.direction[1],m.direction[0]+70,m.direction[1],ORANGE)
                d.line(m.direction[0],m.direction[1]-70,m.direction[0],m.direction[1]+70,ORANGE)
        if m.state in ('dash','charge'):
            for j in range(5):
                x=m.x-m.direction[0]*(40+j*13);y=m.y-m.direction[1]*(40+j*13)
                ring(d,x,y,10-j,CYAN if w.host==m.kind else RED)
        mech(d,m,w.host==m.kind,t)
    # Player aim uses actual capped landing position.
    if w.host:
        ux,uy=aim[0]-w.x,aim[1]-w.y
        length=math.hypot(ux,uy) or 1
        if w.host=='gun':
            r=min(length,620);end=(w.x+ux/length*r,w.y+uy/length*r)
            dotted(d,w.pos,end,(76,109,107));ring(d,*end,25,CYAN)
            d.circle(*end,3,CYAN)
        else:
            end=(w.x+ux/length*115,w.y+uy/length*115)
            dotted(d,w.pos,end,CYAN,10)
    else:
        if not(w.invuln>0 and int(t*15)%2):core(d,w.x,w.y,t)
        if w.dodge_time>0:
            for j in range(4):ring(d,w.x-w.dodge_dir[0]*j*10,w.y-w.dodge_dir[1]*j*10,8-j,CYAN)
        target=w.candidate()
        if target:
            ring(d,*target.pos,46+math.sin(t*7)*3,CYAN)
            dotted(d,w.pos,target.pos,CYAN)
            d.text(target.x-40,target.y+78,'E  몸 탈취',CYAN,17)
    for s in w.shots:
        if s.explosive:
            ring(d,*s.target,62,ORANGE if s.team=='enemy' else CYAN)
            ring(d,*s.target,10+48*max(0,1-s.age/s.flight),ORANGE)
            yy=s.y+math.sin(math.pi*s.age/s.flight)*85
            d.circle(s.x,s.y,6,(45,40,34));d.line(s.x,s.y,s.x,yy,(85,73,52))
            d.circle(s.x,yy,9,ORANGE);d.circle(s.x-2,yy+2,3,GOLD)
        else:
            d.line(s.x-s.vx*.04,s.y-s.vy*.04,s.x,s.y,RED)
            d.circle(s.x,s.y,5,RED);d.circle(s.x,s.y,2,GOLD)
    for particle in w.particles:d.circle(particle.x,particle.y,max(1,int(particle.life*6)),particle.color)
    # Aim reticle stays in screen coordinates when shake is enabled.
    ring(d,*aim,8,MUTED)
    for dx,dy in ((-13,0),(13,0),(0,-13),(0,13)):d.line(aim[0]+dx*.7,aim[1]+dy*.7,aim[0]+dx,aim[1]+dy,MUTED)

def hud(d,w,paused=False,help_open=False,muted=False,shake=True):
    d.offset=(0,0)
    d.text(40,742,'SHELLBOUND',CYAN,38)
    d.text(40,702,f'STAGE {w.stage_index+1}/3  /  {w.level.name}',CYAN,17)
    form={'ram':'돌진형 · 방향 고정 돌진','gun':'포격형 · 착탄 위치 예측'}.get(w.host,'작은 본체 · 빠른 이동 / 스텝')
    d.text(465,741,form,WHITE,20)
    d.text(465,710,'본체',MUTED,14)
    for j in range(5):d.circle(527+j*19,710,5,CYAN if j<w.hp else (47,62,76))
    if w.practice:d.text(680,710,'연습 모드 · 피해 없음',GOLD,14)
    d.text(945,741,f'{w.time:05.1f}s',MUTED,20)
    n,objective=w.objective
    d.text(40,110,n,CYAN,26);d.text(90,110,objective,WHITE,20)
    if w.message_time>0:d.text(90,79,w.message,GOLD,17)
    elif w.host:
        m=w.machines[w.host]
        d.text(90,79,'공격 준비 완료' if m.cooldown<=0 else f'다음 공격 {m.cooldown:.1f}초',CYAN,17)
    else:d.text(90,79,'Space: 이동 방향으로 스텝 (무적 아님)',MUTED,17)
    d.text(40,36,'WASD 이동   마우스 조준   Space / 클릭 공격   E 탑승·하차   R 재시작   H 도움말   Esc 일시정지',MUTED,14)
    d.text(40,14,f'F2 연습 {"ON" if w.practice else "OFF"}   F4 흔들림 {"ON" if shake else "OFF"}   M 소리 {"OFF" if muted else "ON"}',MUTED,14)

def panel(d,title,lines):
    d.offset=(0,0)
    d.rect(160,210,780,360,(11,20,31));d.rect(160,210,780,360,(80,119,131),False)
    d.text(205,510,title,CYAN,38)
    for i,line in enumerate(lines):d.text(205,451-i*38,line,WHITE if i==0 else MUTED,20)

def menu(d,t):
    d.rect(0,0,1100,780,BG)
    for i in range(24):
        y=100+i*25;d.line(40,y,1060,y,(22,36,49))
    d.text(72,656,'SHELLBOUND',CYAN,58)
    d.text(74,603,'적의 몸을 빼앗아 길을 여는 액션 퍼즐',WHITE,26)
    d.text(74,551,'피하고 → 탈취하고 → 돌파하라',ORANGE,26)
    d.text(74,475,'01  탈취의 시작 — 돌진형 탈취와 균열벽 돌파',WHITE,20)
    d.text(74,432,'02  몸 바꾸기 — 포격형으로 교체해 차단벽 파괴',WHITE,20)
    d.text(74,389,'03  교차 사격 — 포탑과 주기 레이저를 피해 탈출',WHITE,20)
    d.text(74,290,'Enter  실전 시작',CYAN,26)
    d.text(74,245,'P  연습 시작    1 / 2 / 3  원하는 스테이지 선택',GOLD,20)
    d.text(74,175,'WASD 이동 · 마우스 조준 · Space 공격/스텝 · E 탑승/하차',MUTED,17)
    d.text(74,140,'F2 연습 모드   H 도움말   Esc 종료',MUTED,17)
    d.text(74,70,'기존 탈피 퍼즐: python main.py --classic',MUTED,14)
    # Existing native game-rendering geometry is used here, not slide artwork.
    from .takeover import Machine
    m=Machine('ram',855,475,direction=(1,0));mech(d,m,False,t)
    m=Machine('gun',855,325);mech(d,m,False,t)
    core(d,855,610,t)
    dotted(d,(855,585),(855,525),CYAN)
    dotted(d,(855,425),(855,370),CYAN)
