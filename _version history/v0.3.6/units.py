# units.py

import pygame
from pygame.sprite import Sprite

from lf_functions import CARDINALS, determine_range, determine_los

################################################################################
#   SUPERCLASS
################################################################################

class PlainUnit(Sprite):
    """The base class for player units. Sniper, Scout, and Grunt are subclasses"""
    def __init__(self, lf_game, team):
        super().__init__()
        self.screen   = lf_game.screen
        self.settings = lf_game.settings

        # default values
        self.team        = team
        self.unit_type   = 'Plain Unit'
        self.to_hit      = self.settings.base_to_hit
        self.move_speed  = self.settings.base_move_speed
        self.cover_bonus = self.settings.base_cover_bonus
        self.max_ap      = self.settings.base_max_ap
        self.elev_bonus  = -2

        # starting values
        self.sight_lines     = None     # mabye get rid of this?
        self.reachable_tiles = None
        self.visible_tiles   = None

        self.laser_uncharged = False
        self.laser_charging  = False
        self.current_ap      = self.max_ap
        self.elevated = False
        self.selected = False
        self.visible  = False
        self.targeted = False
        self.in_cover = {}
        for direction in CARDINALS:
            self.in_cover[direction] = False
        self.current_attack_bonus  = 0
        self.current_defense_bonus = 0

        # load sprite images
        #   base solder image
        self.base_image = pygame.image.load(f'images/unit_{self.team}.png')
        self.rect = self.base_image.get_rect()

        # status indicator images
        self.uncharged_image = pygame.image.load('images/unit_status_uncharged.png')
        self.charging_image = pygame.image.load('images/unit_status_charging.png')
        self.selected_image = pygame.image.load('images/unit_status_selected.png')
        self.targeted_image = pygame.image.load('images/unit_status_targeted.png')
        self.visible_image  = pygame.image.load('images/tile_mark_los.png')



    def _check_cover(self):
        """determine which directions the unit is covered in"""
        check = ['n', 's', 'e', 'w']

        # if elevated, only check for walls
        if self.tile.type == 'elevated':
            for direction in check:
                if self.tile.adjoiners[direction].type == 'wall':
                    self.in_cover[direction] = True
                else: self.in_cover[direction] = False

        # if on level ground, check for walls and elevated tiles
        else:
            for direction in check:
                if (self.tile.adjoiners[direction].type == 'wall' or
                    self.tile.adjoiners[direction].type == 'elevated'
                ):
                    self.in_cover[direction] = True
                else: self.in_cover[direction] = False

        # for debugging
        print(f'unit standing on {self.tile.type} ground')
        for direction in check:
            print(f'covered to {direction}: {self.in_cover[direction]}')


    def show_range(self, lf_game):
        """highlight tiles that the unit can reach this AP"""

        for step in self.reachable_tiles:

            # display highlights
            for tile in step:
                if lf_game.selected_unit.current_ap == 3:
                    tile.hilited = 'b'
                elif lf_game.selected_unit.current_ap == 2:
                    tile.hilited = 'y'
                elif lf_game.selected_unit.current_ap == 1:
                    tile.hilited = 'r'

            # animate the step
            lf_game._update_screen()
            base_speed = lf_game.settings.animation_speed
            speed_modifier = lf_game.selected_unit.move_speed
            FACTOR = 2
            pygame.time.delay((base_speed // speed_modifier) * FACTOR)


    def show_los(self, lf_game):
        """mark tiles that the unit can see"""
        for tile in self.visible_tiles:
            tile.mark()



    def move(self, lf_game, tile):
        """Move the selected unit to the selected tile"""

        # move the unit; add animation here later
        self.rect.x = tile.rect.x
        self.rect.y = tile.rect.y
        # unflag the old tile, assign the new tile to the unit, flag the new tile
        self.tile.occupied = False
        self.tile          = tile
        self.tile.occupied = True
        # flag whether the unit is on elevated terrain
        if self.tile.type == 'elevated':
            self.elevated = True
            self.current_attack_bonus = self.elev_bonus
        else:
            self.elevated = False
            self.current_attack_bonus = 0
        # test if the unit has touched base:
        if ('base' in self.tile.type and
            self.tile.type[-1] == self.team and
            self.laser_uncharged):
            self.begin_charging()

        # determine new walking range
        determine_range(lf_game, self)

        # determine new line-of-sight
        determine_los(lf_game, self)

        # clear highlighted tiles
        lf_game.game_map.clear_highlights()

        # charge one action point
        self.current_ap -= 1

        # determine which directions the unit is covered in
        self._check_cover()

        # deselect the unit
        self.selected = False
        lf_game.selected_unit = None






    def fire(self):
        self.current_ap = 0
        self.selected = False

    def hit(self):
        """when the unit is hit by an enemy laser"""
        self.laser_uncharged = True
        self.laser_charging = False

    def begin_charging(self):
        """when a deactivated unit touches his own base"""
        self.laser_charging = True

    def finish_charging(self):
        """after the recharged unit's turn has ended"""
        if self.laser_charging:
            self.laser_uncharged = False
            self.laser_charging = False

    def blitme(self):
        """draw the unit"""
        self.screen.blit(self.base_image, self.rect)
        if not self.unit_type == '_SuperUnit':
            self.screen.blit(self.class_image, self.rect)
        if self.selected:
            self.screen.blit(self.selected_image, self.rect)
        if self.laser_uncharged:
            self.screen.blit(self.uncharged_image, self.rect)
        if self.laser_charging:
            self.screen.blit(self.charging_image, self.rect)
        if self.visible:
            self.screen.blit(self.visible_image, self.rect)
        if self.targeted:
            self.screen.blit(self.targeted_image, self.rect)

        # change so this loads only once and then only displays the correct one
        ap = str(self.current_ap)
        image_file = pygame.image.load(f'images/unit_ap_{ap}.png')
        self.screen.blit(image_file, self.rect)


################################################################################
# SUBCLASSES
################################################################################

class Sniper(PlainUnit):
    """A sniper has higher accuracy and lower mobility; it may fire twice
        roll to hit : 6
        tiles per AP: 4
        can fire twice if AP remains"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unit_type   = 'sniper'
        self.to_hit     -= 1
        self.move_speed -= 1
        self.class_image = pygame.image.load(f'images/unit_type_sniper.png')

################################################################################

class Scout(PlainUnit):
    """A scout has higher mobility and lower accuracy; it can move after firing
        roll to hit : 8
        tiles per AP: 6
        can move after firing if APs remain"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unit_type   = 'scout'
        self.to_hit     += 1
        self.move_speed += 1
        self.class_image = pygame.image.load(f'images/unit_type_scout.png')

################################################################################

class Grunt(PlainUnit):
    """A grunt has average mobility and accuracy; it loves cover and low ground
        roll to hit : 7
        tiles per AP: 5
        +1 defensive bonus when in cover
        -1 to elevation attack bonus"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unit_type    = 'grunt'
        self.cover_bonus += 1
        self.elev_bonus  += 1
        self.class_image  = pygame.image.load(f'images/unit_type_grunt.png')