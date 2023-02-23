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

from settings import Settings
from game_map import GameMap
from button_frame import ButtonFrame, Button
from lf_functions import (Point, Line, D6, game_caption, swap)


class LaserFlag:
    """overall class to manage game assets and behavior"""

    def __init__(self, map_file):
        """initialize game and create resources"""
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode(
                (self.settings.screen_width, self.settings.screen_height))
        res = f"{self.settings.screen_width}x{self.settings.screen_height}"
        pygame.display.set_caption(game_caption())

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

        self.turn_button  = {}
        self.score_label  = {}
        self.status_label = {}

        # create the buttons; use buttons for score labels too
        self.turn_button['g'] = Button(self, msg="END TURN",
            color=self.settings.team_g_color, text_color='blue',
            border_color='blue', border_weight = 2,
            grid_position=(3, 1), width=3)

        self.score_label['g'] = Button(self, msg='0',
            color=self.settings.team_g_color, text_color='black',
            border_color='black', border_weight = 5,
            grid_position=(2, 3), width=5, height=2, font_factor = 1.5)

        self.status_label['g'] = Button(self, msg='',
            color=self.settings.team_g_color, text_color='black',
            border_color='black', border_weight = 5,
            grid_position=(1, 6), width=7, height=3, font_factor=0.55)

        self.turn_button['m'] = Button(self, msg="END TURN",
            color=self.settings.team_m_color, text_color='yellow',
            border_color='yellow', border_weight = 2,
            grid_position=(3, 19), width=3, visible=False)

        self.score_label['m'] = Button(self, msg='0',
            color=self.settings.team_m_color, text_color='black',
            border_color='black', border_weight = 5,
            grid_position=(2, 16), width=5, height=2, font_factor = 1.5)

        self.status_label['m'] = Button(self, msg='',
            color=self.settings.team_m_color, text_color='black',
            border_color='black', border_weight = 5,
            grid_position=(1, 12), width=7, height=3, font_factor=0.55)

        self.laser_button = Button(self, "FIRE LASER (roll D6 + D6)",
            color='red', text_color='yellow',
            border_color='yellow', border_weight = 2,
            grid_position=(0.5, 10), width=8, visible=False)


        self.buttons = (
            self.turn_button['g'],
            self.score_label['g'],
            self.status_label['g'],
            self.turn_button['m'],
            self.score_label['m'],
            self.status_label['m'],
            self.laser_button
        )

        # initialize the game board for the first turn
        self.selected_unit   = None
        self.targeted_unit   = None
        self.sight_line      = None
        self.targets_visible = False
        self.turn_number     = 1
        self.teams           = {'g': pygame.sprite.Group(),
                                'm': pygame.sprite.Group()}
        self.scores          = {'g': 0,
                                'm': 0}
        self.active_team     =  'g'
        self.inactive_team   =  'm'
        self.game_map.build_teams(self)
        self._generate_background_lasers()
        self._update_screen()

################################################################################
# MAIN GAME LOOP
################################################################################

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
                print(f'key pressed')
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_tile_clicks(mouse_pos)
                self._check_unit_clicks(mouse_pos)
                self._check_button_clicks(mouse_pos)


    def _check_button_clicks(self, mouse_pos):
        """check if a button has been clicked"""
        turn_button_clicked = {}
        laser_button_clicked  = self.laser_button.rect.collidepoint(mouse_pos)
        turn_button_g_clicked = self.turn_button['g'].rect.collidepoint(mouse_pos)
        turn_button_m_clicked = self.turn_button['m'].rect.collidepoint(mouse_pos)
        if laser_button_clicked and self.laser_button.visible:
            self._fire_laser()
        elif ((turn_button_g_clicked and self.active_team == 'g') or
             (turn_button_m_clicked and self.active_team == 'm')
        ):
            self._increment_turn()


    def _check_tile_clicks(self, mouse_pos):
        """check if a map tile has been clicked"""
        # CLEAN THIS UP ONCE AVAILABEL TILES ARE PUT INTO UNIT DEF
        for row in self.game_map.tiles:
            for tile in row:
                tile_clicked = tile.rect.collidepoint(mouse_pos)
                if tile_clicked:
                    self._print_tile_data(tile, mouse_pos)                   # FOR DEBUG
                    if (self.selected_unit and
                        tile.hilited and not
                        tile.occupied
                    ):
                        self.selected_unit.move(self, tile)
                        self._clear_targets()
                        self.game_map.clear_highlights()
                        self.game_map.clear_marks()
                        self._update_screen()
                    break


    def _check_unit_clicks(self, mouse_pos):
        """check if a unit has been clicked"""
        # if friendly unit is clicked on
        for unit in self.teams[self.active_team]:
            unit_clicked = unit.rect.collidepoint(mouse_pos)
            if unit_clicked:
                self._on_select_unit(unit)
        # if enemy unit is clicked on
        for unit in self.teams[self.inactive_team]:
            unit_clicked = unit.rect.collidepoint(mouse_pos)
            if unit_clicked:
                self._on_target_unit(unit)


    def _increment_turn(self):
        """end the turn"""
        # swap the turn buttons
        self.turn_button['g'].visible = not self.turn_button['g'].visible
        self.turn_button['m'].visible = not self.turn_button['m'].visible
        # deselect the selected unit
        if self.selected_unit:
            self.selected_unit.selected = False
        # swap active teams
        self.active_team, self.inactive_team = swap(
            self.active_team, self.inactive_team)
        # set the now inactive team's overwatch mode
        for unit in self.teams[self.inactive_team]:
            unit.finish_charging()
            # regular mode
            if unit.laser_uncharged:
                unit.current_ap = 0
            elif unit.current_ap >= 2:
                unit.current_ap = -2
            # snapshot mode
            elif unit.current_ap == 1:
                unit.current_ap = -1
        # refill the now active team's action points
        for unit in self.teams[self.active_team]:
            unit.current_ap = 3
        # wrap up
        self.status_label['g'].prep_msg('')
        self.status_label['m'].prep_msg('')
        self._generate_background_lasers()
        self.turn_number += 1
        self.game_map.clear_highlights()
        self.game_map.clear_marks()
        self._clear_targets()
        self._update_screen()


    def _quit_game(self):
        """ends the game"""
        sys.exit()

