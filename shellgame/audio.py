"""Tiny synthesized effects; missing audio devices never prevent playing."""
import math
import struct
import wave
from pathlib import Path
import pico2d as p


class Audio:
    def __init__(self):
        self.muted = False
        self.sounds = {}
        root = Path(__file__).resolve().parent.parent / '.cache' / 'audio'
        try:
            root.mkdir(parents=True, exist_ok=True)
            for name, start, end in [('shed', 180, 90), ('throw', 650, 180),
                                      ('equip', 260, 880), ('hurt', 120, 45),
                                      ('key', 650, 1100), ('block', 950, 400)]:
                path = root / (name+'.wav')
                samples = []
                phase = 0
                count = 3300
                for i in range(count):
                    t = i/count
                    phase += math.tau*(start+(end-start)*t)/22050
                    value = math.sin(phase)*math.sin(math.pi*t)*(1-t)*6500
                    samples.append(struct.pack('<h', int(value)))
                with wave.open(str(path), 'wb') as output:
                    output.setparams((1, 2, 22050, 0, 'NONE', 'not compressed'))
                    output.writeframes(b''.join(samples))
                self.sounds[name] = p.load_wav(str(path))
        except Exception:
            self.sounds.clear()

    def receive(self, events):
        if self.muted:
            return
        for name, _, _ in events:
            sound = self.sounds.get(name)
            if sound is not None:
                try:
                    sound.play()
                except Exception:
                    self.muted = True
