################################################################################

import os
import sys
import random
import pygame

from settings import Settings
from game_map import GameMap
from button_frame import ButtonFrame, Button
from lf_functions import (Point, Line, D6, game_caption, swap,
    tile_direction, determine_range, CARDINALS)
from rules import Rules
from laser import Laser



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

        # don't show the rules frame
        self.rules = Rules(self)
        self.show_rules = False

        # don't show the roll result
        self.show_roll_result = False

        # track if running overwatch mode
        self.overwatch_mode = False
        self.overwatch_list = []

        # to track the user selection
        self.selected_unit      = None
        self.targeted_unit      = None
        # # to store the selection when viewing enemy overwatch zones
        # self.temp_selected_unit = None

        # initialize the dictionary of to-hit variables for roll display
        self._clear_to_hit()

        # initialize the game board for the first turn
        self.turn_number     = 1
        self.all_units       = []
        self.teams           = {'g': pygame.sprite.Group(),
                                'm': pygame.sprite.Group()}
        self.scores          = {'g': 0,
                                'm': 0}
        self.active_team     =  'g'
        self.inactive_team   =  'm'
        self.showing_inactive_los = False
        self.game_map.build_teams(self)
        self._generate_background_lasers()
        self._update_screen('init')



################################################################################
# MAIN GAME LOOP
################################################################################



    def run_game(self):
        """the main game loop"""
        while True:
            self._check_events()
            if self.overwatch_mode and not self.show_roll_result:
                self._next_overwatch()



    def _check_events(self):
        """respond to keypresses & mouse events"""
        for event in pygame.event.get():

            # if click on window X?
            if event.type == pygame.QUIT:
                self._quit_game()


            # if keypress, quit game or clear selection
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self._quit_game()
                self._clear_selection()
                self._update_screen()


            # if mouse click
            elif event.type == pygame.MOUSEBUTTONDOWN:

                # if the rules pane was open, just close it
                if self.show_rules:
                    self.show_rules = False

                # if a roll result was shown, just clear it
                elif self.show_roll_result:
                    self._hide_roll_result()

                # otherwise, check the buttons and map
                else:
                    mouse_pos = pygame.mouse.get_pos()
                    self._check_button_clicks(mouse_pos)
                    self._check_unit_clicks(mouse_pos)
                    self._check_tile_clicks(mouse_pos)

                # # then update the screen
                # NOT NEEDED BECAUSE WE UPDATE ON UNCLICK
                # self._update_screen('check events, on mouse click')

            # if mouse release
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()
                self._check_button_unclicks(mouse_pos)



    def _check_button_clicks(self, mouse_pos):
        """check if a button has been clicked"""
        turn_button_clicked = {}
        for team in self.teams:
            turn_button_clicked[team] = (
                self.turn_button[team].rect.collidepoint(mouse_pos))
        rules_button_clicked = self.rules_button.rect.collidepoint(mouse_pos)
        laser_button_clicked = self.laser_button.rect.collidepoint(mouse_pos)

###############################  FIRE THE LASER  ###############################
        if laser_button_clicked and self.laser_button.visible:
            self._fire_laser(self.selected_unit, self.targeted_unit)
            self._begin_overwatch()

        # show the rules screen
        elif rules_button_clicked and not self.laser_button.visible:
            self.show_rules = True

        # end the turn
        elif turn_button_clicked[self.active_team]:
            self._increment_turn()

        # flash enemy team's overwatch zones
        elif turn_button_clicked[self.inactive_team]:
            self._show_inactive_los()



    def _check_button_unclicks(self, mouse_pos):
        """clear enemy LOS when button released"""
        if self.showing_inactive_los == True:
            self.showing_inactive_los = False
            self._clear_selection()
        self._update_screen('check button unclicks')



    def _check_unit_clicks(self, mouse_pos):
        """check if a unit has been clicked"""

        # if ACTIVE unit is clicked on
        for unit in self.teams[self.active_team]:
            unit_clicked = unit.rect.collidepoint(mouse_pos)
            if unit_clicked:
                self._on_click_unit(unit)

        # if INACTIVE unit is clicked on
        for unit in self.teams[self.inactive_team]:
            unit_clicked = unit.rect.collidepoint(mouse_pos)
            if unit_clicked:
                self._on_click_target(unit)



    def _check_tile_clicks(self, mouse_pos):
        """check if an eligible tile has been clicked (for a unit move)"""
        if not self.selected_unit: return
        for tile in self.game_map.all_tiles:

            # if the selected unit is on the tile don't do anything here
            if tile == self.selected_unit.tile: continue

            tile_clicked = tile.rect.collidepoint(mouse_pos)
            if tile_clicked:

###########################  MOVE THE SELECTED UNIT  ###########################
                if self.selected_unit and tile.hilited:
                    self.selected_unit.move(self.game_map, tile)
                    self._update_selected_unit()
                    self._begin_overwatch()
                break



    def _quit_game(self):
        """ends the game"""
        pygame.quit()
        sys.exit()



################################################################################
# INCREMENT TURN
################################################################################



    def _increment_turn(self):
        """end the turn"""
        self._clear_selection()

        # swap the turn buttons
        for team in self.teams:
            self.turn_button[team].visible = not self.turn_button[team].visible
            self.status_label[team].prep_msg('')

        # swap active teams
        self.active_team, self.inactive_team = swap(
            self.active_team, self.inactive_team)

        # set the now inactive team's APs for overwatch mode
        for unit in self.teams[self.inactive_team]:
            unit.end_turn()

        # refill the now active team's action points and action flags
        for unit in self.teams[self.active_team]:
            unit.begin_turn()

        # wrap up
        self._generate_background_lasers()
        self.turn_number += 1



################################################################################
# UNIT AND TARGET SELECTION
################################################################################



    def _on_click_unit(self, clicked_unit):
        """when a unit of the active team is clicked"""

        # clear active team status window
        self.status_label[self.active_team].prep_msg('')

        # if unit was already selected, just clear
        if clicked_unit == self.selected_unit:
            self._clear_selection()

        # # if a current selection is active, switch it
        # elif self.selected_unit:
        #     self._clear_selection()
        #     self._select_unit(clicked_unit)

        # otherwise select this unit
        else:
            self._select_unit(clicked_unit)


    def _select_unit(self, clicked_unit):
        """select the clicked unit"""
        self._clear_selection()
        self.selected_unit = clicked_unit
        self.selected_unit.selected = True
        self._update_selected_unit()


    def _update_selected_unit(self):
        """when new unit is selected OR after unit move (with AP remaining)"""

        # THIS SHOULDN'T BE NEEDED HERE, FIGURE OUT WHY
        if not self.selected_unit:
            self._clear_selection()
            return

        self.game_map.clear_highlights_and_marks()

        # don't show range if unit has no AP
        if self.selected_unit.current_ap > 0 and self.selected_unit.can_move:
            determine_range(self, self.selected_unit)

        # update active team status window
        self._calc_to_hit(shooter=self.selected_unit)
        self._prep_active_message(self.selected_unit)

        # update the map marked & highlighted tiles
        self.game_map.show_los(self, self.selected_unit)
        if self.selected_unit.can_move:
            self.game_map.show_range(self, self.selected_unit)




    def _on_click_target(self, clicked_unit):
        """when a unit of the inactive team is clicked"""

        # if the clicked unit was already targeted, just untarget it
        # can't select targets if no selected unit
        # can't select targets if selected unit has no laser
        if (clicked_unit.targeted or
            not self.selected_unit or
            not self.selected_unit.laser_charged
        ):
            self._clear_target()
            return

        # if we're still here & the unit is in LOS of the current selection
        elif clicked_unit.visible:
            self._clear_target()
            self.targeted_unit = clicked_unit
            self.targeted_unit.targeted = True
            self._show_laser_button()
            self._calc_to_hit(
                shooter=self.selected_unit, target=self.targeted_unit)
            self._prep_inactive_message(
                self.selected_unit, self.targeted_unit)



    def _prep_active_message(self, shooter, target = None):#, overwatch = False):
        """place the message for the ACTIVE team's status box. Active team
        is SHOOTER during their main turn and TARGET during overwatch phase"""
        if not self.overwatch_mode:
            msg = self._shooter_message(shooter)
        else:
            msg = self._target_message(shooter, target)
        self.status_label[self.active_team].prep_msg(msg)



    def _prep_inactive_message(self, shooter, target):#, overwatch = False):
        """place the message for the INACTIVE team's status box. Only show
        when inactive unit is targeted (as TARGET) or on overwatch (as SHOOTER)"""
        if not self.overwatch_mode:
            msg = self._target_message(shooter, target)
        else:
            msg = self._shooter_message(shooter)
        self.status_label[self.inactive_team].prep_msg(msg)



    def _shooter_message(self, shooter):
        """create the message for the SHOOTER'S status box. Does not need to
        know TARGET position because it doesn't display a cover bonus"""
        msg =  f"{shooter.unit_class.title()}: "
        msg += f"base {self.to_hit['to-hit']} to hit"

        if self.overwatch_mode:
            msg += f" (+{self.to_hit['overwatch_penalty']} snapshot)\n"
        else:
            msg += '\n'

        # terrain type
        if not 'base' in shooter.tile.type:
            msg += f"  on {shooter.tile.type} ground "
        else: # NEED TO SHOW DIFFERENT BASE TYPES HERE
            msg += "  on base (level ground)"
        # add a plus symbol for 0 modifier
        plus_string = ''
        if self.to_hit['elevated_hit_bonus'] == 0:
            plus_string += "+"
        msg += f"({plus_string}{self.to_hit['elevated_hit_bonus']})\n"

        # determine all cover directions; do NOT show a roll modifier
        covered = []
        for d, direction in CARDINALS.items():
            if shooter.in_cover[d]:
                covered.append(direction)
        if covered != []:
            D = ', '.join(covered).upper()
            msg += f"  covered to {D}"
        else:
            msg += '  not in cover'

        return msg



    def _target_message(self, shooter, target):
        """create the message for the TARGET'S status box"""
        msg =  f"{target.unit_class.title()}\n"

        # terrain type
        msg += f"  on {target.tile.type} ground "

        # add a plus symbol for 0 modifier
        plus_string = ''
        if self.to_hit['elev_defense_malus'] == 0:
            plus_string = '+'
        msg += f"({plus_string}{self.to_hit['elev_defense_malus']})\n"

        # determine cover, but only for shooter's direction, and show modifier
        covered = []
        shooter_direction = tile_direction(target.tile, shooter.tile)
        for d, direction in CARDINALS.items():
            if (d in shooter_direction and
                target.in_cover[d]
            ):
                covered.append(direction)
        if covered != []:
            D = ', '.join(covered).upper()
            msg += f"  covered to {D} (+{self.to_hit['cover_defense_bonus']})"
        else:
            msg += '  not in cover'
        return msg



    def _clear_selection(self):
        """deselect the selected unit"""
        # reset the to_hit dictionary
        self._clear_to_hit()

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
        # reset the to_hit dictionary
        self._clear_to_hit()
        # clear the selected target
        if self.targeted_unit:
            self.targeted_unit.targeted = False
            self.targeted_unit = None
        # clear status label and fire button
        self.status_label[self.inactive_team].prep_msg('')
        self.laser_button.visible = False



