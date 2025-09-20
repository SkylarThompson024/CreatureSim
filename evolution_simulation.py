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

# Precompute lake polygon points (used for rendering) to avoid rebuilding each frame
LAKE_CENTER = (WIDTH // 2, HEIGHT // 2)
cx, cy = LAKE_CENTER
LAKE_POINTS = [
    (cx - 60, cy),
    (cx - 50, cy - 20),
    (cx - 30, cy - 25),
    (cx - 10, cy - 15),
    (cx + 10, cy - 25),
    (cx + 30, cy - 20),
    (cx + 50, cy),
    (cx + 40, cy + 20),
    (cx + 20, cy + 25),
    (cx, cy + 15),
    (cx - 20, cy + 25),
    (cx - 40, cy + 20)
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
    plt.plot(df["second"], df["avg_thirst"], label="Avg Thirst")
    plt.plot(df["second"], df["avg_hunger"], label="Avg Hunger")
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
def draw_population(screen, creatures, bushes, font, tick_count):
    """Draw the scene. Cache per-creature status text surfaces and update only occasionally to save font.render calls."""
    screen.fill((34, 139, 82))

    # draw precomputed lake polygon
    try:
        pg.draw.polygon(screen, (0, 191, 255), LAKE_POINTS)
    except NameError:
        # fallback if LAKE_POINTS not set yet
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
        pg.draw.polygon(screen, (0, 191, 255), points)

    # Draw bushes
    for bush in bushes:
        bush.draw_bush(screen, bush.x, bush.y)

    # Draw creatures. Cache and reuse status text surfaces.
    for creature in creatures:
        cx = int(creature.x)
        cy = int(creature.y)
        radius = int(creature.size / 10)
        pg.draw.circle(screen, creature.color, (cx, cy), radius)

        # initialize cache attributes if needed
        if not hasattr(creature, "_status_surface"):
            creature._status_surface = None
            creature._status_last_tick = -9999
            # update every N frames (tweak this for perf/accuracy)
            creature._status_update_interval = 10

        # update cached surface only occasionally
        if (tick_count - creature._status_last_tick) >= creature._status_update_interval or creature._status_surface is None:
            stats_text = f"E:{creature.energy} H:{creature.hunger} T:{creature.thirst}"
            creature._status_surface = font.render(stats_text, True, (255, 255, 255))
            creature._status_last_tick = tick_count

        # blit cached surface
        text_surface = creature._status_surface
        if text_surface:
            text_x = cx - text_surface.get_width() // 2
            text_y = cy - radius + 12
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
    # Build water source points along the lake perimeter (use LAKE_POINTS)
    water_sources = []
    for (wx, wy) in LAKE_POINTS:
        # represent water source as a simple object with x,y and is_water flag
        ws = type("W", (), {})()
        ws.x = wx
        ws.y = wy
        ws.is_water = True
        ws.radius = 6.0
        ws.reserved_by = None
        water_sources.append(ws)

    for creature in creatures:
        env.process(creature.drain_vitals(env))
        env.process(creature.behavior_loop(env, bushes, water_sources=water_sources, creatures=creatures))
        # initialize small rendering cache on creatures
        creature._status_surface = None
        creature._status_last_tick = -9999
        creature._status_update_interval = 10
        # # initialize small rendering cache on creatures
        # creature._status_surface = None
        # creature._status_last_tick = -9999
        # creature._status_update_interval = 10
        
    
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
                        env.process(creatures[-1].behavior_loop(env, bushes, water_sources=water_sources, creatures=creatures))
                elif event.button == 3:  # Right click to add bush
                    if len(bushes) < max_bushes:
                        x, y = event.pos
                        bushes.append(Bush(x, y))
                        
        draw_population(screen, creatures, bushes, font, tick_count)
        tick_count += 1
        if (tick_count % 60 == 0): # Every second at 60 fps
            stats_tracker.record(creatures, tick_count // 60)
        # Advance simulated time by 1 unit per frame so each creature's timeouts
        # progress at a consistent rate regardless of active event count.
        try:
            env.run(until=env.now + 1)
        except Exception:
            # fallback to single step if run() isn't appropriate for the env state
            env.step()
        clock.tick(60)  # Limit to 60 FPS
    pg.quit()
    export_stats_to_excel(stats_tracker)
    plot_stats(stats_tracker)
    
if __name__ == "__main__":
    main()