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

################################################################################
# BUILD A MAIN MENU AND MAP LOADER
################################################################################

map_list = [
    'maps/map_01.dat',
    'maps/map_02.dat'
]
current_map = map_list[0]

################################################################################

import sys
from random import choice
import pygame

from settings import Settings
from game_map import GameMap
from button_frame import ButtonFrame, Button
from lf_functions import Point, Line, D6, game_caption, swap


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
        self.button_frame.create_buttons(self)
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



        # to track the user selection
        self.selected_unit      = None
        self.targeted_unit      = None
        # to store the selection when viewing enemy overwatch zones
        self.temp_selected_unit = None

        # tracking to_hit numbers
        self.to_hit = {'to-hit'  : self.settings.base_to_hit,   # MAKE THIS A METHOD
            'elevated_hit_bonus' : 0,
            'cover_defense_bonus': 0,
            'elev_defense_malus' : 0,
            'total'              : 0}

        # initialize the game board for the first turn
        self.turn_number     = 1
        self.all_units       = []
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
                self._update_screen()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_tile_clicks(mouse_pos)
                self._check_unit_clicks(mouse_pos)
                self._check_button_clicks(mouse_pos)
                self._update_screen()
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()
                self._check_button_unclicks(mouse_pos)


    def _check_button_clicks(self, mouse_pos):
        """check if a button has been clicked"""
        # turn_button_clicked = {}
        laser_button_clicked  = self.laser_button.rect.collidepoint(mouse_pos)
        turn_button_g_clicked = self.turn_button['g'].rect.collidepoint(mouse_pos)
        turn_button_m_clicked = self.turn_button['m'].rect.collidepoint(mouse_pos)
        if laser_button_clicked and self.laser_button.visible:
            self._fire_laser()

        elif ((turn_button_g_clicked and self.active_team == 'g') or
              (turn_button_m_clicked and self.active_team == 'm')
        ):
            self._increment_turn()

        elif ((turn_button_g_clicked and self.inactive_team == 'g') or
              (turn_button_m_clicked and self.inactive_team == 'm')
        ):
            self.temp_selected_unit = self.selected_unit
            self._show_inactive_los()



    def _check_button_unclicks(self, mouse_pos):
        """clear enemy LOS when button released"""
        turn_button_g_unclicked = self.turn_button['g'].rect.collidepoint(mouse_pos)
        turn_button_m_unclicked = self.turn_button['m'].rect.collidepoint(mouse_pos)
        if ((turn_button_g_unclicked and self.inactive_team == 'g') or
            (turn_button_m_unclicked and self.inactive_team == 'm')
        ):
            self._clear_selection()
            if self.temp_selected_unit:
                self._on_click_unit(self.temp_selected_unit)
                self.temp_selected_unit = None
            self._update_screen()

    def _check_tile_clicks(self, mouse_pos):
        """check if a map tile has been clicked"""
        # CLEAN THIS UP ONCE AVAILABLE TILES ARE PUT INTO UNIT DEF
        for row in self.game_map.tiles:
            for tile in row:
                tile_clicked = tile.rect.collidepoint(mouse_pos)
                if tile_clicked:
                    self._print_tile_data(tile, mouse_pos)                   # FOR DEBUG


                    # move the selected unit if all conditions are met
                    if (self.selected_unit and
                        tile.hilited and
                        self.selected_unit.can_move and not
                        tile.occupied
                    ):
                        self.selected_unit.move(self, tile)
                        self.game_map.clear_highlights_and_marks()
                        self._clear_selection()
                    break


    def _check_unit_clicks(self, mouse_pos):
        """check if a unit has been clicked"""
        # if friendly unit is clicked on
        for unit in self.teams[self.active_team]:
            unit_clicked = unit.rect.collidepoint(mouse_pos)
            if unit_clicked:
                self._on_click_unit(unit)
        # if VISIBLE enemy unit is clicked on
        for unit in self.teams[self.inactive_team]:
            unit_clicked = unit.rect.collidepoint(mouse_pos)
            if unit_clicked and unit.visible:
                self._on_click_target(unit)


    def _quit_game(self):
        """ends the game"""
        sys.exit()