################################################################################
# FIRING THE LASER
################################################################################



    def _clear_to_hit(self):
        """reset the to-hit dictionary"""
        self.to_hit = {'to-hit'  : self.settings.base_to_hit,
            'elevated_hit_bonus' : 0,
            'cover_defense_bonus': 0,
            'elev_defense_malus' : 0,
            'total'              : 0,
            'overwatch_penalty'  : 0}



    def _calc_to_hit(self, shooter = None, target = None):
        """calculate the current to-hit requirements"""
        self._clear_to_hit()

        if shooter:
            self.to_hit['to-hit'] = shooter.to_hit
            # if shooter is on elevated ground
            if shooter.elevated:
                self.to_hit['elevated_hit_bonus']   = shooter.elevated_hit_bonus
            # if this is an overwatch shot
            if self.overwatch_mode:
                self.to_hit['overwatch_penalty']    = shooter.overwatch_penalty

        if target:
            # if target is covered in the shooter's direction
            if target.is_in_cover(shooter):
                self.to_hit['cover_defense_bonus']  = target.cover_defense_bonus
            # if target is on elevated ground
            if target.elevated:
                self.to_hit['elev_defense_malus']   = target.elev_defense_malus

        self.to_hit['total'] = (self.to_hit['to-hit'] +
                                self.to_hit['elevated_hit_bonus'] +
                                self.to_hit['cover_defense_bonus'] +
                                self.to_hit['elev_defense_malus'] +
                                self.to_hit['overwatch_penalty'])



    def _show_laser_button(self):
        self._calc_to_hit(shooter=self.selected_unit, target=self.targeted_unit)
        msg = f"FIRE LASER (roll {self.to_hit['total']} or more)"
        self.laser_button.prep_msg(msg)
        # make the fire button visible if applicable
        if (self.selected_unit and
            self.targeted_unit and
            self.selected_unit.laser_charged and
            self.selected_unit.current_ap > 0
        ):
            self.laser_button.visible = True
        else:
            return
            # self.laser_button.visible = False



    def _fire_laser(self, shooter, target):
        """fire the selected unit's laser"""
        shooter.fire(self.overwatch_mode)

        # roll dice
        roll  = [D6(), D6()]
        total = roll[0] + roll[1]
        msg   = f"{roll[0]} + {roll[1]} = {total}"
        self._calc_to_hit(shooter=shooter, target=target)
        if total >= self.to_hit['total']:
            hit = True
            target.hit()
            self.scores[shooter.team] += 1
            msg += (f' (HIT) (needed {self.to_hit["total"]})\n')
        else:
            hit = False
            msg += (f' (MISS) (needed {self.to_hit["total"]})\n')
        msg += '(click or keypress to continue)'

        # animate laser
        source_tile   = shooter.tile
        target_tile   = target.tile
        line_dict     = shooter.visible_tiles
        sight_line    = line_dict[target_tile]
        # flash a few lasers, take enough time to see the shot before
        #   displaying the roll result message
        for i in range(0, 10):
            laser = Laser(self, shooter.team,
                sight_line.A, sight_line.B)
            laser.draw()
            pygame.display.flip()
            pygame.time.delay(int(self.settings.animation_speed))
            self._update_screen('laser animation')
            pygame.time.delay(int(self.settings.animation_speed))

        self._show_roll_result(msg)

        return hit



    def _show_roll_result(self, msg):
        """display the result of the dice roll"""
        self.roll_result_message.prep_msg(msg)
        self.roll_result_message.visible = True
        self.show_roll_result = True
        self._update_screen('show roll result')



    def _hide_roll_result(self):
        self.show_roll_result = False
        self.laser_button.visible = False
        if self.selected_unit.current_ap == 0 and not self.overwatch_mode:
            self._clear_selection()
        self._update_screen('hide roll result')



