# tile.py

import pygame
from pygame.sprite import Sprite

from random import choice

from lf_functions import Point, CARDINALS, INTERCARDINALS

class Tile(Sprite):
    """a class to define one map tile"""

    def __init__(self, game_map, tile_data):
        """create one map tile"""
        super().__init__()

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

        self.screen = game_map.screen
        self.settings = game_map.settings

        self.tilefolder = f'images/tilesets/{self.settings.tileset}'

        self.ID = tile_data['ID']

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
        self.marks   = 0

        # initialize dictionary to store adjoining tiles; actual adjoiners are
        #   determined by game_map
        edge_tile = Tile(game_map, {'type': 'edge'})
        directions = {**CARDINALS, **INTERCARDINALS}
        self.adjoiners = {}
        for direction in directions:
            self.adjoiners[direction]  = edge_tile

        self.load_image()

        self.hilited_image = {}
        colors = ['b', 'y', 'r']
        for color in colors:
            self.hilited_image[color] = pygame.image.load(
                f"{self.tilefolder}/tile_hilite_{color}.png")

        self.mark_image = pygame.image.load(f"{self.tilefolder}/tile_mark_los.png")

        self.grid_lines = pygame.image.load(f"{self.tilefolder}/tile_grid.png")
        self.wallcaps = {}

        # randomly rotate floor tiles
        if self.type == 'level':
            angles = [0, 90, 180, 270]
            rotation = choice(angles)
            self.image = pygame.transform.rotate(self.image, rotation)



    def load_image(self):
        """load images; all 3 bases use 1 image"""
        if 'base' in self.type:
            self.image = pygame.image.load(f"{self.tilefolder}/tile_base.png")
        else:
            self.image = pygame.image.load(f"{self.tilefolder}/tile_{self.type}.png")



    def mark(self):
        """mark LOS visible tiles"""
        self.marks += 1

    def unmark(self):
        self.marks = 0




    def change_type(self, new_type):
        """for use by the Map Editor"""
        self.type = new_type
        self.load_image()



    def blitme(self):
        """draw the tile"""

        if 'base' in self.type:

            if '_u' in self.type:
                t = self.settings.tile_size // 2
                pygame.draw.rect(self.screen,
                    self.settings.alt_team_color[self.settings.teams[0]],
                    pygame.Rect(self.rect.x, self.rect.y, t, t))
                pygame.draw.rect(self.screen,
                    self.settings.alt_team_color[self.settings.teams[1]],
                    pygame.Rect(self.rect.x, self.rect.y+t, t, t))
                pygame.draw.rect(self.screen,
                    self.settings.team_color[self.settings.teams[1]],
                    pygame.Rect(self.rect.x+t, self.rect.y, t, t))
                pygame.draw.rect(self.screen,
                    self.settings.team_color[self.settings.teams[0]],
                    pygame.Rect(self.rect.x+t, self.rect.y+t, t, t))
                pygame.draw.circle(self.screen, 'gray', self.rect.center, 10)


            elif '_1' in self.type:
                self.screen.fill(self.settings.team_color[self.settings.teams[0]], self.rect)
                pygame.draw.circle(self.screen, self.settings.b_w_team_color[self.settings.teams[0]], self.rect.center, 10)
                pygame.draw.circle(self.screen, self.settings.alt_team_color[self.settings.teams[0]], self.rect.center, 6)

            elif '_2' in self.type:
                self.screen.fill(self.settings.team_color[self.settings.teams[1]], self.rect)
                pygame.draw.circle(self.screen, self.settings.b_w_team_color[self.settings.teams[1]], self.rect.center, 10)
                pygame.draw.circle(self.screen, self.settings.alt_team_color[self.settings.teams[1]], self.rect.center, 6)






        self.screen.blit(self.image, self.rect)

        if self.type != 'wall':
            self.screen.blit(self.grid_lines, self.rect)
        else:
            for c in self.wallcaps:
                self.screen.blit(self.wallcaps[c], self.rect)

        for i in range(self.marks):
            self.screen.blit(self.mark_image, self.rect)

        if self.hilited:
            color = self.hilited
            self.screen.blit(self.hilited_image[color], self.rect)