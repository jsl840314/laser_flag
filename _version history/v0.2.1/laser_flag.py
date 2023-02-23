"""
Laser Flag is a strategy game for two players. Each player controls a team of
units equipped with laser taggers. Each team may have one or more bases, or no
base. Each unit is one of three classes:
    Snipers are accurate shooters but slow movers
    Scouts are fast movers but poor shooters
    Grunts take better advantage of cover

If its line of sight is not blocked by a wall, a unit can fire its laser at
enemy units or enemy bases to score points. Line of sight is not blocked by
bases or other units.

Bases are worth more points but are not affected by the laser.

If a unit is hit by an enemy laser, he must touch his own base to reactivate it.
If the map contains no bases for that unit's team, the unit is eliminated from
the game and removed from the map.

Point values and victory conditions are specified in individual map files:
    number of turns can be limited

"""
import sys
from random import choice
import pygame

import lf_functions as func
from settings import Settings
from game_map import GameMap
from button_frame import ButtonFrame, Button
from units import PlainUnit, Sniper, Grunt, Scout

TITLE   = 'Laser Flag'
VERSION = '0.2.1'
CDATE   = '2/10/2023'
AUTHOR  = 'Jesse Stuart Leitch'

class LaserFlag:
    """overall class to manage game assets and behavior"""

    def __init__(self, map_file):
        """initialize game and create resources"""
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode(
                (self.settings.screen_width, self.settings.screen_height))
        res = f"{self.settings.screen_width}x{self.settings.screen_height}"
        self.caption = f"{TITLE} v.{VERSION} \u00A9{CDATE} by {AUTHOR} ({res})"
        pygame.display.set_caption(self.caption)

        # initialize the main display regions
        self.button_frame = ButtonFrame(self)
        self.game_map = GameMap(self, map_file)

        # build the wall list (self.game_map.walls is a list of lists)
        self.walls = []
        for row in self.game_map.walls:
            for wall in row:
                self.walls.append(wall)

        # build the tile list (self.game_map.tiles is a list of lists
        self.tiles = []
        for row in self.game_map.tiles:
            for tile in row:
                self.tiles.append(tile)

        # create the buttons
        self.turn_button_g = Button(self, msg="END TURN",
            color=self.settings.team_g_color, text_color='white',
            border_color='white', border_weight = 2,
            grid_position=(2, 1), width=5)
        self.turn_button_m = Button(self, msg="END TURN",
            color=self.settings.team_m_color, text_color='white',
            border_color='white', border_weight = 2,
            grid_position=(2, 19), width=5, visible=False)
        self.laser_button = Button(self, "LASER",
            color='red', text_color='black',
            border_color='black', border_weight = 2,
            grid_position=(3, 10), width=3, visible=False)
        self.buttons = [
            self.turn_button_g,
            self.turn_button_m,
            self.laser_button
        ]

        # initialize the game board for the first turn
        self.selected_unit   = None
        self.team_green_turn = True
        self.turn_number     = 1
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
            elif event.type == pygame.KEYDOWN:
                print('test')
                self.game_map.clear_marks()
                self._update_screen()
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
                    # self._print_tile_data(tile, mouse_pos)                   # FOR DEBUG
                    if self.selected_unit and not tile.occupied:
                        self.selected_unit.move(self, tile)
                    break


    def _check_unit_clicks(self, mouse_pos):
        """check if a unit has been clicked"""
        # CLEAN THIS UP WITH A DICTIONARY
        if self.team_green_turn:
            team       = self.teams['g']
            enemy_team = self.teams['m']
            # enemy_bases = self.game_map.bases_m
        else:
            team       = self.teams['m']
            enemy_team = self.teams['g']
            # enemy_bases = self.game_map.bases_g

        for unit in team:
            unit_clicked = unit.rect.collidepoint(mouse_pos)
            if unit_clicked:
                self.game_map.clear_highlights()
                # if the clicked unit is currently selected, deselect it
                if unit.selected:
                    self._unselect()
                # if the clicked unit has any AP remaining, select it
                elif unit.current_ap > 0:
                    self._select_unit(unit)
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


    def _create_teams(self):
        """place the units on the map"""
        tile_size = self.settings.tile_size
        self.teams = {'g': pygame.sprite.Group(),
                      'm': pygame.sprite.Group()}

        for start_position in self.game_map.start_positions:
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
            unit.tile = self.game_map.tiles[row][col]

            # place the unit
            unit.rect.x = (col + 0.5) * tile_size
            unit.rect.y = (row + 0.5) * tile_size
            unit.tile.occupied = True

            # add unit to the proper team
            team = unit.team
            self.teams[team].add(unit)

            # team magenta begins the game on overwatch
            if unit.team == 'm':
                unit.current_ap = -2


    def _select_unit(self, unit):
        """select the chosen unit"""
        # clear the current selection
        if self.selected_unit:      self.selected_unit.selected = False
        # select the chosen unit
        self.selected_unit = unit
        self.selected_unit.selected = True
        # update the map
        self.game_map.clear_marks()
        self._clear_targets()
        func.determine_range(self)
        func.find_targets(self)
        func.show_los(self)
        self._update_screen()


    def _unselect(self):
        """deselect the selected unit"""
        # clear the current selection
        self.selected_unit.selected = False
        self.selected_unit = None
        # update the map
        self.game_map.clear_marks()
        self._clear_targets()
        self._update_screen()


    def _clear_targets(self):
        """clear all target information"""
        for team in self.teams.values():
            for unit in team:
                unit.targeted = False


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
            old_team = self.teams['g']
            new_team = self.teams['m']
        else:
            old_team = self.teams['m']
            new_team = self.teams['g']

        # set old team's overwatch mode
        for unit in old_team:
            # regular mode
            if unit.current_ap >= 2:
                unit.current_ap = -2
            # snapshot mode
            elif unit.current_ap == 1:
                unit.current_ap = -1

        # refill the new team's action points
        for unit in new_team:
            unit.current_ap = 3

        # wrap up
        self.turn_number += 1
        self.team_green_turn = not self.team_green_turn
        self.game_map.clear_highlights()
        self.game_map.clear_marks()
        self._clear_targets()
        self._update_screen()



    def _update_screen(self):
        """update images on the screen, and flip to the new screen"""

        # draw the background color
        self.screen.fill(self.settings.bg_color)

        # # draw lasers in the background
        # # move this elsewhere so it only regens once per turn
        # # make the lasers match the team color
        # # one laser per grid tile, but randomize positions eact turn
        # h = int(self.settings.screen_height)
        # w = int(self.settings.screen_width)
        # for i in range(0, 10):
        #     y1 = choice(range(0, h))
        #     y2 = choice(range(0, h))
        #     color = choice(['cyan', 'red'])
        #     pygame.draw.line(self.screen, color, (0, y1), (w, y2))
        # for i in range(0, 10):
        #     x1 = choice(range(0, w))
        #     x2 = choice(range(0, w))
        #     color = choice(['cyan', 'red'])
        #     pygame.draw.line(self.screen, color, (x1, 0), (x2, h))

        # draw the map
        self.game_map.draw_map()

        # draw the units
        for unit in self.teams['g']:
            unit.blitme()
        for unit in self.teams['m']:
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

    def _print_tile_data(self, tile, mouse_pos):
        """display info about the selected tile"""

        print(f'row: {tile.row}   col: {tile.col}')
        print(f'type: {tile.type}')
        print(f'occupied: {tile.occupied}')
        print("Adjoiners:")
        print(f"N: {tile.adjoiners['n'].type}  S: {tile.adjoiners['s'].type}  E: {tile.adjoiners['e'].type}  W: {tile.adjoiners['w'].type}")
        print(f"NE: {tile.adjoiners['ne'].type} SE: {tile.adjoiners['se'].type} NW: {tile.adjoiners['nw'].type} SW: {tile.adjoiners['sw'].type}")
        print(f'side n: {tile.n} side s: {tile.s}')
        print(f'side e: {tile.e} side w: {tile.w}')
        print(f'corner ne: {tile.ne} corner nw: {tile.nw}')
        print(f'corner se: {tile.se} corner sw: {tile.sw}')
        print(f'center: {tile.center}')
        print(f'mouse position: {mouse_pos}')


################################################################################

map_list = [
    'maps/map_01.dat',
    'maps/map_02.dat'
]

if __name__ == '__main__':
    lf = LaserFlag(map_list[0])
    lf.run_game()