# game_map.py

import pygame
from pygame.sprite import Sprite

from random import choice

from lf_functions import Point, Line

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
        self.base_positions = []
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
            for c, code in enumerate(row_list):

                # initialize tile data
                tile_data = {'row': r, 'col': c, 'occupied': False,
                    'type': self.settings.tile_dict[code]}

                if 'base' in tile_data['type']:
                    base_team = tile_data['type'][-1]
                    base_position = {'row': r, 'col': c,
                        'team': base_team}
                    self.base_positions.append(base_position)
                    # tile_data['occupied'] = True

                elif 'unit' in tile_data['type']:
                    unit_data = tile_data['type'].split('_')
                    unit_team = unit_data[1]
                    unit_class = unit_data[2]
                    start_position = {'row': r, 'col': c,
                        'team': unit_team, 'class': unit_class}
                    self.start_positions.append(start_position)
                    tile_data['type'] = 'level'

                # create the tile and add it to the row
                new_tile = _Tile(self, tile_data)
                row_of_tiles.append(new_tile)
                if 'wall' in new_tile.type:
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
                tile.hilited = None


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
        edge_tile = _Tile(game_map, {'type': 'edge'})
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