################################################################################
# UNIT AND TARGET SELECTION
################################################################################

    def _on_select_unit(self, unit):
        self.game_map.clear_highlights()
        # if the clicked unit is currently selected, deselect it
        if unit.selected:
            self._unselect()
        # if the clicked unit has any AP remaining, select it
        elif unit.current_ap > 0:
            self._select_unit(unit)


    def _select_unit(self, unit):
        """select the chosen unit"""
        # clear the current selection
        if self.selected_unit:      self.selected_unit.selected = False
        # select the chosen unit
        self.selected_unit = unit
        self.selected_unit.selected = True

        # update the status labels
        # NEED TO ADD LABELS FOR TARGET
        # {TYPE} IN COVER / NOT IN COVER
        # ELEVATED / LEVEL GROUND
        # MOVE ALL THIS TO A NEW METHOD
        # NEED ONE METHOD TO DETERMINE ALL ATTACK & DEFENSE BONUSES
        to_hit = unit.to_hit + unit.current_attack_bonus
        msg = f"{unit.unit_type.title()}: roll {to_hit} or better to hit"
        msg += '\n'
        msg += f"on {unit.tile.type} ground ("

        if unit.current_attack_bonus > 0:
            msg += '+'
        msg += f"{unit.current_attack_bonus})"
        self.status_label[unit.team].prep_msg(msg)

        # update the map
        self.game_map.clear_highlights()
        self.game_map.clear_marks()
        self._clear_targets()

        unit.show_los(self)
        unit.show_range(self)
        self._update_screen()

    def _on_target_unit(self, unit):
        if self.selected_unit:
            if unit.visible:
                # if there was a target selection already
                if self.targeted_unit != None:
                    # if the selection was this unit, deselect it
                    if unit == self.targeted_unit:
                        self.targeted_unit.targeted = False
                        self.targeted_unit = None
                    # otherwise, switch targets
                    else:
                        self.targeted_unit.targeted = False
                        self.targeted_unit = unit
                        self.targeted_unit.targeted = True
                # if there was no target selected, and this one is not already hit
                #   select this unit as a target
                elif not unit.laser_uncharged:
                    self.targeted_unit = unit
                    self.targeted_unit.targeted = True
        self._show_laser_button()
        self._update_screen()


    def _unselect(self):
        """deselect the selected unit"""
        # clear the current selection
        if self.selected_unit:
            self.selected_unit.selected = False
            self.selected_unit = None
        if self.targeted_unit:
            self.targeted_unit.targeted = False
            self.targeted_unit = None

        self.status_label['g'].prep_msg('')
        self.status_label['m'].prep_msg('')
        # update the map
        self.game_map.clear_highlights()
        self.game_map.clear_marks()
        self._clear_targets()
        self._update_screen()

    def _clear_targets(self):
        """clear all target information"""
        self.targeted_unit = None
        for team in self.teams.values():
            for unit in team:
                unit.visible = False
                unit.targeted = False

