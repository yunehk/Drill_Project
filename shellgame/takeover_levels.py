"""Authored campaign: learn a body, combine bodies, then plan their placement."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Stage:
    name: str
    subtitle: str
    solids: tuple
    spawns: tuple
    gate_weapon: str = 'gun'
    turret_interval: float = 0
    turret_delay: float = 4
    laser: tuple = ()
    empty: tuple = ()
    required: tuple | None = None
    drones: tuple = ()
    plates: tuple = ()  # x, y, minimum total chassis weight
    doors: tuple = ()   # x, y, width, height, plate index
    relays: tuple = ()  # x, y; latch permanently when hit by spider web
    pits: tuple = ()
    anchors: tuple = ()
    crates: tuple = ()  # x, y, weight, conductive
    goal: str = 'gate'
    powered_gate: bool = False
    recover_bodies: bool = True
    boss: bool = False
    hints: tuple = ()

SLIT=((970,148,25,218),(970,410,25,236))
STAGES=(
    Stage('탈취의 시작','빼앗은 몸은 도구다. 벗어 둔 몸도 남는다.',
          ((105,310,34,160),(500,148,42,150),(620,480,42,166))+SLIT,
          (('ram',580,390),),'ram',hints=(
              '돌진의 붉은 선이 고정되면 옆으로 피하세요.',
              '벽에 박힌 기체에 접근해 E. 주황 균열벽은 직접 돌진으로 부숩니다.',
              '출구 틈은 본체만 통과합니다. 이동키+E로 원하는 쪽에 내리세요.')),
    Stage('5초 뒤의 한 발','폭격은 예약이다. 몸을 떠나도 명령은 남는다.',
          ((145,310,34,160),(485,148,40,160),(485,500,40,146))+SLIT,
          (('ram',590,390),('gun',745,350)),hints=(
              '돌진형으로 포격형의 장갑을 깨세요.',
              '포격형은 조준한 위치에 5초 뒤 폭격합니다. 내린 뒤에도 취소되지 않습니다.',
              'Tab으로 생각을 정리하고, Z로 방 안의 이전 행동을 되돌릴 수 있습니다.')),
    Stage('교차 사격','무작정 빠르기보다, 안전한 순간을 고른다.',
          ((105,310,34,160),(470,290,45,125))+SLIT,
          (('ram',580,390),('gun',745,505)),'gun',2.8,4.5,(610,250,24,290),hints=(
              '중앙 엄폐물도 돌진형을 기절시키는 데 쓸 수 있습니다.',
              '레이저는 노란 예고 뒤 빨갛게 켜집니다. 꺼진 동안 건너세요.',
              '빈 기체는 직선 탄을 막습니다. 회수할 몸의 위치를 생각하세요.')),
    Stage('모이는 순간','폭격 구역을 만들고, 적의 위치를 바꾼다.',
          ((490,148,28,130),(490,520,28,126))+SLIT,
          (('gun',345,390),('mag',650,390)),empty=('gun','mag'),required=('gun','mag'),
          drones=((795,335,False,'patrol'),(800,445,False,'patrol')),
          goal='purge',hints=(
              '움직이는 경비 드론 2기를 처리하면 출구 전원이 켜집니다.',
              '폭격을 예약하고 E로 내린 뒤 자석형으로 갈아타세요.',
              '자석은 조준 방향으로 Space/클릭을 누르는 동안 당깁니다. 가까운 위치에 폭격을 예약하세요.')),
    Stage('돌아갈 몸을 남겨라','이길 수 있는 몸과, 남겨야 하는 몸은 다르다.',
          ((130,220,30,180),)+SLIT,
          (('ram',565,390),('gun',465,290),('mag',320,230)),
          empty=('mag',),required=('ram','gun'),plates=((420,535,3),),
          doors=((600,148,26,498,0),),powered_gate=True,recover_bodies=False,
          crates=((320,510,1,False),),hints=(
              '압력판은 무게 3이 필요합니다. 본체는 무게가 없습니다.',
              '돌진형의 무게는 3. 먼저 포격형 장갑을 깬 뒤 돌진형을 압력판에 남기세요.',
              '압력판 전원이 켜져 있어야 출구벽을 부술 수 있습니다. 핵심 몸을 폭격하지 마세요. Z로 복구 가능.')),
    Stage('건너편의 전원','갈 수 있는 몸과 싸울 수 있는 몸을 나눈다.',
          ((150,180,30,100),)+SLIT,
          (('spider',430,390),('gun',750,470)),empty=('spider','gun'),required=('spider','gun'),
          pits=((555,148,85,498),),anchors=((740,390),(455,390)),relays=((730,235),),
          powered_gate=True,hints=(
              '검은 정비 구덩이는 거미형만 건널 수 있습니다.',
              '거미형으로 고리를 조준해 클릭하면 웹 이동. 초록 릴레이를 웹으로 맞히면 전원이 켜집니다.',
              '건너편 릴레이를 켜고 육지에서 포격형으로 교체하세요. 구덩이 위에서는 안전하게 내릴 수 없습니다.')),
    Stage('남겨 둔 것들의 합','세운 몸, 켜 둔 전원, 마지막 한 발.',
          ((140,180,30,110),)+SLIT,
          (('ram',380,390),('gun',420,250),('mag',735,300),('spider',735,510)),
          empty=('ram','gun','mag','spider'),required=(),
          plates=((410,535,3),(755,245,2)),doors=((585,148,26,498,0),),
          relays=((735,560),),powered_gate=True,recover_bodies=False,
          crates=((315,510,1,False),),hints=(
              '출구에는 압력판 두 개와 웹 릴레이의 전원이 모두 필요합니다.',
              '돌진형을 왼쪽 압력판에 남겨 통로를 열고, 건너편에서 거미형으로 릴레이를 켜세요.',
              '오른쪽 무게 2는 자석형이나 포격형으로 만들 수 있습니다. 어떤 몸을 남길지 선택하세요.')),
    Stage('정원의 심장','가진 몸을 모두 쓰기보다, 필요한 연결을 찾는다.',
          ((250,148,35,125),(250,515,35,131))+SLIT,
          (('ram',435,390),('gun',480,505),('mag',450,260),('spider',335,560)),
          empty=('ram','gun','mag','spider'),required=(),boss=True,goal='boss',
          turret_interval=4.5,turret_delay=6.,laser=(610,240,20,300),
          relays=((470,200),(740,565)),anchors=((700,540),(460,240)),
          crates=((570,285,1,True),(580,490,1,True)),hints=(
              '관리자의 방패는 돌진 충격 또는 푸른 전지와의 충돌로 12초 동안 열립니다.',
              '방패가 열린 동안 예약 폭격을 맞히세요. 총 세 번 명중하면 정원이 정지합니다.',
              '거미형으로 안전 릴레이 두 개를 연결하면 레이저와 보조 포탑이 멈춥니다. Tab으로 순서를 정하고 Z로 되돌리세요.')),
)

WEIGHTS={'core':0,'ram':3,'gun':2,'mag':2,'spider':1}
BODY_NAMES={'ram':'돌진형','gun':'포격형','mag':'자석형','spider':'거미형'}
