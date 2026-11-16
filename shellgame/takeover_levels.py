"""Three authored stages: learn, combine, then execute under pressure."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Stage:
    name: str
    subtitle: str
    solids: tuple
    spawns: tuple
    gate_weapon: str
    turret_interval: float
    turret_delay: float
    laser: tuple = ()

SLIT=((970,148,25,218),(970,410,25,236))
STAGES=(
    Stage('탈취의 시작','돌진을 피하고, 빼앗은 몸으로 균열벽을 돌파',
          ((105,310,34,160),(500,148,42,150),(620,480,42,166))+SLIT,
          (('ram',580,390),),'ram',0,0),
    Stage('몸 바꾸기','돌진형의 힘으로 포격형을 얻고, 엄폐물 너머로 포격',
          ((145,310,34,160),(485,148,40,160),(485,500,40,146))+SLIT,
          (('ram',590,390),('gun',745,350)),'gun',0,0),
    Stage('교차 사격','포탑과 주기 레이저 사이에서 두 몸을 연결해 탈출',
          ((105,310,34,160),(470,290,45,125))+SLIT,
          (('ram',580,390),('gun',745,505)),'gun',2.4,3.8,(610,250,24,290)),
)