################################################################################
# FIRING THE LASER
################################################################################

    def _show_laser_button(self):
        # make the fire button visible if applicable
        if (self.selected_unit and
            self.targeted_unit and
            self.selected_unit.current_ap > 0
        ):
            self.laser_button.visible = True
        else:
            self.laser_button.visible = False

    def _fire_laser(self):
        """fire the selected unit's laser"""
        self.selected_unit.fire()
        self.laser_button.visible = False

        # roll dice
        roll   = [D6(), D6()]
        total  = roll[0] + roll[1]
        to_hit = self.selected_unit.to_hit
        print(f'{roll[0]} + {roll[1]} = {total} (need {to_hit})')
        if total >= to_hit:
            self.targeted_unit.hit()
            self.scores[self.selected_unit.team] += self.settings.points_per_unit
            print(f'{self.scores[self.selected_unit.team]} points for team {self.selected_unit.team}')
        else:
            print('miss')

        # animate laser
        FACTOR = 5
        if self.selected_unit.team == 'g':
            laser_color = self.settings.team_g_color
        else:
            laser_color = self.settings.team_m_color
        for i in range(0, 10):
            sight_line = choice(self.targeted_unit.sight_lines)
            pygame.draw.line(self.screen, laser_color,
                (sight_line.A.x, sight_line.A.y),
                (sight_line.B.x, sight_line.B.y))
            pygame.display.flip()
            pygame.time.delay(int(self.settings.animation_speed / FACTOR))
            self._update_screen()
            pygame.time.delay(int(self.settings.animation_speed / FACTOR))

        self._unselect()
        self._clear_targets()
        self._update_screen()

################################################################################
# INCREMENT TURN
################################################################################



################################################################################
# BACKGROUND LASERS
################################################################################

    def _generate_background_lasers(self):
        self.background_lasers = []

        # one laser per grid tile, but randomize positions each turn
        t       = self.settings.tile_size
        h       = int(self.settings.screen_height)
        w       = int(self.settings.screen_width)
        y_tiles = h // t
        x_tiles = w // t

        # left-right lasers
        for i in range(0, y_tiles):
            left_y  = choice(range(0, h))
            right_y = choice(range(0, h))
            A       = Point(0, left_y)
            B       = Point(w, right_y)
            line    = Line(A, B)
            self.background_lasers.append(line)

        # up-down lasers
        for i in range(0, x_tiles):
            top_x = choice(range(0, w))
            bot_x = choice(range(0, w))
            A     = Point(top_x, 0)
            B     = Point(bot_x, h)
            line  = Line(A, B)
            self.background_lasers.append(line)

    def _draw_background_lasers(self):
        if self.active_team == 'g':
            laser_color = self.settings.team_g_color
        else:
            laser_color = self.settings.team_m_color
        for line in self.background_lasers:
            pygame.draw.line(self.screen, laser_color,
                (line.A.x, line.A.y), (line.B.x, line.B.y))

################################################################################
# UPDATE SCREEN
################################################################################

    def _update_screen(self):
        """update images on the screen, and flip to the new screen"""
        self.score_label['g'].prep_msg(str(self.scores['g']))
        self.score_label['m'].prep_msg(str(self.scores['m']))
        # draw the background color
        self.screen.fill(self.settings.bg_color)
        # draw lasers in the background
        self._draw_background_lasers()
        # draw the map
        self.game_map.draw_map()
        # draw the units
        for unit in self.teams['g']:
            unit.blitme()
        for unit in self.teams['m']:
            unit.blitme()
        # draw the button frame
        self.button_frame.draw_frame()
        # draw any visible buttons
        for button in self.buttons:
            if button.visible:
                button.draw_button()
        # make the most recently drawn screen visible
        pygame.display.flip()

        # # USE THIS PRINT LINE TO DEBUG; THIS FUNCTION
        # # PROBABLY GETS CALLED MORE THEN NEEDED
        # print("updating screen...")



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

        print(f'N side: {tile.N.y} S side: {tile.S.y}')
        print(f'E side: {tile.E.x} W side: {tile.W.x}')
        print(f'NE corner: ({tile.NE.x}, {tile.NE.y})')
        print(f'NW corner: ({tile.NW.x}, {tile.NW.y})')
        print(f'SE corner: ({tile.SE.x}, {tile.SE.y})')
        print(f'SW corner: ({tile.SW.x}, {tile.SW.y})')
        print(f'center   : ({tile.CEN.x}, {tile.CEN.y})')
        print(f'mouse position: {mouse_pos}')


################################################################################

map_list = [
    'maps/map_01.dat',
    'maps/map_02.dat'
]

if __name__ == '__main__':
    lf = LaserFlag(map_list[0])
    lf.run_game()