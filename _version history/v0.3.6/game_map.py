# game_map.py

import pygame

from tile import Tile
from units import PlainUnit, Sniper, Grunt, Scout
from lf_functions import CARDINALS, determine_range, determine_los

class GameMap:
    """a class to store map data and build the map"""

    def __init__(self, lf_game, filename):
        """initialize the map from a file"""
        self.screen   = lf_game.screen
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
                new_tile = Tile(self, tile_data)
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


    def build_teams(self, lf_game):
        """place the units on the map"""
        tile_size = self.settings.tile_size

        for start_position in self.start_positions:
            if start_position['class'] == 'plain':
                unit = BaseUnit(self, team = start_position['team'])
            elif start_position['class'] == 'sniper':
                unit = Sniper(self, team = start_position['team'])
            elif start_position['class'] == 'grunt':
                unit = Grunt(self, team = start_position['team'])
            elif start_position['class'] == 'scout':
                unit = Scout(self, team = start_position['team'])

            # assign the tile to the unit
            row = start_position['row']
            col = start_position['col']
            unit.tile = self.tiles[row][col]

            # place the unit on the tile
            unit.rect.x = (col + 0.5) * tile_size
            unit.rect.y = (row + 0.5) * tile_size
            unit.tile.occupied = True

            # figure out what tiles the unit can reach and see
            determine_range(lf_game, unit)
            determine_los(lf_game, unit)

            # add unit to the proper team
            team = unit.team
            lf_game.teams[team].add(unit)

            # team magenta begins the game on overwatch
            if unit.team == 'm':
                unit.current_ap = -2