################################################################################
# OVERWATCH MODE
################################################################################



    def _show_inactive_los(self):
        """show the inactive team's sight lines"""
        self._clear_selection()
        self.showing_inactive_los = True
        for unit in self.teams[self.inactive_team]:
            if unit.current_ap < 0:
                self.game_map.show_los(self, unit)

################################

    def _begin_overwatch(self):
        """fill the list of eligible snap-shooters and randomize it"""

        # don't run overwatch mode if the unit has no laser
        if self.selected_unit.laser_uncharged:
            self._end_overwatch()
            return

        self.overwatch_mode = True
        self.overwatch_list = []

        # each unit on overwatch gets one shot per enemy move
        for shooter in self.teams[self.inactive_team]:

            # negative AP denotes active overwatch
            if shooter.current_ap >= 0 or shooter == None: continue #THE shooter==None SHOULNT BE NEEDED; WHY IS THERE AN EMPTY ITEM IN THE TEAM GROUP?
            if self.selected_unit.tile in shooter.visible_tiles:
                if shooter.current_ap <= -1:
                    self.overwatch_list.append(shooter)

        # randomize the list of shooters
        random.shuffle(self.overwatch_list)



    def _next_overwatch(self):
        """run the inactive team's overwatch phase after a move"""

        target = self.selected_unit

        # if no overwatch shooters, end overwatch round
        if len(self.overwatch_list) == 0:
            self._end_overwatch()

        else:
            # take the first shooter from the list
            shooter = self.overwatch_list.pop(0)

            # calc to-hit
            self._calc_to_hit(shooter, target)

            # display roll modifiers in status windows
            self._prep_active_message(shooter, target)
            self._prep_inactive_message(shooter, target)

            # use the laser button to show the snapshot to-hit total
            msg = f"SNAP SHOT! (roll {self.to_hit['total']} or more)"
            self.laser_button.prep_msg(msg)
            self.laser_button.visible = True

            # roll the dice and fire the laser
            hit = self._fire_laser(shooter, target)

            # if a hit was scored, end overwatch mode
            if hit:
                self._end_overwatch()


    def _end_overwatch(self):
        """end overwatch mode and go back to normal selection mode"""
        self.overwatch_mode = False
        # if self.selected_unit.current_ap == 0:
        #     self._clear_selection()

