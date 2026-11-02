import random


class Camera:
    def __init__(self):
        self.strength = 0
        self.enabled = True

    def receive(self, events):
        for name, _, _ in events:
            strength = {'hurt': 7, 'equip': 4, 'enemy': 5, 'block': 2}.get(name, 0)
            self.strength = max(self.strength, strength)

    def update(self, dt):
        self.strength = max(0, self.strength-28*dt)

    def offset(self):
        if not self.enabled:
            return 0, 0
        return (random.uniform(-self.strength, self.strength),
                random.uniform(-self.strength, self.strength))
