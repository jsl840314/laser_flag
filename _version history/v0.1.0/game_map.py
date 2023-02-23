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
LEVEL   = ['_'] + G_START + M_START # unit start positions count as level floor

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
        self.bases_g = []
        self.bases_m = []
        self.start_positions = []
        self.filename = filename
        self._read_map()
        self._determine_adjoiners()
        self._determine_wallcaps()

    def _read_map(self):
        """Loads a map in ASCII format"""
        f = open(self.filename, 'r')
        for r, row in enumerate(f.readlines()):
            row_list = row.split()
            row_of_tiles = []
            row_of_walls = []
            for c, item in enumerate(row_list):
                is_wall = False
                tile_data = {'row': r, 'col': c,
                    'base': False, 'occupied': False}
                if item == WALL:
                    is_wall = True
                    tile_data['type'] = 'wall'
                elif item == COVER:
                    tile_data['type'] = 'cover'
                elif item in LEVEL:
                    x = ['1', '2', '3', '4']
                    tile_data['type'] = f'level{choice(x)}'
                    if item in G_START:
                        self.start_positions.append((tile_data, item))
                    elif item in M_START:
                        self.start_positions.append((tile_data, item))
                elif item == G_BASE:
                    tile_data['type'] = 'base_g'
                    self.bases_g.append(tile_data)
                elif item == M_BASE:
                    tile_data['type'] = 'base_m'
                    self.bases_m.append(tile_data)
                # create the tile and add it to the row
                new_tile = _Tile(self, tile_data)
                row_of_tiles.append(new_tile)
                # add it to the wall list if appropriate
                if is_wall:
                    row_of_walls.append(new_tile)
            # add the rows to the master lists
            self.tiles.append(row_of_tiles)
            self.walls.append(row_of_walls)
        f.close()



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
        for row in self.walls:
            for wall in row:
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

    def clear_marks(self):
        """clear any marked tiles"""
        for row in self.tiles:
            for tile in row:
                tile.marked = False


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
        half_tile = tile_size // 2
        self.rect = pygame.Rect(0, 0, tile_size,
                                   tile_size)
        self.rect.x = (self.col * tile_size) + (tile_size // 2)
        self.rect.y = (self.row * tile_size) + (tile_size // 2)
        self.center = (self.rect.x + half_tile, self.rect.y + half_tile)

        self.corners = {
            'nw': (self.rect.x,             self.rect.y),
            'ne': (self.rect.x + tile_size, self.rect.y),
            'sw': (self.rect.x,             self.rect.y + tile_size),
            'se': (self.rect.x + tile_size, self.rect.y + tile_size)
        }

        self.sides = {
            'n': (self.corners['nw'], self.corners['ne']),
            's': (self.corners['sw'], self.corners['se']),
            'e': (self.corners['ne'], self.corners['se']),
            'w': (self.corners['nw'], self.corners['sw'])
        }

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
        if self.type != 'wall':
            self.grid_lines = pygame.image.load("images/tile_grid.png")

        # highlighting
        self.hilite_b = False
        self.hilite_y = False
        self.hilite_r = False
        self.marked = False
        self.hilite_b_image = pygame.image.load("images/tile_hilite_b.png")
        self.hilite_y_image = pygame.image.load("images/tile_hilite_y.png")
        self.hilite_r_image = pygame.image.load("images/tile_hilite_r.png")
        self.mark_image = pygame.image.load("images/tile_mark.png")

        # wall caps
        self.wallcaps = {}

    def mark(self):
        """mostly for debugging line-of-sight"""
        self.marked = True
    def unmark(self):
        self.marked = False


    def blitme(self):
        """draw the tile"""
        self.screen.blit(self.image, self.rect)
        if self.type != 'wall':
            self.screen.blit(self.grid_lines, self.rect)

        if self.hilite_b:
            self.screen.blit(self.hilite_b_image, self.rect)
        elif self.hilite_y:
            self.screen.blit(self.hilite_y_image, self.rect)
        elif self.hilite_r:
            self.screen.blit(self.hilite_r_image, self.rect)

        if self.marked:
            self.screen.blit(self.mark_image, self.rect)

        # if self.wallcaps != {}:
        for c in self.wallcaps:
            self.screen.blit(self.wallcaps[c], self.rect)



