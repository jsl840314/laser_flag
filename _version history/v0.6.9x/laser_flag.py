################################################################################

import os
import sys
from random import choice
import pygame

from settings import Settings
from game_map import GameMap
from button_frame import ButtonFrame, Button
from lf_functions import (Point, Line, D6, game_caption, swap,
    tile_direction, determine_range, CARDINALS)
from rules import Rules



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

        # to track the user selection
        self.selected_unit      = None
        self.targeted_unit      = None
        # to store the selection when viewing enemy overwatch zones
        self.temp_selected_unit = None

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

            # if click on window X?
            if event.type == pygame.QUIT:
                self._quit_game()

            # if keypress
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self._quit_game()
                self._clear_selection()
                self._update_screen()

            # if mouse click
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.show_rules:
                    self.show_rules = False
                elif self.show_roll_result:
                    self.show_roll_result = False
                else:
                    mouse_pos = pygame.mouse.get_pos()
                    self._check_button_clicks(mouse_pos)
                    self._check_unit_clicks(mouse_pos)
                    self._check_tile_clicks(mouse_pos)
                self._update_screen()

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
        ######################## FIRE THE LASER ########################
        if laser_button_clicked and self.laser_button.visible:
            self._fire_laser(self.selected_unit, self.targeted_unit)
            self._run_overwatch(self.selected_unit)
            self._clear_selection()
        # show the rules screen
        elif rules_button_clicked and not self.laser_button.visible:
            self.show_rules = True
        # end the turn
        elif turn_button_clicked[self.active_team]:
            self._increment_turn()
        # show enemy team's overwatch zones
        elif turn_button_clicked[self.inactive_team]:
            self._show_inactive_los()

    def _check_button_unclicks(self, mouse_pos):
        """clear enemy LOS when button released"""
        if self.showing_inactive_los == True:
            self.showing_inactive_los = False
            self._clear_selection()
        self._update_screen()



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
            if tile == self.selected_unit.tile: continue
            tile_clicked = tile.rect.collidepoint(mouse_pos)
            if tile_clicked:

            #### MOVE THE SELECTED UNIT ####
                if (self.selected_unit and tile.hilited):
                    self.selected_unit.move(self.game_map, tile)
                    self._run_overwatch(self.selected_unit)
                    self._clear_selection()
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

        # if the clicked unit was already selected, just deselect it
        if clicked_unit.selected:
            self._clear_selection()
            return

        # otherwise select this unit
        # self._clear_selection()
        determine_range(self, clicked_unit)
        self.selected_unit = clicked_unit
        self.selected_unit.selected = True

        # update active team status window
        self._calc_to_hit(shooter=self.selected_unit)
        self._prep_active_message(self.selected_unit)

        # update the map marked & highlighted tiles
        self.game_map.show_los(self, clicked_unit)
        if clicked_unit.can_move:
            self.game_map.show_range(self, clicked_unit)


    def _on_click_target(self, clicked_unit):
        """when a unit of the inactive team is clicked"""
        # if the clicked unit was already targeted, just untarget it
        if clicked_unit.targeted:
            self._clear_target()
            return
        # if the unit is in LOS of the currently selected unit
        elif clicked_unit.visible and self.selected_unit.can_fire:
            self._clear_target()
            self.targeted_unit = clicked_unit
            self.targeted_unit.targeted = True
            self._show_laser_button()
            self._calc_to_hit(
                shooter=self.selected_unit, target=self.targeted_unit)
            self._prep_inactive_message(
                self.selected_unit, self.targeted_unit)


    def _prep_active_message(self, shooter, target = None, overwatch = False):
        """place the message for the ACTIVE team's status box. Active team
        is SHOOTER during their main turn and TARGET during overwatch phase"""
        if not overwatch:
            msg = self._shooter_message(shooter, overwatch)
        else:
            msg = self._target_message(shooter, target, overwatch)
        self.status_label[self.active_team].prep_msg(msg)


    def _prep_inactive_message(self, shooter, target, overwatch = False):
        """place the message for the INACTIVE team's status box. Only show
        when a enemy unit is targeted (as TARGET) or on overwatch (as SHOOTER)"""
        if not overwatch:
            msg = self._target_message(shooter, target)
        else:
            msg = self._shooter_message(shooter)
        self.status_label[self.inactive_team].prep_msg(msg)


    def _shooter_message(self, shooter, overwatch=False):
        """create the message for the SHOOTER'S status box. Does not need to
        know TARGET position because it doesn't display a cover bonus"""
        msg =  f"{shooter.unit_class.title()}: "
        msg += f"roll {self.to_hit['to-hit']} or more to hit\n"
        # terrain type
        msg += f"  on {shooter.tile.type} ground "
        # add a plus symbol for 0 modifier
        plus_string = ''
        if self.to_hit['elevated_hit_bonus'] == 0:
            plus_string += "+"
        msg += f"({plus_string}{self.to_hit['elevated_hit_bonus']})\n"
        # determine all cover directions; do NOT show a roll modifier
        covered = []
        for direction in CARDINALS:
            if shooter.in_cover[direction]:
                covered.append(direction)
        if covered != []:
            D = ', '.join(covered).upper()
            msg += f"  covered to {D}"
        else:
            msg += '  not in cover'
        return msg

    def _target_message(self, shooter, target, overwatch=False):
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
        for direction in CARDINALS:
            if (direction in shooter_direction and
                target.in_cover[direction]
            ):
                covered.append(direction)
        if covered != []:
            D = ', '.join(covered).upper()
            msg += f"  covered (+2) to {D}"
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


    def _calc_to_hit(self, shooter = None, target = None, overwatch = False):
        """calculate the current to-hit requirements"""
        self._clear_to_hit()
        if shooter:
            # print('to-hit adjustment for shooter')
            self.to_hit['to-hit'] = shooter.to_hit
            # if shooter is on elevated ground
            if shooter.elevated:
                self.to_hit['elevated_hit_bonus'] = shooter.elevated_hit_bonus
            if overwatch:
                self.to_hit['overwatch_penalty'] = shooter.overwatch_penalty
        if target:
            # print('to-hit adjustment for target')
            # if target is covered in the shooter's direction
            if target.is_in_cover(shooter):
                self.to_hit['cover_defense_bonus'] = target.cover_defense_bonus
            # if target is on elevated ground
            if target.elevated:
                self.to_hit['elev_defense_malus']  = target.elev_defense_malus

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
            self.selected_unit.can_fire and
            self.selected_unit.current_ap > 0
        ):
            self.laser_button.visible = True
        else:
            self.laser_button.visible = False




    def _fire_laser(self, shooter, target, overwatch=False):
        """fire the selected unit's laser"""
        shooter.fire(overwatch)

        # roll dice
        roll  = [D6(), D6()]
        total = roll[0] + roll[1]
        msg   = f"{roll[0]} + {roll[1]} = {total}"
        self._calc_to_hit(shooter=shooter, target=target, overwatch=overwatch)
        if total >= self.to_hit['total']:
            hit = True
            target.hit()
            self.scores[shooter.team] += 1
            msg += (f' (HIT) (needed {self.to_hit["total"]})\n(click or keypress to continue)')
        else:
            hit = False
            msg += (f' (MISS) (needed {self.to_hit["total"]})\n(click or keypress to continue)')

        if not overwatch:
            self.roll_result_message.prep_msg(msg)

        else:
            msg = f"Snap shot! (+{self.to_hit['overwatch_penalty']} penalty)\n" + msg
            self.roll_result_message.prep_msg(msg)

        # animate laser
        source_tile = shooter.tile
        target_tile = target.tile
        line_dict   = shooter.visible_tiles
        sight_line  = line_dict[target_tile]
        laser_color = self.settings.team_color[shooter.team]

        # draw a few lasers and take enough time to read the hit message
        for i in range(0, 5):
            pygame.draw.line(self.screen, laser_color,
                (sight_line.A.x, sight_line.A.y),
                (sight_line.B.x, sight_line.B.y))
            pygame.display.flip()
            pygame.time.delay(int(self.settings.animation_speed))
            self._update_screen()
            pygame.time.delay(int(self.settings.animation_speed))



        self.laser_button.visible = False

        return hit



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


    def _run_overwatch(self, target):
        """run the inactive team's overwatch phase after a move"""
        # return
        if self.selected_unit.laser_uncharged and not 'base' in self.selected_unit.tile.type:
            return
        # self._clear_selection()
        shooters = []

        # each unit on overwatch gets one shot per enemy move
        for shooter in self.teams[self.inactive_team]:
            if shooter.current_ap >= 0 or shooter == None: continue   # negative AP denotes active overwatch
            if target.tile in shooter.visible_tiles:
                if shooter.current_ap <= -1:
                    shooters.append(shooter)

        # randomize the list of shooters
        random_shooters = []
        while len(shooters) > 0:
            shooter = choice(shooters)
            shooters.remove(shooter)
            random_shooters.append(shooter)

        for shooter in random_shooters:
            self.roll_result_message.visible = True
            shooter.targeted = True
            self._calc_to_hit(shooter, target, overwatch=True)
            self._prep_active_message(shooter, target, overwatch = True)
            self._prep_inactive_message(shooter, target, overwatch = True)
            self._update_screen()

            # roll the dice and fire the laser
            hit = self._fire_laser(shooter, target, overwatch=True)
            shooter.targeted = False

            self.roll_result_message.visible = False

            if hit:
                break
            # else:
            #     # pause for a beat so it's clear a different unit is firing
            #     pygame.time.delay(self.settings.animation_speed*5)

        self._update_screen()