################################################################################
# INCREMENT TURN
################################################################################

    def _increment_turn(self):
        """end the turn"""
        self._clear_selection()
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

            if unit.current_ap > unit.max_overwatch:
                unit.current_ap = unit.max_overwatch
            if unit.laser_uncharged:
                unit.current_ap = 0
            unit.current_ap = -unit.current_ap

        # refill the now active team's action points and action flags
        for unit in self.teams[self.active_team]:
            unit.current_ap = 3
            unit.can_move   = True
            unit.can_fire   = True
        # wrap up
        self.status_label['g'].prep_msg('')
        self.status_label['m'].prep_msg('')
        self._generate_background_lasers()
        self.turn_number += 1
        self.to_hit = None
        self.game_map.clear_highlights_and_marks()

################################################################################
# UNIT AND TARGET SELECTION
################################################################################

    def _on_click_unit(self, clicked_unit):
        """when a friendly unit is clicked"""
        # clear active team status window
        self.status_label[self.active_team].prep_msg('')
        # if the clicked unit was already selected, just deselect it
        if clicked_unit.selected:
            self._clear_selection()
            return
        # otherwise select this unit
        self._clear_selection()
        self.selected_unit = clicked_unit
        self.selected_unit.selected = True
        # update active team status window
        self._calc_to_hit()
        plus_string = ''
        if self.to_hit['elevated_hit_bonus'] == 0:
            plus_string += "+"
        msg =  f"{clicked_unit.unit_class.title()}: "
        msg += f"base roll {self.to_hit['to-hit']} to hit\n"
        msg += f" on {clicked_unit.tile.type} ground "
        msg += f"({plus_string}{self.to_hit['elevated_hit_bonus']})"
        self.status_label[self.active_team].prep_msg(msg)
        # update the map
        self.game_map.clear_highlights_and_marks()
        self.game_map.show_los(self, clicked_unit)
        if clicked_unit.can_move:
            self.game_map.show_range(self, clicked_unit) # needs access to a protected class to do the animation - not ideal



    def _on_click_target(self, clicked_unit):
        """when an enemy unit is clicked"""
        # clear inactive team status window
        self.status_label[self.inactive_team].prep_msg('')
        # if the clicked unit was already targeted, just untarget it
        if clicked_unit.targeted:
            self._clear_target()
            return
        # otherwise select this unit
        self._clear_target()
        self.targeted_unit = clicked_unit
        self.targeted_unit.targeted = True
        # if a friendly unit (with active laser) is selected and in range,
        #   show the laser button and calculate hit chance
        if (self.selected_unit and not
            self.selected_unit.laser_uncharged and not
            self.selected_unit.laser_charging and
            clicked_unit.visible
        ):
            self._show_laser_button()
            self._calc_to_hit()
        # update inactive team status window
        self._calc_to_hit()
        not_string = ''
        plus_string = ''
        if self.to_hit['cover_defense_bonus'] == 0:
            not_string = 'NOT '
        if self.to_hit['elev_defense_malus'] == 0:
            plus_string = '+'
        msg =  f"{clicked_unit.unit_class.title()} "
        msg += f"on {clicked_unit.tile.type} ground "
        msg += f"({plus_string}{self.to_hit['elev_defense_malus']})\n"
        msg += f"{not_string}in cover (+{self.to_hit['cover_defense_bonus']})"
        self.status_label[self.inactive_team].prep_msg(msg)


    def _clear_selection(self):
        """deselect the selected unit"""
        # reset the to_hit dictionary   # MAKE THIS A METHOD
        self.to_hit = {'to-hit'  : self.settings.base_to_hit,
            'elevated_hit_bonus' : 0,
            'cover_defense_bonus': 0,
            'elev_defense_malus' : 0}
        # clear the current selection
        if self.selected_unit:
            self.selected_unit.selected = False
            self.selected_unit = None
        # unflag all visible units
        for team in self.teams.values():
            for unit in team:
                unit.visible = False
        # clear status label and fire button
        self.status_label[self.active_team].prep_msg('')
        self.laser_button.visible = False
        # clear the target too since it's a new selection
        self._clear_target()
        # update the map
        self.game_map.clear_highlights_and_marks()

    def _clear_target(self):
        """deselect the selected target"""
        # reset the to_hit dictionary   # MAKE THIS A METHOD
        self.to_hit = {'to-hit'  : self.settings.base_to_hit,
            'elevated_hit_bonus' : 0,
            'cover_defense_bonus': 0,
            'elev_defense_malus' : 0,
            'total'              : 0}
        # clear the selected target
        if self.targeted_unit:
            self.targeted_unit.targeted = False
            self.targeted_unit = None
        # clear status label and fire button
        self.status_label[self.inactive_team].prep_msg('')
        self.laser_button.visible = False

