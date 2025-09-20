"""
Class to track and log statistics of the simulation
"""

class StatTracker:
    def __init__(self):
        self.history = [] # List of dicts: each snapshot is one second
        
    def record(self, creatures, second):
        if not creatures:
            return
        # Single pass aggregation to reduce multiple O(n) passes
        total_speed = total_size = total_energy = total_hunger = total_thirst = 0.0
        n = len(creatures)
        for c in creatures:
            total_speed += c.speed
            total_size += c.size
            total_energy += c.energy
            total_hunger += c.hunger
            total_thirst += c.thirst
        avg_speed = total_speed / n
        avg_size = total_size / n
        avg_energy = total_energy / n
        avg_hunger = total_hunger / n
        avg_thirst = total_thirst / n
        
        self.history.append({
            "second": second,
            "avg_speed": avg_speed,
            "avg_size": avg_size,
            "avg_energy": avg_energy,
            "avg_hunger": avg_hunger,
            "avg_thirst": avg_thirst
        })