################################################################################
# UPDATE SCREEN
################################################################################

    def _update_screen(self):
        """update images on the screen, and flip to the new screen"""

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

        # make the most recently drawn screen visible
        pygame.display.flip()

################################################################################
# BACKGROUND LASERS
################################################################################

    def _generate_background_lasers(self):
        self.background_lasers = {}
        # one laser per grid tile, but randomize positions each turn
        t       = self.settings.tile_size
        h       = int(self.settings.screen_height)
        w       = int(self.settings.screen_width)
        y_tiles = h // t
        x_tiles = w // t
        team_colors = (self.settings.team_color[self.active_team],
                       self.settings.alt_team_color[self.active_team])
        # left-right lasers
        for i in range(0, y_tiles):
            # color = choice(team_colors)
            color = (choice(range(0,255)), choice(range(0,255)), choice(range(0,255)))
            left_y  = choice(range(0, h))
            right_y = choice(range(0, h))
            A       = Point(0, left_y)
            B       = Point(w, right_y)
            line    = Line(A, B)
            self.background_lasers[line] = color
        # up-down lasers
        for i in range(0, x_tiles):
            # color = choice(team_colors)
            color = (choice(range(0,255)), choice(range(0,255)), choice(range(0,255)))
            top_x = choice(range(0, w))
            bot_x = choice(range(0, w))
            A     = Point(top_x, 0)
            B     = Point(bot_x, h)
            line  = Line(A, B)
            self.background_lasers[line] = color



    def _draw_background_lasers(self):
        """draw the lasers"""
        for line in self.background_lasers:
            laser_color = self.background_lasers[line]
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