################################################################################
# OVERWATCH MODE
################################################################################

    def _show_inactive_los(self):
        """show the inactive team's sight lines"""
        self._clear_selection()
        for unit in self.teams[self.inactive_team]:
            if unit.current_ap < 0:
                self.game_map.show_los(self, unit)

################################################################################
# FIRING THE LASER
################################################################################


    def _calc_to_hit(self):
        """calculate the current to-hit requirements"""
        shooter = self.selected_unit
        self.to_hit['to-hit'] = shooter.to_hit

        # if shooter is on elevated ground
        if shooter.elevated:
            self.to_hit['elevated_hit_bonus']  = shooter.elevated_hit_bonus

        if self.targeted_unit:
            target = self.targeted_unit

            # if target is in cover
            if target.is_in_cover(shooter):
                self.to_hit['cover_defense_bonus'] = target.cover_defense_bonus

            # if target is on elevated ground
            if self.targeted_unit.elevated:
                self.to_hit['elev_defense_malus']  = target.elev_defense_malus

        self.to_hit['total'] = (self.to_hit['to-hit'] +
                                self.to_hit['elevated_hit_bonus'] +
                                self.to_hit['cover_defense_bonus'] +
                                self.to_hit['elev_defense_malus'])

        # print(f"             to-hit: {self.to_hit['to-hit']}"             )
        # print(f" elevated_hit_bonus: {self.to_hit['elevated_hit_bonus']}" )
        # print(f"cover_defense_bonus: {self.to_hit['cover_defense_bonus']}")
        # print(f" elev_defense_malus: {self.to_hit['elev_defense_malus']}" )
        # print(f"              total: {self.to_hit['total']}"              )



    def _show_laser_button(self):

        self._calc_to_hit()
        msg = f"FIRE LASER (roll {self.to_hit['total']} or more)"
        self.laser_button.prep_msg(msg)


        # make the fire button visible if applicable
        if (self.selected_unit and
            self.targeted_unit and
            self.selected_unit.can_fire and
            self.selected_unit.current_ap > 0
        ):
            self.laser_button.visible = True
        else:
            self.laser_button.visible = False

    def _fire_laser(self):
        """fire the selected unit's laser"""
        self.selected_unit.fire()

        # roll dice
        roll  = [D6(), D6()]
        total = roll[0] + roll[1]
        msg = f"{roll[0]} + {roll[1]} = {total}"
        self._calc_to_hit()
        if total >= self.to_hit['total']:
            self.targeted_unit.hit()
            self.scores[self.selected_unit.team] += self.settings.points_per_unit
            msg += (f' (HIT) (needed {self.to_hit["total"]})')
        else:
            msg += (f' (MISS) (needed {self.to_hit["total"]})')
        self.laser_button.prep_msg(msg)

        # animate laser
        source_tile = self.selected_unit.tile
        target_tile = self.targeted_unit.tile
        line_dict   = self.selected_unit.visible_tiles
        sight_line  = line_dict[target_tile]
        laser_color = self.settings.team_color[self.active_team]

        # draw a few lasers and take enough time to read the hit message
        for i in range(0, 25):
            pygame.draw.line(self.screen, laser_color,
                (sight_line.A.x, sight_line.A.y),
                (sight_line.B.x, sight_line.B.y))
            pygame.display.flip()
            pygame.time.delay(int(self.settings.animation_speed))
            self._update_screen()
            pygame.time.delay(int(self.settings.animation_speed))

        self._clear_selection()
        self.laser_button.visible = False

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
            button.draw_button()

        # make the most recently drawn screen visible
        pygame.display.flip()

        # # USE THIS PRINT LINE TO DEBUG; THIS FUNCTION
        # # PROBABLY GETS CALLED MORE THEN NEEDED
        # print("updating screen...")

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
        laser_color = self.settings.team_color[self.active_team]

        for line in self.background_lasers:
            pygame.draw.line(self.screen, laser_color,
                (line.A.x, line.A.y), (line.B.x, line.B.y))

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
        print(f'ID: {tile.ID}')

################################################################################

if __name__ == '__main__':
    lf = LaserFlag(current_map)
    lf.run_game()