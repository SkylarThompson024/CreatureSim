import time
import simpy
import numpy as np
import random
import pygame as pg
from creature import Creature
from bush import Bush
from statTracker import StatTracker
import pandas as pd
import matplotlib.pyplot as plt


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

def export_stats_to_excel(stats_tracker):
    df = pd.DataFrame(stats_tracker.history)
    df.to_excel("CreatureSim_Stats.xlsx", index=False)
    
def plot_stats(stats_tracker):
    df = pd.DataFrame(stats_tracker.history)
    if df.empty:
        print("No data to plot.")
        return
    plt.plot(df["second"], df["avg_speed"], label="Avg Speed")
    plt.plot(df["second"], df["avg_size"], label="Avg Size")
    plt.plot(df["second"], df["avg_energy"], label="Avg Energy")
    plt.legend()
    plt.xlabel("Time (seconds)")
    plt.ylabel("Average Value")
    plt.title("Creature Simulation Stats Over Time")
    plt.show()

# # ---Evolution Simulation---
# def evolution_simulation(env, creatures, bushes):
#     while True:
            
#         yield env.timeout(1) # Advance simulation time by 1 unit
        
# ---Pygame Visualization---
def draw_population(screen, creatures, bushes, font):
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
        stats_text = f"E:{creature.energy} H:{creature.hunger} T:{creature.thirst}"
        text_surface = font.render(stats_text, True, (255, 255, 255))
        
        text_x = int(creature.x) - text_surface.get_width() // 2
        text_y = int(creature.y) - int(creature.size / 10) + 12
        screen.blit(text_surface, (text_x, text_y))

    pg.display.flip()
    
def main():
    pg.init()
    pg.font.init()
    stats_tracker = StatTracker()
    tick_count = 0
    font = pg.font.SysFont(None, 16)
    
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    env = simpy.Environment()
    creatures = [Creature(name=random.choice(creatureNames),
                          env=env,
                          x=random.randint(0, WIDTH),
                          y=random.randint(0, HEIGHT),
                          color=(255, 0, 0),
                          diet=random.choice(["herbivore", "carnivore", "omnivore"]))
                 for _ in range(2)]
    bushes = [Bush(x=random.randint(0, WIDTH),
                   y=random.randint(0, HEIGHT)) for _ in range(max_bushes - 5)]
    for creature in creatures:
        env.process(creature.drain_vitals(env))
        env.process(creature.behavior_loop(env, bushes, water_sources=[]))
        
    
    # env.process(evolution_simulation(env, creatures, bushes))
    
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
                        env.process(creatures[-1].drain_vitals(env))
                        env.process(creatures[-1].behavior_loop(env, bushes, water_sources=[]))
                elif event.button == 3:  # Right click to add bush
                    if len(bushes) < max_bushes:
                        x, y = event.pos
                        bushes.append(Bush(x, y))
                        
        draw_population(screen, creatures, bushes, font)
        tick_count += 1
        if (tick_count % 60 == 0): # Every second at 60 fps
            stats_tracker.record(creatures, tick_count // 60)
        env.step()
        clock.tick(60)  # Limit to 60 FPS
    pg.quit()
    export_stats_to_excel(stats_tracker)
    plot_stats(stats_tracker)
    
if __name__ == "__main__":
    main()