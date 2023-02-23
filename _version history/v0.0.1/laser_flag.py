# laser_flag.py

import sys

import pygame

from settings import Settings
from game_map import GameMap
from button_frame import ButtonFrame, Button
from units import _SuperUnit, Sniper, Grunt, Scout
from lf_functions import determine_range

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
VERSION = '0.0.1'
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

        # the main display regions
        self.button_frame = ButtonFrame(self)
        self.game_map = GameMap(self, map_file)

        # initialize the buttons
        self.turn_button_g = Button(self, msg="END TURN",
            color=self.settings.team_g_color, text_color='white',
            grid_position=(2, 1), width=5)
        self.turn_button_m = Button(self, msg="END TURN",
            color=self.settings.team_m_color, text_color='white',
            grid_position=(2, 19), width=5, visible=False)
        self.laser_button = Button(self, "LASER",
            color='red', text_color='black',
            grid_position=(3, 10), width=3, visible=False)
        self.buttons = [
            self.turn_button_g,
            self.turn_button_m,
            self.laser_button
        ]

        # initialize the teams. Player 1 is green, 2 is magenta
        self.team_green   = pygame.sprite.Group()
        self.team_magenta = pygame.sprite.Group()

        # initialize the game board for the first turn
        self.selected_unit = None
        self.team_green_turn = True
        self.turn_number = 1
        self._create_teams()
        self._update_screen()



    def run_game(self):
        """the main game loop"""
        while True:
            self._check_events()



    def _check_events(self):
        """respond to keypresses & mouse events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_tile_clicks(mouse_pos)
                self._check_unit_clicks(mouse_pos)
                self._check_button_clicks(mouse_pos)



    def _check_tile_clicks(self, mouse_pos):
        """check if a map tile has been clicked"""
        for row in self.game_map.tiles:
            for tile in row:
                tile_clicked = tile.rect.collidepoint(mouse_pos)
                if tile_clicked:
                    # self._print_tile_data(tile)                   # FOR DEBUG
                    if self.selected_unit:
                        self._move_selected_unit(tile)
                    break



    def _check_unit_clicks(self, mouse_pos):
        """check if a unit has been clicked"""
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
                    determine_range(self, unit)
                    self._update_screen()
                break



    def _check_button_clicks(self, mouse_pos):
        """check if a button has been clicked"""
        turn_button_g_clicked = self.turn_button_g.rect.collidepoint(mouse_pos)
        turn_button_m_clicked = self.turn_button_m.rect.collidepoint(mouse_pos)
        laser_button_clicked = self.laser_button.rect.collidepoint(mouse_pos)

        if turn_button_g_clicked and self.team_green_turn:
            self._increment_turn()
        elif turn_button_m_clicked and not self.team_green_turn:
            self._increment_turn()
        elif laser_button_clicked and self.laser_button.visible:
            print('pew pew')



    def _increment_turn(self):
        """end the turn"""
        # swap the turn buttons
        self.turn_button_g.visible = not self.turn_button_g.visible
        self.turn_button_m.visible = not self.turn_button_m.visible

        # deselect the selected unit
        if self.selected_unit:
            self.selected_unit.deselect(self)

        # assign temp names to the teams
        if self.team_green_turn:
            old_team = self.team_green
            new_team = self.team_magenta
        else:
            old_team = self.team_magenta
            new_team = self.team_green

        # reset action points
        for unit in old_team:
            if unit.current_ap >= 2:
                unit.current_ap = -2
            elif unit.current_ap == 1:
                unit.current_ap = -1
            else: unit.current_ap = 0
        for unit in new_team:
            unit.current_ap = 3

        # wrap up
        self.game_map.clear_highlights()
        self.team_green_turn = not self.team_green_turn
        self.turn_number += 1
        self._update_screen()



    def _move_selected_unit(self, tile):
        """move the selected unit to its chosen tile"""
        if tile.type == 'wall' or tile.occupied: return
        if not tile.hilite_b and not tile.hilite_y and not tile.hilite_r: return

        self.game_map.clear_highlights()

        # add animation here if desired
        self.selected_unit.rect.x = tile.rect.x
        self.selected_unit.rect.y = tile.rect.y

        # unflag the old tile, assign the new tile to the unit, flag the new tile
        self.selected_unit.tile.occupied = False
        self.selected_unit.tile = tile
        self.selected_unit.tile.occupied = True

        # charge the unit one action point
        self.selected_unit.current_ap -= 1



    def _create_teams(self):
        """place the units on the map"""
        tile_size = self.settings.tile_size
        self.team_green = pygame.sprite.Group()
        self.team_magenta = pygame.sprite.Group()

        for start_position in self.game_map.start_positions:
            # find the tile associated with this position
            row = start_position[0]['row']
            col = start_position[0]['col']
            tile = self.game_map.tiles[row][col]

            # interpret the ASCII codes
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

            # place the unit
            unit.rect.x = (col + 0.5) * tile_size
            unit.rect.y = (row + 0.5) * tile_size

            # assign the tile to the unit
            unit.tile = tile

            # add unit to the proper team
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

        # make the fire button visible if applicable
        # move this section to the place where it's triggered
        if self.selected_unit and self.selected_unit.current_ap > 0:
            self.laser_button.visible = True
        else:
            self.laser_button.visible = False

        # draw any visible buttons
        for button in self.buttons:
            if button.visible:
                button.draw_button()

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