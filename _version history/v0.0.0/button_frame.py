# button_frame.py

import pygame
# from pygame.sprite import Sprite


class ButtonFrame():
    """a frame to hold buttons to control the game"""

    def __init__(self, lf_game):
        self.screen = lf_game.screen
        self.settings = lf_game.settings
        self.tile_size = self.settings.tile_size

        # set dimensions and properties of the button frame
        self.width, self.height = self.tile_size * 9, self.tile_size * 21
        self.frame_color = (50, 50, 50)

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.x = self.tile_size * 23
        self.rect.y = self.tile_size * 1

    def draw_frame(self):
        self.screen.fill(self.frame_color, self.rect)