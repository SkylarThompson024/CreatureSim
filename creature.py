"""
Class for Creature Objects
"""
import random 
import numpy as np



mutatableStats = [
    "speed",
    "size",
    "strength",
    "color",
    "diet",
]
mutation_rate = 0.25

class Creature:
    def __init__(self, name, env, x, y, 
                 energy=100, thirst=100, hunger=100,
                 speed=1, size=50, strength=50,
                 color=(0, 255, 0), diet="herbivore"):
        self.name = name
        self.env = env
        # store positions as floats for smooth movement
        self.x = float(x)
        self.y = float(y)
        self.energy = energy
        self.thirst = thirst
        self.hunger = hunger
        self.speed = speed
        self.size = size
        self.strength = strength
        self.color = color
        self.diet = diet
        # velocity components for smooth movement
        self.vx = 0.0
        self.vy = 0.0
        # tuning parameters for the random-walk inertia
        self._accel_mag = max(0.1, float(self.speed) * 0.2)  # random acceleration magnitude
        self._damping = 0.85  # velocity damping each tick (0..1)
        # ensure size/speed reasonable defaults
        try:
            self.speed = float(self.speed)
        except Exception:
            self.speed = 1.0
    def moveRandom(self):
        """Apply a small random acceleration, damp velocity, and update position.

        This produces smoother movement than jumping by random integers each tick.
        """
        # random acceleration vector
        ax = random.uniform(-1.0, 1.0) * self._accel_mag
        ay = random.uniform(-1.0, 1.0) * self._accel_mag

        # integrate acceleration -> velocity
        self.vx += ax
        self.vy += ay

        # limit velocity magnitude to speed
        vel_mag = (self.vx ** 2 + self.vy ** 2) ** 0.5
        if vel_mag > self.speed:
            scale = self.speed / vel_mag
            self.vx *= scale
            self.vy *= scale

        # apply damping to smooth out jitter
        self.vx *= self._damping
        self.vy *= self._damping

        # update position
        self.x += self.vx
        self.y += self.vy
        