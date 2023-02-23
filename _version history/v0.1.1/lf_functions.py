# lf_functions.py

"""several lengthy functions needed by Laser Flag"""

import pygame

def determine_range(lf_game):
    """determine which tiles are accessible to the unit"""
    # MOVE THIS TO A SEPARATE MODULE WITH THE LOS FUNCTION
    tile_size = lf_game.settings.tile_size
    unit = lf_game.selected_unit
    home_tile = unit.tile

    # reachable_tiles is a list of lists
    #   each sub-list contains all the tiles reachable in 1 step
    #   first sub-list is the home tile
    #   second sub-list is any of the surrounding 8 that are accessible
    #   third sub-list is
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
                    adj_tile.type != 'base' and
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
                tile.hilite_b = True
            elif lf_game.selected_unit.current_ap == 2:
                tile.hilite_y = True
            elif lf_game.selected_unit.current_ap == 1:
                tile.hilite_r = True

        # # animate the step
        # lf_game._update_screen()
        # pygame.time.delay(lf_game.settings.animation_speed)

        # add all tiles in this step
        reachable_tiles.append(this_step)

################################################################################
# LINE OF SIGHT FUNCTIONS
################################################################################

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def find_targets(lf_game):
    """find any targets visible to the unit"""
    # need to expand this to bases once los bugs worked out
    settings = lf_game.settings
    unit = lf_game.selected_unit
    source_tile = unit.tile
    if unit.team == 'green':
        enemy_team = lf_game.team_magenta
        enemy_bases = lf_game.game_map.bases_m
    else:
        enemy_team = lf_game.team_green
        enemy_bases = lf_game.game_map.bases_g
    for enemy_unit in enemy_team:
        target_tile = enemy_unit.tile
        los = line_of_sight(lf_game, source_tile, target_tile)
        if los:
            enemy_unit.targeted = True

def show_los(lf_game):
    """find any tiles visible to the unit"""
    source_tile = lf_game.selected_unit.tile
    # check each tile on the map
    for target_tile in lf_game.tiles:
        if target_tile.type == 'wall' or target_tile == source_tile:
            continue
        # determine if source has LOS to current tile
        los = line_of_sight(lf_game, source_tile, target_tile)
        if los:
            target_tile.mark()


def line_of_sight(lf_game, source, target):
    """return True if source tile has line-of-sight to target tile"""
    source_points = (source.center, source.nw, source.ne, source.sw, source.se)
    target_points = (target.center, target.nw, target.ne, target.sw, target.se)

    test_lines = []
    for source_point in source_points:
        for target_point in target_points:
            test_line = ((source_point[0], source_point[1]),
                (target_point[0], target_point[1]))
            test_lines.append(test_line)

    los = False
    for line in test_lines:
        line_is_good = True
        for wall in lf_game.walls:
            collide = collide_line_tile(line, wall)
            if collide:
                line_is_good = False
                break
        if line_is_good:
            los = True
            break

    return los


def collide_line_tile(sight_line, tile):
    """returns True if the sightline touches the tile"""

    # get endpoints of sight_line
    A = Point(sight_line[0][0], sight_line[0][1])
    B = Point(sight_line[1][0], sight_line[1][1])

    # handle any lines that are completely to one side

    # if both y endpoints are north of the tile, return False
    if A.y < tile.n and B.y < tile.n:
        return False
    # if both y endpoints are south of the tile, return False
    elif A.y > tile.s and B.y > tile.s:
        return False
    # if both x endpoints are west of the tile, return False
    elif A.x < tile.w and B.x < tile.w:
        return False
    # if both x endpoints are east of the tile, return False
    elif A.x > tile.e and B.x > tile.e:
        return False

    # if line is vertical
    elif A.x == B.x:

        # if line is w of tile.w or east of tile.e, return False
        if A.x < tile.w or A.x > tile.e:
            return False
        # otherwise return True
        else:
            return True

    # if line is horizontal
    elif A.y == B.y:

        # if line is n of tile.n or south of tile.s, return False
        if A.y < tile.n or A.y > tile.s:
            return False
        # otherwide return True
        else:
            return True


    #if diagonal line
    else:
        slope = (B.y - A.y) / (B.x - A.x)   # slope = rise over run
        y_int = B.y - (slope * B.x)             # y_int = y - mx


        # find intersections of the line with the four sides of the tile
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