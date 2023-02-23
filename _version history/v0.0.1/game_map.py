# game_map.py

import pygame
from pygame.sprite import Sprite

from random import choice

# constants for reading map.dat files
WALL    = 'X'
COVER   = 'c'
G_BASE  = 'G'
M_BASE  = 'M'
G_START = ['g', 'h', 'i', 'j']  # _SuperUnit, Sniper, Grunt, Scout
M_START = ['m', 'n', 'o', 'p']  # _SuperUnit, Sniper, Grunt, Scout
LEVEL   = ['_', 'g', 'h', 'i', 'j', 'm', 'n', 'o', 'p']   # unit start positions must be on level floor

CARDINALS = ['n', 's', 'e', 'w']


class GameMap:
    """a class to store map data and build the map"""

    def __init__(self, lf_game, filename):
        """initialize the map from a file"""
        self.screen = lf_game.screen
        self.settings = lf_game.settings

        # initialize tracking variables
        self.tiles = []
        self.walls = []
        self.base_positions_green = []
        self.base_positions_magenta = []
        self.start_positions = []
        self.filename = filename
        self._read_map()
        self._build_wall_list()
        self._determine_adjoiners()
        self._determine_wallcaps()

    def _read_map(self):
        # load a map file
        f = open(self.filename, 'r')
        for r, row in enumerate(f.readlines()):
            row_list = row.split()
            row_of_tiles = []
            for c, item in enumerate(row_list):
                tile_data = {'row': r, 'col': c,
                    'base': False, 'occupied': False}

                if item == WALL:
                    tile_data['type'] = 'wall'

                elif item == COVER:
                    tile_data['type'] = 'cover'

                elif item == G_BASE:
                    tile_data['type'] = 'base_g'
                    tile_data['occupied'] = True
                    self.base_positions_green.append(tile_data)

                elif item == M_BASE:
                    tile_data['type'] = 'base_m'
                    tile_data['occupied'] = True
                    self.base_positions_magenta.append(tile_data)

                elif item in LEVEL:
                    x = ['1', '2', '3', '4']
                    tile_data['type'] = f'level{choice(x)}'
                    if item in G_START:
                        self.start_positions.append((tile_data, item))
                        tile_data['occupied'] = True
                    elif item in M_START:
                        self.start_positions.append((tile_data, item))
                        tile_data['occupied'] = True

                row_of_tiles.append(_Tile(self, tile_data))

            self.tiles.append(row_of_tiles)

        f.close()


    def _build_wall_list(self):
        for row in self.tiles:
            for tile in row:
                if tile.type == 'wall':
                    self.walls.append(tile)


    def _determine_adjoiners(self):
        """determine what's occupying the 8 tiles adjacent to each tile"""
        m = self.settings.grid_size-1
        for r, row in enumerate(self.tiles):
            for c, tile in enumerate(row):
                if r > 0:
                    tile.adjoiners['n'] = self.tiles[r-1][c]
                if r < m:
                    tile.adjoiners['s'] = self.tiles[r+1][c]
                if c > 0:
                    tile.adjoiners['w'] = self.tiles[r][c-1]
                if c < m:
                    tile.adjoiners['e'] = self.tiles[r][c+1]
                if r > 0 and c > 0:
                    tile.adjoiners['nw'] = self.tiles[r-1][c-1]
                if r > 0 and c < m:
                    tile.adjoiners['ne'] = self.tiles[r-1][c+1]
                if r < m and c < m:
                    tile.adjoiners['se'] = self.tiles[r+1][c+1]
                if r < m and c > 0:
                    tile.adjoiners['sw'] = self.tiles[r+1][c-1]


    def _determine_wallcaps(self):
        """adds any wallcap images to the tile if necessary"""
        for wall in self.walls:
            for c in CARDINALS:
                if wall.adjoiners[c].type != 'wall':
                    image_file = f"images/tile_wallcap_{c}.png"
                    wall.wallcaps[c] = pygame.image.load(image_file)



    def draw_map(self):
        """redraw the map tiles"""
        for row in self.tiles:
            for tile in row:
                tile.blitme()

    def clear_highlights(self):
        """clear any highlighted tiles"""
        for row in self.tiles:
            for tile in row:
                tile.hilite_b = False
                tile.hilite_y = False
                tile.hilite_r = False


class _Tile(Sprite):
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
            self.row = tile_data['row']
            self.col = tile_data['col']
            self.occupied = tile_data['occupied']
            self.base = tile_data['base']
        else:
            self.row = None
            self.col = None
            self.occupied = None
            self.base = None
            return

        # create the tile and position it
        tile_size = self.settings.tile_size
        self.rect = pygame.Rect(0, 0, tile_size,
                                   tile_size)
        self.rect.x = (self.col * tile_size) + (tile_size / 2)
        self.rect.y = (self.row * tile_size) + (tile_size / 2)

        # flags for adjoining tiles
        edge_tile = _Tile(game_map, {'type': 'edge'})
        self.adjoiners = {}
        self.adjoiners['n'] = edge_tile
        self.adjoiners['s'] = edge_tile
        self.adjoiners['e'] = edge_tile
        self.adjoiners['w'] = edge_tile
        self.adjoiners['ne'] = edge_tile
        self.adjoiners['se'] = edge_tile
        self.adjoiners['nw'] = edge_tile
        self.adjoiners['sw'] = edge_tile

        image_file = f"images/tile_{self.type}.png"
        self.image = pygame.image.load(image_file)
        if self.base:
            base_image_file = f"images/base_{self.base}.png"
            self.base_image = pygame.image.load(base_image_file)

        # highlighting
        self.hilite_b = False
        self.hilite_y = False
        self.hilite_r = False
        self.hilite_b_image = pygame.image.load("images/tile_hilite_b.png")
        self.hilite_y_image = pygame.image.load("images/tile_hilite_y.png")
        self.hilite_r_image = pygame.image.load("images/tile_hilite_r.png")

        # wall caps
        self.wallcaps = {}


    def blitme(self):
        """draw the tile"""
        self.screen.blit(self.image, self.rect)
        if self.base:
            self.screen.blit(self.base_image, self.rect)
        if self.hilite_b:
            self.screen.blit(self.hilite_b_image, self.rect)
        elif self.hilite_y:
            self.screen.blit(self.hilite_y_image, self.rect)
        elif self.hilite_r:
            self.screen.blit(self.hilite_r_image, self.rect)

        # if self.wallcaps != {}:
        for c in self.wallcaps:
            self.screen.blit(self.wallcaps[c], self.rect)



