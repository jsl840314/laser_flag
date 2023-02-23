# laser_flag.py

import sys

import pygame

import tkinter as tk

from settings import Settings
from game_map import GameMap
from button import Button
from button_frame import ButtonFrame
from units import _SuperUnit, Sniper, Grunt, Scout

"""
Need a function for detecting line-rect collisions:
    line points are (x1, y1) (x2, y2)
    list all x values between x1 and x2, not inclusive
    list all y values between y1 and y2, not inclusive

    use y=mx+b on both lists to create list of collidepoints

    maybe add more collidepoints at midpoint between each 2 in previous list?
    or is this overkill?

    check each of those points against self.game_map.walls()
"""

TITLE = 'Laser Flag'
VERSION = '0.0.0'
VDATE = '2/8/2023'

class LaserFlag:
    """overall class to manage game assets and behavior"""

    def __init__(self, map_file):
        """initialize game and create resources"""
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode(
                (self.settings.screen_width, self.settings.screen_height))
        self.caption = f"{TITLE} v.{VERSION} {VDATE} by Jesse Stuart Leitch"
        self.caption += f" {self.settings.screen_width}x{self.settings.screen_height}"
        pygame.display.set_caption(self.caption)

        self.button_frame = ButtonFrame(self)
        self.game_map = GameMap(self, map_file)

        # initialize the buttons
        self.turn_button_g = Button(self, msg="END TURN", color='green',
            text_color='white', grid_position=(2, 1), width=5)
        self.turn_button_m = Button(self, msg="END TURN", color='magenta',
            text_color='white', grid_position=(2, 19), width=5)
        self.fire_button = Button(self, "FIRE", color='yellow',
            text_color='black', grid_position=(3, 10), width=3)



        # initialize the teams. Player 1 is green, 2 is magenta
        self.team_green   = pygame.sprite.Group()
        self.team_magenta = pygame.sprite.Group()

        self.selected_unit = None

        # initialize the game board for the first turn
        self.team_green_turn = True
        self.end_turn = False
        self._create_teams()
        self._update_screen()



    def run_game(self):
        """the main game loop"""
        while True:
            self._check_events()
            if self.end_turn:
                self._increment_turn()



    def _check_events(self):
        """respond to keypresses & mouse events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_tile_clicks(mouse_pos)
                self._check_unit_clicks(mouse_pos)
                self._check_turn_button(mouse_pos)



    def _increment_turn(self):
        if self.team_green_turn:
            self.team_green_turn = False
            for unit in self.team_green:
                if unit.current_ap >= 2:
                    unit.current_ap = -2
                elif unit.current_ap == 1:
                    unit.current_ap = -1
                else: unit.current_ap = 0
            for unit in self.team_magenta:
                unit.current_ap = 3
        else:
            self.team_green_turn = True
            for unit in self.team_magenta:
                if unit.current_ap >= 2:
                    unit.current_ap = -2
                elif unit.current_ap == 1:
                    unit.current_ap = -1
                else: unit.current_ap = 0
            for unit in self.team_green:
                unit.current_ap = 3

        self.end_turn = False
        self._update_screen()



    def _check_tile_clicks(self, mouse_pos):
        """check which map tile has been clicked"""

        for row in self.game_map.tiles:
            for tile in row:
                tile_clicked = tile.rect.collidepoint(mouse_pos)
                if tile_clicked:
                    self._print_tile_data(tile)                   # FOR DEBUG
                    if self.selected_unit:
                        self._move_selected_unit(tile)



    def _check_unit_clicks(self, mouse_pos):
        """check which unit, if any, has been clicked"""
        if self.team_green_turn:
            team = self.team_green
        else:
            team = self.team_magenta

        for unit in team:
            unit_clicked = unit.rect.collidepoint(mouse_pos)
            if unit_clicked:

                self.game_map.clear_highlights()
                if unit.selected:
                    unit.deselect(self)
                    self._update_screen()
                elif unit.current_ap > 0:
                    unit.select(self)
                    self._determine_range(unit)
                    self._update_screen()



    def _determine_range(self, unit):
        """determine which tiles are accessible to the unit"""
        tile_size = self.settings.tile_size
        home_col = (self.selected_unit.rect.x - tile_size) // tile_size
        home_row = (self.selected_unit.rect.y - tile_size) // tile_size
        home_tile = self.game_map.tiles[home_row][home_col]

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
                # do not walk from cover tiles unless it's step 0
                if tile.type == 'cover' and step > 0: continue 

                # loop through the tile's dictionary of adjoining tiles
                for direction, adj_tile in tile.adjoiners.items():
                    if (adj_tile.type != 'edge' and
                        adj_tile.type != 'wall' and
                        adj_tile not in last_step and
                        adj_tile not in this_step and not
                        adj_tile.occupied
                    ):

                        # if direction is cardinal n, s, e, w, it's valid
                        if len(direction) == 1 and adj_tile not in last_step:
                            this_step.append(adj_tile)

                        # if direction is diagonal, need to check the adjacent cardinals
                        else:
                            n_s = direction[0]
                            e_w = direction[1]

                            if (tile.adjoiners[n_s].type != 'wall' and
                                tile.adjoiners[e_w].type != 'wall' and
                                adj_tile not in last_step and
                                adj_tile not in this_step
                            ):
                                this_step.append(adj_tile)

            # add all tiles in this step
            reachable_tiles.append(this_step)

        for step in reachable_tiles:
            for tile in step:
                if self.selected_unit.current_ap == 3:
                    tile.hilite_b = True
                elif self.selected_unit.current_ap == 2:
                    tile.hilite_y = True
                elif self.selected_unit.current_ap == 1:
                    tile.hilite_r = True



    def _check_turn_button(self, mouse_pos):
        """increment turn when button is clicked"""
        turn_button_g_clicked = self.turn_button_g.rect.collidepoint(mouse_pos)
        turn_button_m_clicked = self.turn_button_m.rect.collidepoint(mouse_pos)

        if turn_button_g_clicked and self.team_green_turn == True:
            self.end_turn = True
            if self.selected_unit: self.selected_unit.deselect(self)
            print("Player 2 turn")

        if turn_button_m_clicked and self.team_green_turn == False:
            self.end_turn = True
            if self.selected_unit: self.selected_unit.deselect(self)
            print("Player 1 turn")



    def _move_selected_unit(self, tile):
        """move the selected unit to its chosen tile"""
        if tile.type == 'wall' or tile.occupied == True: return
        if not tile.hilite_b and not tile.hilite_y and not tile.hilite_r: return

        self.game_map.clear_highlights()

        tile_size = self.settings.tile_size
        old_tile_col = (self.selected_unit.rect.x - tile_size) // tile_size
        old_tile_row = (self.selected_unit.rect.y - tile_size) // tile_size

        self.game_map.tiles[old_tile_row][old_tile_col].occupied = False
        self.selected_unit.rect.x = tile.rect.x
        self.selected_unit.rect.y = tile.rect.y
        self.selected_unit.current_ap -= 1
        tile.occupied = True



    def _create_teams(self):
        """add the green team's units to the map"""
        tile_size = self.settings.tile_size
        self.team_green = pygame.sprite.Group()
        self.team_magenta = pygame.sprite.Group()

        for start_position in self.game_map.start_positions:
            if start_position[1] == 'g':
                unit = _SuperUnit(self, team = 'green')
            elif start_position[1] == 'h':
                unit = Sniper(self, team = 'green')
            elif start_position[1] == 'i':
                unit = Grunt(self, team = 'green')
            elif start_position[1] == 'j':
                unit = Scout(self, team = 'green')
            elif start_position[1] == 'm':
                unit = _SuperUnit(self, team = 'magenta')
            elif start_position[1] == 'n':
                unit = Sniper(self, team = 'magenta')
            elif start_position[1] == 'o':
                unit = Grunt(self, team = 'magenta')
            elif start_position[1] == 'p':
                unit = Scout(self, team = 'magenta')
            unit.rect.x = tile_size * (start_position[0]['col'] + 1)
            unit.rect.y = tile_size * (start_position[0]['row'] + 1)
            if unit.team == 'green':
                self.team_green.add(unit)
            else:
                self.team_magenta.add(unit)



    def _update_screen(self):
        """update images on the screen, and flip to the new screen"""

        # draw the background
        self.screen.fill(self.settings.bg_color)

        # draw the map
        self.game_map.draw_map()

        # draw the units
        for unit in self.team_green:
            unit.blitme()
        for unit in self.team_magenta:
            unit.blitme()

        # draw the button frame
        self.button_frame.draw_frame()

        # draw only the correct Turn button
        if self.team_green_turn:
            self.turn_button_g.draw_button()
        else:
            self.turn_button_m.draw_button()

        # draw the fire button if applicable
        if self.selected_unit and self.selected_unit.current_ap > 0:
            self.fire_button.draw_button()

        # make the most recently drawn screen visible
        pygame.display.flip()



    def _quit_game(self):
        """ends the game"""
        sys.exit()

################################################################################
# FUNCTIONS FOR DEBUGGING AND TESTING
################################################################################

    def _print_tile_data(self, tile):
        """display info about the selected tile"""

        print(f'row: {tile.row}   col: {tile.col}')
        print(f'type: {tile.type}')
        print(f'base: {tile.base}')
        print(f'occupied: {tile.occupied}')
        print("Adjoiners:")
        print(f"N: {tile.adjoiners['n'].type}  S: {tile.adjoiners['s'].type}  E: {tile.adjoiners['e'].type}  W: {tile.adjoiners['w'].type}")
        print(f"NE: {tile.adjoiners['ne'].type} SE: {tile.adjoiners['se'].type} NW: {tile.adjoiners['nw'].type} SW: {tile.adjoiners['sw'].type}")
        for c in tile.wallcaps:
            print(c)


################################################################################

map_list = [
    'maps/map_01.dat',
    'maps/map_02.dat'
]

if __name__ == '__main__':
    lf = LaserFlag(map_list[0])
    lf.run_game()