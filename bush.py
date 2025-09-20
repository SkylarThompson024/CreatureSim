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
    def __init__(self, x = random.randint(0, 800), y = random.randint(0, 600), berryAmount=3, regrowRate=0.5):
        self.x = x
        self.y = y
        self.berryAmount = berryAmount
        self.regrowRate = regrowRate
        # reservation list so creatures can reserve berries to avoid over-targeting
        self.reserved_by = []
    
    def has_berries(self):
        return self.berryAmount > 0
    def pick_berry(self):
        if self.has_berries():
            self.berryAmount -= 1
            
        
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
        sw, sh = screen.get_width(), screen.get_height()
        # quick off-screen cull
        if not (0 <= x <= sw and 0 <= y <= sh):
            return

        # Avoid calling get_at (slow). Instead, draw bush normally.
        pg.draw.polygon(screen, DARK_GREEN, points)  # Draw bush body
        # Draw berries (small cost) only when present
        if self.berryAmount > 0:
            berry_positions = [(x + 4, y - 2), (x - 4, y), (x + 1, y + 2)]
            for i in range(min(self.berryAmount, len(berry_positions))):
                pg.draw.circle(screen, (255, 0, 0), berry_positions[i], 1)
        
        
        
    def regrow(self):
        if (self.berryAmount < 3):
            self.berryAmount += 1
        