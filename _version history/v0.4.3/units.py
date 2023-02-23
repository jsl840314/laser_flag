# units.py

import pygame
from pygame.sprite import Sprite

from lf_functions import CARDINALS, determine_range, determine_los, tile_direction

################################################################################
#   SUPERCLASS
################################################################################

class BasicUnit(Sprite):
    """The base class for player units. Sniper, Scout, and Grunt are subclasses"""
    def __init__(self, lf_game, team):
        super().__init__()
        self.screen   = lf_game.screen
        self.settings = lf_game.settings

        self.team      = team
        self.unit_class = 'Basic'

        # load default settings
        self.max_ap              = self.settings.base_max_ap
        self.move_speed          = self.settings.base_move_speed
        self.to_hit              = self.settings.base_to_hit
        self.elevated_hit_bonus  = self.settings.base_elevated_hit_bonus
        self.cover_defense_bonus = self.settings.base_cover_defense_bonus
        self.elev_defense_malus  = self.settings.base_elev_defense_malus

        # store walking range tiles and line-of-sight tiles
        self.reachable_tiles = None
        self.visible_tiles   = None

        # in-game status flags
        self.can_move        = True
        self.can_fire        = True
        self.current_ap      = self.max_ap
        self.laser_uncharged = False
        self.laser_charging  = False
        self.elevated        = False
        self.in_cover = {}
        for direction in CARDINALS:
            self.in_cover[direction] = False

        # selection flags
        self.selected = False
        self.visible  = False
        self.targeted = False

        # load sprite images
        self.base_image      = pygame.image.load(f'images/unit_class_basic.png')
        self.uncharged_image = pygame.image.load('images/unit_status_uncharged.png')
        self.charging_image  = pygame.image.load('images/unit_status_charging.png')
        self.selected_image  = pygame.image.load('images/unit_status_selected.png')
        self.visible_image   = pygame.image.load('images/tile_mark_los.png')
        self.targeted_image  = pygame.image.load('images/unit_status_targeted.png')
        self.move_y_image    = pygame.image.load('images/unit_status_move_y.png')
        self.move_n_image    = pygame.image.load('images/unit_status_move_n.png')

        self.ap_image = {}
        for i in ['-2', '-1', '0', '1', '2', '3']:
            self.ap_image[i] = pygame.image.load(f'images/unit_ap_{i}.png')

        self.rect = self.base_image.get_rect()

    def check_cover(self):
        """determine which directions the unit is covered in"""

        # if elevated, only check for walls
        if self.tile.type == 'elevated':
            for direction in CARDINALS:
                if self.tile.adjoiners[direction].type == 'wall':
                    self.in_cover[direction] = True
                else: self.in_cover[direction] = False

        # if on level ground, check for walls and elevated tiles
        else:
            for direction in CARDINALS:
                if (self.tile.adjoiners[direction].type == 'wall' or
                    self.tile.adjoiners[direction].type == 'elevated'
                ):
                    self.in_cover[direction] = True
                else: self.in_cover[direction] = False

        # for debugging
        print(f'unit standing on {self.tile.type} ground')
        for direction in CARDINALS:
            print(f'covered to {direction}: {self.in_cover[direction]}')






    def move(self, lf_game, tile):
        """Move the selected unit to the selected tile"""
        if not self.can_move: return
        # move the unit
        self.rect.x = tile.rect.x
        self.rect.y = tile.rect.y
        # unflag the old tile, assign the new tile to the unit, flag the new tile
        self.tile.occupied = None
        self.tile          = tile
        self.tile.occupied = self
        # flag whether the unit is on elevated terrain
        if self.tile.type == 'elevated':
            self.elevated = True
        else:
            self.elevated = False
        # test if the unit has touched base:
        if ('base' in self.tile.type and
            self.tile.type[-1] == self.team and
            self.laser_uncharged):
            self.begin_charging()
        # determine new walking range and line-of-sight
        determine_range(lf_game, self)
        determine_los(lf_game, self)
        # determine which directions the unit is covered in
        self.check_cover()
        # charge one action point
        self.current_ap -= 1

        if self.current_ap == 0:
            self.can_move = False




    def is_in_cover(self, attacking_unit):
        """return True if unit is in cover against enemy unit"""
        # tile_direction returns a string with one or two letters
        enemy_direction = tile_direction(
            self.tile, attacking_unit.tile)
        for direction in enemy_direction[:]:
            if self.in_cover[direction]:
                return True
        return False


    def hit(self):
        """when the unit is hit by an enemy laser"""
        self.targeted = False
        self.laser_uncharged = True
        self.laser_charging  = False

    def begin_charging(self):
        """when a deactivated unit touches his own base"""
        self.laser_charging = True
        self.can_fire       = False

    def finish_charging(self):
        """after the recharged unit's turn has ended"""
        if self.laser_charging:
            self.laser_uncharged = False
            self.laser_charging  = False
            self.can_fire        = True

    def fire(self):
        self.selected       = False
        self.laser_charging = True
        self.can_move       = False
        self.can_fire       = False
        self._class_after_firing()

    def _class_after_firing(self):
        """to be overridden by subclasses to implement class-specific behavior"""
        self.current_ap = 0
        pass


    def _draw_class_images(self):
        """to be overridden by subclasses to draw class-specific stuff"""
        pass

    def blitme(self):
        """draw the unit"""

        pygame.draw.circle(self.screen, self.settings.team_color[self.team],
            self.rect.center, 19)
        self._draw_class_images()
        self.screen.blit(self.base_image, self.rect)
        if not self.unit_class == 'BasicUnit':
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

        if self.can_move and self.current_ap > 0:
            self.screen.blit(self.move_y_image, self.rect)
        elif self.current_ap >= 0:
            self.screen.blit(self.move_n_image, self.rect)

        ap = str(self.current_ap)
        self.screen.blit(self.ap_image[ap], self.rect)


