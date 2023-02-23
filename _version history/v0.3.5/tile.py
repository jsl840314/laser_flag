# tile.py

import pygame
from pygame.sprite import Sprite

from random import choice

from lf_functions import Point, Line

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
        if self.type != 'edge':
            self.row      = tile_data['row']
            self.col      = tile_data['col']
            self.occupied = tile_data['occupied']
        else:
            self.row      = None
            self.col      = None
            self.occupied = None
            return  # do not go any farther if this is an edge tile

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

        # flags for adjoining tiles
        edge_tile = Tile(game_map, {'type': 'edge'})
        self.adjoiners = {}
        self.adjoiners['n']  = edge_tile
        self.adjoiners['s']  = edge_tile
        self.adjoiners['e']  = edge_tile
        self.adjoiners['w']  = edge_tile
        self.adjoiners['ne'] = edge_tile
        self.adjoiners['se'] = edge_tile
        self.adjoiners['nw'] = edge_tile
        self.adjoiners['sw'] = edge_tile

        # load images
        image_file = f"images/tile_{self.type}.png"
        self.image = pygame.image.load(image_file)
        self.hilited_image = {
            'b': pygame.image.load("images/tile_hilite_b.png"),
            'y': pygame.image.load("images/tile_hilite_y.png"),
            'r': pygame.image.load("images/tile_hilite_r.png")
        }
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