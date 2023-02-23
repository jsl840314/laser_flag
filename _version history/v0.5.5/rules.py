# rules.py

import pygame

class Rules():
    """a frame to show the game rules"""

    def __init__(self, lf_game):
        self.screen = lf_game.screen
        self.settings = lf_game.settings
        tile_size = self.settings.tile_size
        grid_size = self.settings.grid_size

        # set dimensions and properties of the rules frame
        self.width, self.height = tile_size * 20, tile_size * 20
        self.frame_color = self.settings.btn_frame_color

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.x = tile_size
        self.rect.y = tile_size


    def show(self):
        """show the rules"""
        self.screen.fill(self.frame_color, self.rect)

