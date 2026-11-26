"""Small original synthesized effects; audio-device failures never stop the game."""
import math
import random
import struct
import wave
from pathlib import Path
import pico2d as p

class Audio:
    def __init__(self):
        self.muted=False;self.sounds={}
        root=Path(__file__).resolve().parent.parent/'.cache'/'audio-v2'
        specs=[('shed',180,90,.12),('throw',650,180,.15),('equip',260,880,.25),
               ('hurt',120,45,.2),('key',650,1100,.3),('block',950,400,.12),
               ('reserve',420,850,.4),('tick',1000,1100,.06),('blast',100,35,.6)]
        try:
            root.mkdir(parents=True,exist_ok=True)
            for name,start,end,duration in specs:
                path=root/(name+'.wav')
                if not path.exists():
                    rng=random.Random(3);count=int(22050*duration);phase=0.;frames=[]
                    for i in range(count):
                        t=i/count;phase+=math.tau*(start+(end-start)*t)/22050
                        signal=math.sin(phase)
                        if name=='blast':signal=signal*.5+rng.uniform(-1,1)*.5
                        envelope=math.sin(math.pi*min(1,t*12)) if t<1/12 else (1-t)**2
                        frames.append(struct.pack('<h',int(signal*envelope*7000)))
                    with wave.open(str(path),'wb') as output:
                        output.setparams((1,2,22050,0,'NONE','not compressed'));output.writeframes(b''.join(frames))
                self.sounds[name]=p.load_wav(str(path))
        except Exception:self.sounds.clear()

    def receive(self,events):
        if self.muted:return
        played=set()
        for name,_,_ in events:
            if name in played:continue
            sound=self.sounds.get(name)
            if sound:
                try:sound.play();played.add(name)
                except Exception:self.muted=True
