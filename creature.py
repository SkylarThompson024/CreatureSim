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
hunger_threshold = 30
thirst_threshold = 30

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
        
        
    def stopMoving(self):
        """Stop the creature's movement by setting velocity to zero."""
        self.vx = 0.0
        self.vy = 0.0
        
        
    def drain_vitals(self, env):
        while True:
            yield env.timeout(15) # divide by 60 to get how fast the stats drain in seconds (30 / 60 = 0.5 seconds to drain 1 point)
            self.energy -= 1
            self.thirst -= 1
            self.hunger -= 1
            
    
    def behavior_loop(self, env, bushes, water_sources):
        while True:
            if self.thirst < thirst_threshold:
                self.seek_water(water_sources)
            elif self.hunger < hunger_threshold:
                self.seek_food(bushes)
            elif self.energy >= 90:
                self.moveRandom()
            else:
                self.stopMoving()
                
            self.x = max(0, min(800, self.x))
            self.y = max(0, min(600, self.y))
            
            yield env.timeout(1)  # Advance simulation time by 1 unit
            
    def seek_water(self, water_sources):
        pass  # Placeholder for water-seeking behavior
    def seek_food(self, bushes):
        pass  # Placeholder for food-seeking behavior
    def reproduce(self, env):
        pass  # Placeholder for reproduction behavior
    def mutate(self):
        pass  # Placeholder for mutation behavior
    def draw(self, screen):
        pass  # Placeholder for drawing the creature on screen
    def eat(self, bush):
        pass  # Placeholder for eating behavior
    def drink(self, water_source):
        pass  # Placeholder for drinking behavior
    