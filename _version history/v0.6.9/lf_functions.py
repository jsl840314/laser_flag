# lf_functions.py

"""several lengthy functions needed by Laser Flag"""

import pygame
from random import choice

################################################################################
# MISC CLASSES, FUNCTIONS, AND CONSTANTS
################################################################################

CARDINALS      = {'n': 'north', 's': 'south', 'e': 'east', 'w': 'west'}
INTERCARDINALS = ['nw', 'ne', 'sw', 'se']

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Line:
    def __init__(self, A, B):
        """A and B being the above Point class"""
        self.A = A
        self.B = B
        self.run  = self.B.x - self.A.x
        self.rise = self.B.y - self.A.y

    def slope_y_int(self):
        """don't calculate unless needed (division is expensive)"""
        self.slope = self.rise / self.run
        self.y_int = self.A.y - (self.slope * self.A.x)
        return self.slope, self.y_int

    def length(self):
        """don't calculate unless needed (division is expensive)"""
        self.length = (self.rise**2 + self.run**2) ** 0.5
        return self.length

def D6(): return choice(range(1, 7))

def game_caption():
    # generate caption for main screen
    f = open('_notes.txt', 'r')
    title = f.read(71)
    f.close()
    title  = title.split('\n')
    author  = title[0].split(', by ')[1]
    version = title[3].split()[0]
    v_date  = title[3].split()[1]
    title   = title[0].split(', by ')[0]
    return (f"{title} {version} \u00a9{v_date} by {author}")

def swap(input_variable_1, input_variable_2):
    """exchange the values of the chosen variables"""
    output_variable_1 = input_variable_2
    output_variable_2 = input_variable_1
    return output_variable_1, output_variable_2


def tile_direction(source_tile, target_tile):
    """returns cardinal or intercardinal direction FROM source TO target"""
    direction_string = ''

    if source_tile.row > target_tile.row:
        direction_string += 'n'
    elif source_tile.row < target_tile.row:
        direction_string += 's'

    if source_tile.col > target_tile.col:
        direction_string += 'w'
    elif source_tile.col < target_tile.col:
        direction_string += 'e'

    return direction_string


################################################################################
# WALKING DISTANCE FUNCTION
################################################################################

def determine_range(game_map, unit):
    """determine which tiles are accessible to the unit with one AP"""

    # print(f"determining walking range for {unit.unit_class}...")

    tile_size = game_map.settings.tile_size
    home_tile = unit.tile

    # reachable_tiles is a list of lists
    #   each sub-list contains all the tiles reachable in 1 step
    #   first sub-list is the home tile
    #   second sub-list is any of the surrounding 8 that are accessible
    #   third sub-list is any reachable from there
    unit.tile_steps     = [[home_tile]]
    for step in range(0, unit.move_speed):
        last_step = unit.tile_steps[step]
        this_step = []
        for tile in last_step:
            # if climbing onto elevated ground, end here (unless unit has climbing ability)
            if tile.type == 'elevated' and not unit.elevated and not unit.can_climb: continue
            # loop through the tile's dictionary of adjoining tiles
            for direction, adj_tile in tile.adjoiners.items():
                if (adj_tile.type != 'edge' and
                    adj_tile.type != 'wall' and
                    # adj_tile.type != 'base' and
                    adj_tile not in last_step and
                    adj_tile not in this_step and not
                    adj_tile.occupied
                ):

                    # if direction is cardinal n, s, e, w, it's valid;
                    #   nw, se etc. are a 2-character string so won't pass
                    if (len(direction) == 1 and adj_tile not in last_step):
                        this_step.append(adj_tile)

                    # if direction is diagonal, need to check the adjacent
                    #   cardinals for walls (cannot pass a wall corner)
                    else:
                        # direction is a 2-character string, break it
                        n_s = direction[0]
                        e_w = direction[1]

                        # determine distance from source
                        ROUND_FACTOR = 1
                        l = Line(home_tile.CEN, adj_tile.CEN)
                        dist = l.length() / game_map.settings.tile_size + ROUND_FACTOR
                        # print(dist)

                        # if a valid step, add to the step list and the unit's master list
                        if (tile.adjoiners[n_s].type != 'wall' and
                            tile.adjoiners[e_w].type != 'wall' and
                            adj_tile not in last_step and
                            adj_tile not in this_step and
                            dist <= unit.move_speed
                        ):
                            this_step.append(adj_tile)

        # add all tiles in this step
        unit.tile_steps.append(this_step)