################################################################################
# SUBCLASSES
################################################################################

class Sniper(BasicUnit):
    """A sniper has higher accuracy and lower mobility; it may fire twice
        roll to hit : 6
        tiles per AP: 4
        can fire twice if AP remains"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unit_class   = 'sniper'
        self.to_hit     -= 1    # a bonus
        self.move_speed -= 1    # a malus
        self.class_image = pygame.image.load(f'images/unit_class_sniper.png')

    def _draw_class_images(self):
        """draw another circle of the alt color"""
        # proof of concept, refine later for each class
        pass
        # pygame.draw.circle(self.screen, self.settings.alt_team_color[self.team],
        #     self.rect.center, 10)

    def _class_after_firing(self):
        self.current_ap -= 1
        if self.laser_charging:
            self.laser_charging = False
            self.laser_uncharged = False
            self.can_fire = True

################################################################################

class Scout(BasicUnit):
    """A scout has higher mobility and lower accuracy; it can move after firing
        roll to hit : 8
        tiles per AP: 6
        can move after firing if APs remain"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unit_class   = 'scout'
        self.to_hit     += 1    # a malus
        self.move_speed += 1    # a bonus
        self.class_image = pygame.image.load(f'images/unit_class_scout.png')

    def _class_after_firing(self):
        self.current_ap -= 1
        if self.current_ap > 0:
            self.can_move = True

################################################################################

class Grunt(BasicUnit):
    """A grunt has average mobility and accuracy; it loves cover and low ground
        roll to hit : 7
        tiles per AP: 5
        +1 defensive bonus when in cover
        -1 to elevation attack bonus"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unit_class    = 'grunt'
        self.cover_defense_bonus += 1   # a bonus
        self.elevated_hit_bonus  += 1   # a malus
        self.class_image  = pygame.image.load(f'images/unit_class_grunt.png')