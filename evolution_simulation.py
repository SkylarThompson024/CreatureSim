import time
import simpy
import numpy as np
import random
import pygame as pg
from creature import Creature
from bush import Bush


# ---Configuration---
WIDTH, HEIGHT = 800, 600
max_creatures = 500
max_bushes = 50
mutation_rate = 0.25
creatureNames = [
    "Goblin",
    "Orc",
    "Troll",
    "Dragon",
    "Elf",
    "Dwarf",
    "Giant",
    "Vampire",
    "Werewolf",
    "Zombie",
]

# ---Evolution Simulation---
def evolution_simulation(env, creatures, bushes):
    while True:
        for creature in creatures:
            creature.moveRandom()
            # Ensure creatures stay within bounds
            creature.x = max(0, min(WIDTH, creature.x))
            creature.y = max(0, min(HEIGHT, creature.y))
        yield env.timeout(1) # Advance simulation time by 1 unit
        
# ---Pygame Visualization---
def draw_population(screen, creatures, bushes):
    screen.fill((34, 139, 82))
    x, y = 400, 300
    points = [
        (x - 60, y),
        (x - 50, y - 20),
        (x - 30, y - 25),
        (x - 10, y - 15),
        (x + 10, y - 25),
        (x + 30, y - 20),
        (x + 50, y),
        (x + 40, y + 20),
        (x + 20, y + 25),
        (x, y + 15),
        (x - 20, y + 25),
        (x - 40, y + 20)
    ]
    pg.draw.polygon(screen , (0, 191, 255), points)  # Draw lake
    for bush in bushes:
        bush.draw_bush(screen, bush.x, bush.y)
    for creature in creatures:
        pg.draw.circle(screen, creature.color, (int(creature.x), int(creature.y)), int(creature.size / 10))

    pg.display.flip()
    
def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    env = simpy.Environment()
    creatures = [Creature(name=random.choice(creatureNames),
                          env=env,
                          x=random.randint(0, WIDTH),
                          y=random.randint(0, HEIGHT),
                          color=(random.randint(0,255), random.randint(0,255), random.randint(0,255)),
                          diet=random.choice(["herbivore", "carnivore", "omnivore"]))
                 for _ in range(max_creatures - 5)]
    bushes = [Bush(x=random.randint(0, WIDTH),
                   y=random.randint(0, HEIGHT)) for _ in range(max_bushes - 5)]
    env.process(evolution_simulation(env, creatures, bushes))
    
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click to add creature
                    if len(creatures) < max_creatures:
                        x, y = event.pos
                        creatures.append(Creature(name=random.choice(creatureNames),
                                                  env=env,
                                                  x=x,
                                                  y=y,
                                                  color=(random.randint(0,255), random.randint(0,255), random.randint(0,255)),
                                                  diet=random.choice(["herbivore", "carnivore", "omnivore"])))
                elif event.button == 3:  # Right click to add bush
                    if len(bushes) < max_bushes:
                        x, y = event.pos
                        bushes.append(Bush(x, y))
                        
        draw_population(screen, creatures, bushes)
        env.step()
        clock.tick(60)  # Limit to 60 FPS
    pg.quit()
    
if __name__ == "__main__":
    main()