################################################################################
# LINE OF SIGHT PUBLIC FUNCTIONS
################################################################################

def determine_los(game_map, unit):
    """find any tiles visible to the unit"""
    # print(f"determining line-of-sight for row {unit.tile.row}, col {unit.tile.col}...")

    # check each tile on the map
    # visible_tiles is a dictionary;
    #   keys are tiles and values are the first sight line found
    unit.visible_tiles = {unit.tile: None}
    for target_tile in game_map.all_tiles:
        # if target_tile.type == 'wall':
        #     continue
        # determine if source has LOS to current tile
        los, sight_line = line_of_sight(game_map, unit.tile, target_tile)
        if los:
            unit.visible_tiles[target_tile] = sight_line


def line_of_sight(game_map, source, target, wide_fov = True):
    """return True if source tile has line-of-sight to target tile"""
    los        = False
    sight_line = None
    test_lines = []

    if wide_fov:
        # generate 25 lines: connect centers and all 4 corners
        # CHANGE THIS TO THE 5 POINTS ON FACE BUT ONLY IF TILES NOT ORDINAL
        source_points = (source.CEN,
            source.NW, source.NE, source.SW, source.SE)
        target_points = (target.CEN,
            target.NW, target.NE, target.SW, target.SE)

    else:
        # generate 1 line: center to center
        source_points = [source.CEN]
        target_points = [target.CEN]

    # generate all possible lines from the 2 point groups
    for source_point in source_points:
        for target_point in target_points:
            test_lines.append(Line(source_point, target_point))

    # test all lines against all walls except target
    for line in test_lines:
        line_is_good = True
        for wall in game_map.all_walls:
            if wall.CEN == target.CEN:
                continue
            collide = _collide_line_tile(line, wall)
            if collide:
                line_is_good = False
                break
        if line_is_good:
            sight_line = line
            los = True
            break
    return los, sight_line

################################################################################
# LINE OF SIGHT PROTECTED FUNCTION
################################################################################

def _collide_line_tile(sight_line, tile):
    """returns True if the sightline touches the tile"""

    # get endpoints of sight_line
    A = sight_line.A
    B = sight_line.B

    # first handle any line segments that are completely to one side
    # if both y endpoints are north of the tile
    if A.y < tile.N.y and B.y < tile.N.y:           return False
    # if both y endpoints are south of the tile
    elif A.y > tile.S.y and B.y > tile.S.y:         return False
    # if both x endpoints are west of the tile
    elif A.x < tile.W.x and B.x < tile.W.x:         return False
    # if both x endpoints are east of the tile
    elif A.x > tile.E.x and B.x > tile.E.x:         return False

    # if line segment is vertical
    elif A.x == B.x:
        # if line is west of tile.W or east of tile.E, it's in a different column
        if A.x < tile.W.x or A.x > tile.E.x:
            return False
        else:
            return True

    # if line segment is horizontal
    elif A.y == B.y:
        # if line is north of tile.N or south of tile.S, it's in a different row
        if A.y < tile.N.y or A.y > tile.S.y:
            return False
        else:
            return True

    # if diagonal line
    else:
        slope, y_int = sight_line.slope_y_int()

        # find intersections of the sightline with the four sides of the tile
        x_int_n = (tile.N.y - y_int) / slope  # y=tile.N, solve for x
        x_int_s = (tile.S.y - y_int) / slope  # y=tile.S, solve for x
        y_int_e = (slope * tile.E.x) + y_int  # x=tile.E, solve for y
        y_int_w = (slope * tile.W.x) + y_int  # x=tile.W, solve for y

        # if either y_int is between tile.N and tile.S, return True
        if tile.N.y <= y_int_w <= tile.S.y:
            return True
        elif tile.N.y <= y_int_e <= tile.S.y:
            return True

        # if either x_int is between tile.W and tile.W, return True
        elif tile.W.x <= x_int_n <= tile.E.x:
            return True
        elif tile.W.x <= x_int_s <= tile.E.x:
            return True
        else:
            return False