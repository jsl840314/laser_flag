# tile.py

import pygame
from pygame.sprite import Sprite

from random import choice

from lf_functions import Point, Line, CARDINALS, INTERCARDINALS

class Tile(Sprite):
    """a class to define one map tile"""

    def __init__(self, game_map, tile_data):
        """create one map tile"""
        super().__init__()

        self.screen = game_map.screen
        self.settings = game_map.settings

        # get dictionary data obtained by _read_map
        #   the game_map uses an empty 'edge' tile to place in the 'adjoiners'
        #   dictionary where appropriate
        self.type = tile_data['type']
        if self.type == 'edge':
            self.row      = None
            self.col      = None
            self.occupied = None
            return
            # do not go any farther if this is an edge tile

        self.row      = tile_data['row']
        self.col      = tile_data['col']
        self.occupied = tile_data['occupied']

        # create the tile and position it
        tile_size   = self.settings.tile_size
        half_tile   = tile_size // 2
        self.rect   = pygame.Rect(0, 0, tile_size,
                                        tile_size)
        self.rect.x = (self.col * tile_size) + (tile_size // 2)
        self.rect.y = (self.row * tile_size) + (tile_size // 2)

        # corner coordinates
        # TURN THESE INTO CAPITALS AND CHANGE CENTER to CEN
        self.NW  = Point(self.rect.x,             self.rect.y)
        self.N   = Point(self.rect.x + half_tile, self.rect.y)
        self.NE  = Point(self.rect.x + tile_size, self.rect.y)
        self.W   = Point(self.rect.x,             self.rect.y + half_tile)
        self.CEN = Point(self.rect.x + half_tile, self.rect.y + half_tile)
        self.E   = Point(self.rect.x + tile_size, self.rect.y + half_tile)
        self.SW  = Point(self.rect.x,             self.rect.y + tile_size)
        self.S   = Point(self.rect.x + half_tile, self.rect.y + tile_size)
        self.SE  = Point(self.rect.x + tile_size, self.rect.y + tile_size)

        # CREATE DICTIONARIES FOR EACH FACE (8 TOTAL)

        # display flags
        self.hilited = None
        self.marked  = False

        # dictionary to store adjoining tiles
        edge_tile = Tile(game_map, {'type': 'edge'})
        directions = CARDINALS + INTERCARDINALS
        self.adjoiners = {}
        for direction in directions:
            self.adjoiners[direction]  = edge_tile

        # load images
        self.image = pygame.image.load(f"images/tile_{self.type}.png")

        self.hilited_image = {}
        colors = ['b', 'y', 'r']
        for color in colors:
            self.hilited_image[color] = pygame.image.load(
                f"images/tile_hilite_{color}.png")

        self.mark_image = pygame.image.load("images/tile_mark_los.png")

        if self.type != 'wall':
            self.grid_lines = pygame.image.load("images/tile_grid.png")
        else:
            self.wallcaps = {}

        # randomly rotate floor tiles
        if self.type == 'level':
            angles = [0, 90, 180, 270]
            rotation = choice(angles)
            self.image = pygame.transform.rotate(self.image, rotation)

    def mark(self):
        """mark LOS visible tiles"""
        self.marked = True

    def unmark(self):
        self.marked = False

    def blitme(self):
        """draw the tile"""
        self.screen.blit(self.image, self.rect)

        if self.type != 'wall':
            self.screen.blit(self.grid_lines, self.rect)
        else:
            for c in self.wallcaps:
                self.screen.blit(self.wallcaps[c], self.rect)

        if self.marked:
            self.screen.blit(self.mark_image, self.rect)

        if self.hilited:
            color = self.hilited
            self.screen.blit(self.hilited_image[color], self.rect)