# lf_functions.py

"""several lengthy functions needed by Laser Flag"""

import pygame

def determine_range(lf_game, unit):
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

        # animate the step
        lf_game._update_screen()
        pygame.time.delay(lf_game.settings.animation_speed)

        # add all tiles in this step
        reachable_tiles.append(this_step)

################################################################################
# LINE OF SIGHT FUNCTIONS
################################################################################

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def find_targets(lf_game, unit):
    """find any targets visible to the unit"""

    settings = lf_game.settings
    if unit.team == 'green':
        enemy_team = lf_game.team_magenta
        enemy_bases = lf_game.game_map.bases_m
    else:
        enemy_team = lf_game.team_green
        enemy_bases = lf_game.game_map.bases_g
    tiles = lf_game.game_map.tiles

    tile_size = settings.tile_size
    t = tile_size // 2

    for enemy_unit in enemy_team:
        los, lines = line_of_sight(lf_game, unit.tile, enemy_unit.tile)
        if los:
            enemy_unit.targeted = True

        # for line in lines:
        #     pygame.draw.line(lf_game.screen, 'red', line[0], line[1])
        #     pygame.display.flip()
        #     pygame.time.delay(50)
        # pygame.time.delay(500)


def show_los(lf_game):
    """display the selected unit's line of sight"""
    unit = lf_game.selected_unit
    tiles = lf_game.game_map.tiles
    for row in tiles:
        for tile in row:
            los, lines = line_of_sight(lf_game, unit.tile, tile)
            if los:
                tile.mark()



def line_of_sight(lf_game, source, target):
    """determine if source tile has line-of-sight to target tile"""

    tileset = lf_game.game_map.tiles
    lines = get_sight_lines(source, target)

    walls = []
    for row in tileset:
        for tile in row:
            if tile.type == 'wall':
                walls.append(tile)

    for line in lines:
        for wall in walls:
            collision = collideline(line, wall)
            if collision:
                # if this line hits a wall, try the next one
                return False, lines
        # if we haven't returned yet, the line must be clear
        return True, lines


def get_sight_lines(source, target):
    """Generates a series of sight lines between the corners of two tiles"""

    row1 = source.row
    col1 = source.col
    row2 = target.row
    col2 = target.col

    # if target is southeast of source
    if row1 < row2 and col1 < col2:
        source_nearest = 'se'
        source_r_wing = 'sw'
        source_l_wing = 'ne'
        target_nearest = 'nw'
        target_r_wing = 'ne'
        target_l_wing = 'sw'

    # if target is northeast of source
    elif row1 > row2 and col1 < col2:
        source_nearest = 'ne'
        source_r_wing = 'se'
        source_l_wing = 'nw'
        target_nearest = 'sw'
        target_r_wing = 'nw'
        target_l_wing = 'se'

    # if target is northwest of source
    elif row1 > row2 and col1 < col2:
        source_nearest = 'nw'
        source_r_wing = 'ne'
        source_l_wing = 'sw'
        target_nearest = 'se'
        target_r_wing = 'nw'
        target_l_wing = 'se'

    # if target is southwest of source
    elif row1 < row2 and col1 > col2:
        source_nearest = 'sw'
        source_r_wing = 'nw'
        source_l_wing = 'se'
        target_nearest = 'ne'
        target_r_wing = 'se'
        target_l_wing = 'sw'

    else:
        return [(source.center, target.center)]



    s_near = source.corners[source_nearest]
    s_rwing = source.corners[source_r_wing]
    s_lwing = source.corners[source_l_wing]
    t_near = target.corners[target_nearest]
    t_rwing = target.corners[target_r_wing]
    t_lwing = target.corners[target_l_wing]

    return [
        (source.center, target.center),
        (s_near,        t_near),
        (s_near,        t_rwing),
        (s_near,        t_lwing),
        (s_rwing,       t_rwing),
        (s_rwing,       t_lwing),
        (s_lwing,       t_rwing),
        (s_lwing,       t_lwing)
    ]




def collideline(sight_line, tile):
    """returns True if the sightline touches the tile"""

    # # line intersection code from StackOverflow, by @i_4_got_points via
    # # Grumdrig. Will not detect colinearity; so maybe expand this
    def ccw(A,B,C):
        return (C.y-A.y) * (B.x-A.x) > (B.y-A.y) * (C.x-A.x)
    # Return true if line segments AB and CD intersect
    def intersect(A,B,C,D):
        return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

    # sight_line is a tuple, (firstpoint, endpoint)
    A = Point(sight_line[0][0], sight_line[0][1])
    B = Point(sight_line[1][0], sight_line[1][1])

    # check line against the four sidelines of the tile
    for side in tile.sides.values():
        C = Point(side[0][0], side[0][1])
        D = Point(side[1][0], side[1][1])

        if intersect(A, B, C, D):
            return True
    return False




def animate_laser(line):
    """draws a brief laser flash"""
    pass