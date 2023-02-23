# lf_functions.py

"""the two somewhat lengthy functions needed by Laser Flag"""

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



def find_targets(lf_game, unit, enemy_team, enemy_bases, walls):
    """find any targets visible to the unit"""
    settings = lf_game.settings

    RANGE = 10
    tile_size = settings.tile_size
    t = tile_size // 2

    (x1, y1) = (unit.rect.x + t, unit.rect.y + t)
    if unit.team == 'green':
        enemy_team = lf_game.team_magenta
    else:
        enemy_team = lf_game.team_green

    for enemy_unit in enemy_team:
        (x2, y2) = (enemy_unit.rect.x + t, enemy_unit.rect.y + t)
        a = x2 - x1
        b = y2 - y1
        c = (a**2 + b**2) ** 0.5
        if c < tile_size * RANGE:
            enemy_unit.targeted = True