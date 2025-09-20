"""
Class for Creature Objects
"""
import random 
import numpy as np
import time
import math



mutatableStats = [
    "speed",
    "size",
    "strength",
    "color",
    "diet",
]
mutation_rate = 0.25
hunger_threshold = 70
thirst_threshold = 70

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
        # current target (e.g., a Bush instance) when seeking food or water
        self.target = None
        # pause state (real time): when set, creature will not move until time.time() >= paused_until
        self.paused_until = 0.0
        # pending action to complete when pause ends ('eat' or 'drink')
        self._pending_action = None
        # temporary move-away target after eating/drinking
        self._move_away_target = None
            
            
    def moveRandom(self, others=None):
        """Apply a small random acceleration, damp velocity, and update position.

        This produces smoother movement than jumping by random integers each tick.
        """
        # random acceleration vector
        ax = random.uniform(-1.0, 1.0) * self._accel_mag
        ay = random.uniform(-1.0, 1.0) * self._accel_mag

        # integrate acceleration -> velocity
        self.vx += ax
        self.vy += ay

        # apply simple repulsion from nearby creatures to spread them out
        if others:
            repel_x = 0.0
            repel_y = 0.0
            for o in others:
                if o is self:
                    continue
                dx = self.x - o.x
                dy = self.y - o.y
                d2 = dx * dx + dy * dy
                if d2 <= 0.0001:
                    continue
                # only consider neighbors within a radius
                neighbor_radius = 50.0
                if d2 < (neighbor_radius * neighbor_radius):
                    inv_d = 1.0 / (d2 ** 0.5)
                    # repulsion strength falls off with distance
                    strength = (neighbor_radius - (d2 ** 0.5)) / neighbor_radius
                    repel_x += (dx * inv_d) * strength * 0.5
                    repel_y += (dy * inv_d) * strength * 0.5
            # apply repel to velocity
            self.vx += repel_x
            self.vy += repel_y

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
            yield env.timeout(30) # divide by 60 to get how fast the stats drain in seconds (30 / 60 = 0.5 seconds to drain 1 point)
            self.energy -= 1
            self.thirst -= 1
            self.hunger -= 1
            
    
    def behavior_loop(self, env, bushes, water_sources, creatures=None):
        # Behavior: check vitals first; if thirsty/hungry, pick a target and move toward it
        while True:
            # If currently paused for eating/drinking, wait until real-time pause ends
            if time.time() < self.paused_until:
                # remain stopped while paused
                self.stopMoving()
                yield env.timeout(1)
                continue
            # If we just finished a pause, complete the pending action and set move-away
            if self._pending_action is not None and time.time() >= self.paused_until:
                # perform the pending action effects now (eat or drink)
                target_ref = self.target
                if self._pending_action == 'drink':
                    # increase thirst
                    self.thirst = min(100, self.thirst + 40)
                    # release reservation if held
                    if hasattr(target_ref, 'reserved_by'):
                        if target_ref.reserved_by is self:
                            target_ref.reserved_by = None
                        elif isinstance(target_ref.reserved_by, list) and self in target_ref.reserved_by:
                            try:
                                target_ref.reserved_by.remove(self)
                            except ValueError:
                                pass
                elif self._pending_action == 'eat':
                    # attempt to pick a berry now
                    if hasattr(target_ref, 'pick_berry') and target_ref.has_berries():
                        target_ref.pick_berry()
                        self.hunger = min(100, self.hunger + 30)
                    # release reservation on bush if any
                    if hasattr(target_ref, 'reserved_by'):
                        if target_ref.reserved_by is self:
                            target_ref.reserved_by = None
                        elif isinstance(target_ref.reserved_by, list) and self in target_ref.reserved_by:
                            try:
                                target_ref.reserved_by.remove(self)
                            except ValueError:
                                pass

                # set a move-away target about 3 creature lengths in a random outward direction
                creature_radius = max(1.0, self.size / 10.0)
                move_dist = 3.0 * creature_radius
                angle = random.uniform(0, 2 * 3.14159)
                away_x = self.x + move_dist * math.cos(angle)
                away_y = self.y + move_dist * math.sin(angle)
                # clamp
                away_x = max(0, min(800, away_x))
                away_y = max(0, min(600, away_y))
                self._move_away_target = (away_x, away_y)
                # clear pending action and set target to move-away
                self._pending_action = None
                self.target = self._move_away_target
            if self.thirst < thirst_threshold:
                # acquire or move toward water target
                if self.target is None or getattr(self.target, 'reserved_by', None) not in (None, self):
                    self.seek_water(water_sources)
                if self.target is not None:
                    action = self.move_towards_target()
                    if action == 'drink':
                        # stop movement immediately and ensure reservation
                        target_ref = self.target
                        self.stopMoving()
                        if hasattr(target_ref, 'reserved_by') and target_ref.reserved_by is None:
                            target_ref.reserved_by = self
                        # begin real-time pause: set paused_until and mark pending action (0.5s)
                        self.paused_until = time.time() + 0.5
                        self._pending_action = 'drink'
                        # during pause, don't change hunger/thirst now; will apply after pause
                        yield env.timeout(1)
                        continue
                else:
                    # no water target found; wander a bit (consider neighbors to spread out)
                    self.moveRandom(others=creatures)
            elif self.hunger < hunger_threshold:
                # acquire or move toward food target; re-acquire if current target has no berries
                if self.target is None or (hasattr(self.target, 'has_berries') and not self.target.has_berries()):
                    self.seek_food(bushes)
                if self.target is not None:
                    action = self.move_towards_target()
                    if action == 'eat':
                        target_ref = self.target
                        # stop movement immediately
                        self.stopMoving()
                        # mark pending eat and pause for real time (0.5s)
                        self.paused_until = time.time() + 0.5
                        self._pending_action = 'eat'
                        # do not pick the berry now; perform after pause
                        yield env.timeout(1)
                        continue
                else:
                    # no food target found; wander a bit (consider neighbors to spread out)
                    self.moveRandom(others=creatures)
            else:
                # not thirsty or hungry -> random movement and clear any target
                self.target = None
                self.moveRandom(others=creatures)

            # clamp to bounds
            self.x = max(0, min(800, self.x))
            self.y = max(0, min(600, self.y))

            yield env.timeout(1)  # Advance simulation time by 1 unit

    def move_towards_target(self):
        """Move toward self.target (expects target has x,y). Clears target when reached."""
        if self.target is None:
            return
        # get target coords (target may be an object with x,y or a tuple)
        try:
            tx = float(self.target.x)
            ty = float(self.target.y)
        except Exception:
            # fallback if target is a tuple
            tx, ty = self.target

        dx = tx - self.x
        dy = ty - self.y
        dist2 = dx * dx + dy * dy
        if dist2 <= 0.0:
            return
        dist = dist2 ** 0.5

        # determine touch distance: creature draw radius + target radius (defaults)
        creature_radius = max(1.0, self.size / 10.0)
        target_radius = getattr(self.target, 'radius', getattr(self.target, 'r', 6.0))
        touch_dist = creature_radius + float(target_radius)

    # if already touching, signal action to behavior_loop (so it can pause)
        if dist <= touch_dist:
            # eating
            if hasattr(self.target, 'pick_berry'):
                if self.target.has_berries():
                    # tell caller to perform eat (after pause)
                    return 'eat'
            # drinking
            if getattr(self.target, 'is_water', False):
                return 'drink'
            # otherwise just clear (release reservation if we had one)
            if hasattr(self.target, 'reserved_by'):
                if self.target.reserved_by is self:
                    self.target.reserved_by = None
                elif isinstance(self.target.reserved_by, list) and self in self.target.reserved_by:
                    try:
                        self.target.reserved_by.remove(self)
                    except ValueError:
                        pass
            self.target = None
            self.stopMoving()
            return

        # not yet touching: move up to speed toward target, but don't overshoot
        # compute step length
        step_len = self.speed
        if step_len >= dist:
            # jump to target position (or very near) to avoid overshoot
            self.x = tx
            self.y = ty
        else:
            # normal step toward target
            step_x = (dx / dist) * step_len
            step_y = (dy / dist) * step_len
            self.vx = step_x * self._damping
            self.vy = step_y * self._damping
            self.x += self.vx
            self.y += self.vy
        # if target is water and not reserved, reserve it for this creature
        if getattr(self.target, 'is_water', False):
            if getattr(self.target, 'reserved_by', None) in (None, self):
                self.target.reserved_by = self
        return None
            
    def seek_water(self, water_sources):
        # Choose the nearest unreserved water source. If none free, choose nearest overall.
        if not water_sources:
            return
        nearest_free = None
        nearest_free_d2 = None
        nearest_any = None
        nearest_any_d2 = None
        for w in water_sources:
            dx = w.x - self.x
            dy = w.y - self.y
            d2 = dx * dx + dy * dy
            # track nearest overall
            if nearest_any is None or d2 < nearest_any_d2:
                nearest_any = w
                nearest_any_d2 = d2
            # if free (not reserved) consider for nearest_free
            if getattr(w, 'reserved_by', None) is None:
                if nearest_free is None or d2 < nearest_free_d2:
                    nearest_free = w
                    nearest_free_d2 = d2

        chosen = nearest_free if nearest_free is not None else nearest_any
        self.target = chosen
    def seek_food(self, bushes):
        # Acquire the nearest bush that has at least one unreserved berry
        nearest = None
        best_dist2 = None
        for b in bushes:
            if not b.has_berries():
                continue
            # compute unreserved berries
            reserved_count = len(getattr(b, 'reserved_by', []))
            available = b.berryAmount - reserved_count
            if available <= 0:
                continue
            dx = b.x - self.x
            dy = b.y - self.y
            d2 = dx * dx + dy * dy
            if nearest is None or d2 < best_dist2:
                nearest = b
                best_dist2 = d2

        if nearest is None:
            return

        # reserve one berry slot on the bush and set target
        if not hasattr(nearest, 'reserved_by'):
            nearest.reserved_by = []
        nearest.reserved_by.append(self)
        self.target = nearest
            
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
    