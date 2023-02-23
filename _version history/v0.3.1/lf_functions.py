# lf_functions.py

"""several lengthy functions needed by Laser Flag"""

import pygame
from random import choice

################################################################################
# MISC CLASSES AND FUNCTIONS
################################################################################

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Line:
    def __init__(self, A, B):
        self.A = A
        self.B = B

    def slope_y_int(self):
        """don't calculate unless needed"""
        self.run   = self.B.x - self.A.x
        self.rise  = self.B.y - self.A.y
        self.slope = self.rise / self.run
        self.y_int = self.A.y - (self.slope * self.A.x)
        return self.slope, self.y_int

    def length(self):
        """don't calculate unless needed"""
        self.length = (self.rise**2 + self.run**2) ** 0.5
        return self.length


def D6():
    return choice(range(1, 7))


################################################################################
# WALKING DISTANCE FUNCTION
################################################################################

def determine_range(lf_game):
    """determine which tiles are accessible to the unit with one AP"""

    tile_size = lf_game.settings.tile_size
    unit = lf_game.selected_unit
    home_tile = unit.tile

    # reachable_tiles is a list of lists
    #   each sub-list contains all the tiles reachable in 1 step
    #   first sub-list is the home tile
    #   second sub-list is any of the surrounding 8 that are accessible
    #   third sub-list is any reachable from there
    reachable_tiles = [[home_tile]]
    for step in range(0, unit.move_speed):
        last_step = reachable_tiles[step]
        this_step = []
        for tile in last_step:
            # if climbing onto cover, end here
            if tile.type == 'cover' and not unit.elevated: continue
            # loop through the tile's dictionary of adjoining tiles
            for direction, adj_tile in tile.adjoiners.items():
                if (adj_tile.type != 'edge' and
                    adj_tile.type != 'wall' and
                    # adj_tile.type != 'base' and
                    adj_tile not in last_step and
                    adj_tile not in this_step and not
                    adj_tile.occupied
                ):

                    # if direction is cardinal n, s, e, w, it's valid
                    if len(direction) == 1 and adj_tile not in last_step:
                        this_step.append(adj_tile)

                    # if direction is diagonal, need to check the adjacent cardinals
                    else:
                        # direction is a 2 character string, break it
                        n_s = direction[0]
                        e_w = direction[1]

                        if (tile.adjoiners[n_s].type != 'wall' and
                            tile.adjoiners[e_w].type != 'wall' and
                            adj_tile not in last_step and
                            adj_tile not in this_step
                        ):
                            this_step.append(adj_tile)

        # display highlights
        for tile in this_step:
            if lf_game.selected_unit.current_ap == 3:
                tile.hilited = 'b'
            elif lf_game.selected_unit.current_ap == 2:
                tile.hilited = 'y'
            elif lf_game.selected_unit.current_ap == 1:
                tile.hilited = 'r'

        # animate the step
        lf_game._update_screen()

        base_speed = lf_game.settings.animation_speed
        speed_modifier = lf_game.selected_unit.move_speed
        FACTOR = 3
        pygame.time.delay((base_speed // speed_modifier) * FACTOR)

        # add all tiles in this step
        reachable_tiles.append(this_step)

################################################################################
# LINE OF SIGHT FUNCTIONS
################################################################################


def find_targets(lf_game):
    """find any enemy units visible to the selected unit"""
    # need to expand this to include bases
    settings = lf_game.settings
    unit = lf_game.selected_unit
    source_tile = unit.tile

    lf_game.targets_visible = False
    if unit.team == 'g':
        enemy_team = lf_game.teams['m']
        # enemy_bases = lf_game.game_map.bases_m
    else:
        enemy_team = lf_game.teams['g']
        # enemy_bases = lf_game.game_map.bases_g
    for enemy_unit in enemy_team:
        target_tile = enemy_unit.tile
        los, sight_lines = line_of_sight(lf_game, source_tile, target_tile)
        if los:
            enemy_unit.sight_lines = sight_lines
            enemy_unit.visible = True
            lf_game.targets_visible = True


def show_los(lf_game, source_tile):
    """find any tiles visible to the unit"""
    # check each tile on the map
    for target_tile in lf_game.tiles:
        if target_tile.type == 'wall' or target_tile == source_tile:
            continue
        # determine if source has LOS to current tile
        los, sight_lines = line_of_sight(lf_game, source_tile, target_tile)
        if los:
            target_tile.mark()


def line_of_sight(lf_game, source, target, wide_fov = True, unfair = False):
    """return True if source tile has line-of-sight to target tile"""
    los = False
    test_lines = []

    if unfair:
        # generate 5 lines, all shooter points to target center
        source_points = (source.center, source.nw, source.ne, source.sw, source.se)
        target_points = [target.center]

    # # test 5 lines: connect source center to all target points
    # source_points = ((source.center[0], source.center[1]))
    # target_points = (target.center, target.nw, target.ne, target.sw, target.se)

    elif wide_fov:
        # generate 25 lines: connect centers and all 4 corners
        source_points = (source.center,
            source.nw, source.ne, source.sw, source.se)
        target_points = (target.center,
            target.nw, target.ne, target.sw, target.se)

    else:
        # generate 1 line: center to center
        source_points = [source.center]
        target_points = [target.center]

    # generate all possible lines from the 2 point groups
    for source_point in source_points:
        for target_point in target_points:
            test_lines.append(Line(source_point, target_point))

    # add another option here for comparing only a few select corners

    # test all lines against all walls
    sight_lines = []
    for line in test_lines:
        line_is_good = True
        for wall in lf_game.walls:
            collide = collide_line_tile(line, wall)
            if collide:
                line_is_good = False
                break
        if line_is_good:
            sight_lines.append(line)
            los = True
            # break # to break after first line
    return los, sight_lines









def collide_line_tile(sight_line, tile):
    """returns True if the sightline touches the tile"""

    # get endpoints of sight_line
    A = sight_line.A
    B = sight_line.B

    # first handle any line segments that are completely to one side
    # if both y endpoints are north of the tile
    if A.y < tile.n and B.y < tile.n:           return False
    # if both y endpoints are south of the tile
    elif A.y > tile.s and B.y > tile.s:         return False
    # if both x endpoints are west of the tile
    elif A.x < tile.w and B.x < tile.w:         return False
    # if both x endpoints are east of the tile
    elif A.x > tile.e and B.x > tile.e:         return False

    # if line segment is vertical
    elif A.x == B.x:
        # if line is w of tile.w or east of tile.e, it's in a different column
        if A.x < tile.w or A.x > tile.e:
            return False
        else:
            return True

    # if line segment is horizontal
    elif A.y == B.y:
        # if line is n of tile.n or south of tile.s, it's in a different row
        if A.y < tile.n or A.y > tile.s:
            return False
        else:
            return True

    # if diagonal line
    else:
        slope, y_int = sight_line.slope_y_int()

        # find intersections of the sightline with the four sides of the tile
        x_int_n = (tile.n - y_int) / slope  # y=tile.n, solve for x
        x_int_s = (tile.s - y_int) / slope  # y=tile.s, solve for x
        y_int_e = (slope * tile.e) + y_int  # x=tile.e, solve for y
        y_int_w = (slope * tile.w) + y_int  # x=tile.w, solve for y

        # if either y_int is between side.n and side.s, return True
        if tile.n <= y_int_w <= tile.s:
            return True
        elif tile.n <= y_int_e <= tile.s:
            return True

        # if either x_int is between side.w and side.w, return True
        elif tile.w <= x_int_n <= tile.e:
            return True
        elif tile.w <= x_int_s <= tile.e:
            return True
        else:
            return False








def animate_laser(line):
    """draws a brief laser flash"""
    pass