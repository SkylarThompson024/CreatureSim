"""
Class to track and log statistics of the simulation
"""

class StatTracker:
    def __init__(self):
        self.history = [] # List of dicts: each snapshot is one second
        
    def record(self, creatures, second):
        if not creatures:
            return
        avg_speed = sum(c.speed for c in creatures) / len(creatures)
        avg_size = sum(c.size for c in creatures) / len(creatures)
        avg_energy = sum(c.energy for c in creatures) / len(creatures)
        avg_hunger = sum(c.hunger for c in creatures) / len(creatures)
        avg_thirst = sum(c.thirst for c in creatures) / len(creatures)
        
        self.history.append({
            "second": second,
            "avg_speed": avg_speed,
            "avg_size": avg_size,
            "avg_energy": avg_energy,
            "avg_hunger": avg_hunger,
            "avg_thirst": avg_thirst
        })