################################################################################
# UPDATE SCREEN
################################################################################



    def _update_screen(self, what_func):
        """update images on the screen, and flip to the new screen"""

        # for debugging; print the name of the function that called it
        print(what_func)

        # draw the background color
        self.screen.fill(self.settings.bg_color)

        # draw lasers in the background
        self._draw_background_lasers()

        # draw the map
        self.game_map.draw_map()

        # draw the units and update score labels
        for team in self.teams:
            for unit in self.teams[team]:
                unit.blitme()
            score = f'{self.scores[team]} / {self.settings.score_limit[team]}'
            self.score_label[team].prep_msg(score)

        # draw the button frame
        self.button_frame.draw_frame()

        # draw any visible buttons
        for button in self.buttons:
            button.draw_button()

        # show the rules screen
        if self.show_rules:
            self.rules.show()

        # show the result of the last dice roll
        if self.show_roll_result:
            self.roll_result_message.visible = True
        else: self.roll_result_message.visible = False

        # make the most recently drawn screen visible
        pygame.display.flip()



################################################################################
# BACKGROUND LASERS
################################################################################



    def _generate_background_lasers(self):
        # pass
        self.background_lasers = []
        # one laser per grid tile, but randomize positions each turn
        t       = self.settings.tile_size
        h       = int(self.settings.screen_height)
        w       = int(self.settings.screen_width)
        y_tiles = h // t
        x_tiles = w // t
        team_colors = (self.settings.team_color[self.active_team],
                       self.settings.alt_team_color[self.active_team])
        # left-right lasers
        for i in range(0, 8):
            left_y  = random.choice(range(0, h))
            right_y = random.choice(range(0, h))
            A       = Point(0, left_y)
            B       = Point(w, right_y)
            laser = Laser(self, self.active_team, A, B)
            self.background_lasers.append(laser)

        # up-down lasers
        for i in range(0, 6):
            # color = choice(team_colors)
            top_x = random.choice(range(0, w))
            bot_x = random.choice(range(0, w))
            A     = Point(top_x, 0)
            B     = Point(bot_x, h)
            laser = Laser(self, self.active_team, A, B)
            self.background_lasers.append(laser)


    def _draw_background_lasers(self):
        """draw the lasers"""
        # pass
        for laser in self.background_lasers:
            laser.draw()
        # pygame.display.flip()


################################################################################
# FUNCTIONS FOR DEBUGGING AND TESTING
################################################################################



    def _print_tile_data(self, tile, mouse_pos):
        """display info about the selected tile"""
        print(f'row: {tile.row}   col: {tile.col}')
        print(f'type: {tile.type}')
        print(f'occupied: {tile.occupied}')
        print("Adjoiners:")
        print(f"N:  {tile.adjoiners['n'].type}\tS:  {tile.adjoiners['s'].type}")
        print(f"E:  {tile.adjoiners['e'].type}\tW:  {tile.adjoiners['w'].type}")
        print(f"NE: {tile.adjoiners['ne'].type}\tSE: {tile.adjoiners['se'].type}")
        print(f"NW: {tile.adjoiners['nw'].type}\tSW: {tile.adjoiners['sw'].type}")
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
    lf = LaserFlag('maps\\_testing ground.txt')
    lf.run_game()