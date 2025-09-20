"""
Class for Bush Objects
"""
import random
import pygame as pg

LEAF_GREEN = (50, 160, 50)
DARK_GREEN = (20, 100, 20)
GREEN = (34, 139, 34)
WATER_BLUE = (0, 191, 255)

class Bush:
    def __init__(self, x = random.randint(0, 800), y = random.randint(0, 600), berryAmount=5, regrowRate=0.1):
        self.x = x
        self.y = y
        self.berryAmount = berryAmount
        self.regrowRate = regrowRate
        
    def draw_bush(self, screen, x, y):
        points = [
            (x - 8, y),
            (x - 4, y - 6),
            (x, y - 4),
            (x + 4, y - 7),
            (x + 8, y),
            (x + 4, y + 4),
            (x - 4, y + 4)
        ]
        if 0 <= x <= screen.get_width() and 0 <= y <= screen.get_height():
            pixel_color = screen.get_at((x, y))[:3]  # Get RGB color at bush position
            if pixel_color == WATER_BLUE:
                self.draw_bush(screen, x, y + 1)  # Draw bush slightly lower if on water
            else: 
                pg.draw.polygon(screen, DARK_GREEN, points)  # Draw bush body
                #Overlay circles to simulate berries
                pg.draw.circle(screen, (255, 0, 0), (x + 4, y - 2), 1)  # Draw a berry
                pg.draw.circle(screen, (255, 0, 0), (x - 4, y), 1)  # Draw a berry
                pg.draw.circle(screen, (255, 0, 0), (x + 1, y + 2), 1)  # Draw a berry
        else:
            self.draw_bush(screen, random.randint(0, screen.get_width()), random.randint(0, screen.get_height()))
        
        
        
    def regrow(self):
        if (self.appleAmount < 5):
            self.appleAmount += 1
        