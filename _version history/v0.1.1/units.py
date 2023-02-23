# units.py

import pygame
from pygame.sprite import Sprite

class _SuperUnit(Sprite):
    """The base class for player units. This is a protected class not meant for
    actual gameplay. Sniper, Scout, and Grunt are subclasses"""
    def __init__(self, lf_game, team):
        super().__init__()
        self.screen = lf_game.screen
        self.settings = lf_game.settings

        # default values, will be modified by subclasses
        self.hit_chance = 7
        self.move_speed = 5
        self.cover_bonus = 2

        # starting values
        self.laser_charged = True
        self.laser_charging = False
        self.max_ap = 3
        self.current_ap = 3
        self.in_cover = {'n': False, 's': False, 'e': False, 'w': False}
        self.elevated = False
        self.selected = False
        self.targeted = False

        # default soldier
        if team == 'green':
            self.team = 'green'
            self.base_image = pygame.image.load('images/unit_g.png')
        elif team == 'magenta':
            self.team = 'magenta'
            self.base_image = pygame.image.load('images/unit_m.png')

        # load other status indicator images
        self.uncharged_image = pygame.image.load('images/unit_status_uncharged.png')
        self.charging_image = pygame.image.load('images/unit_status_charging.png')
        self.selected_image = pygame.image.load('images/unit_status_selected.png')
        self.targeted_image = pygame.image.load('images/unit_status_targeted.png')

        self.unit_type = '_SuperUnit'

        self.rect = self.base_image.get_rect()
        self.rect.x = self.settings.tile_size
        self.rect.y = self.settings.tile_size

        self.finish_charging()


    def hit(self):
        """when the unit is hit by an enemy laser"""
        self.laser_charged = False
        self.laser_charging = False

    def begin_charging(self):
        """when a deactivated unit touches his own base"""
        self.laser_charging = True

    def finish_charging(self):
        """after the recharged unit's turn has ended"""
        self.laser_charged = True
        self.laser_charging = False

    def select(self, lf_game):
        """select the chosen unit"""
        if lf_game.selected_unit:
            lf_game.selected_unit.deselect(lf_game)
        lf_game.selected_unit = self
        self.selected = True

    def deselect(self, lf_game):
        """deselect the currently selected unit"""
        lf_game.selected_unit = None
        self.selected = False



    def blitme(self):
        """draw the unit"""
        self.screen.blit(self.base_image, self.rect)
        if not self.unit_type == '_SuperUnit':
            self.screen.blit(self.class_image, self.rect)
        if self.selected:
            self.screen.blit(self.selected_image, self.rect)
        if not self.laser_charged:
            self.screen.blit(self.uncharged_image, self.rect)
        if self.laser_charging:
            self.screen.blit(self.charging_image, self.rect)
        if self.targeted:
            self.screen.blit(self.targeted_image, self.rect)

        # change so this loads only once and then only displays the correct one
        ap = str(self.current_ap)
        image_file = pygame.image.load(f'images/unit_ap_{ap}.png')
        self.screen.blit(image_file, self.rect)


class Sniper(_SuperUnit):
    """A sniper has higher accuracy and lower mobility
        roll to hit : 6
        tiles per AP: 4
        can fire twice if AP remains"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unit_type = 'sniper'
        self.hit_chance -= 1
        self.move_speed -= 1
        self.class_image = pygame.image.load(f'images/unit_type_sniper.png')


class Grunt(_SuperUnit):
    """A grunt has average mobility and accuracy
        roll to hit : 7
        tiles per AP: 5
        +1 defensive bonus when in cover"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unit_type = 'grunt'
        self.cover_bonus += 1
        self.class_image = pygame.image.load(f'images/unit_type_grunt.png')


class Scout(_SuperUnit):
    """A scout has higher mobility and lower accuracy
        roll to hit : 8
        tiles per AP: 6
        can move after firing if APs remain"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unit_type = 'scout'
        self.hit_chance += 1
        self.move_speed += 1
        self.class_image = pygame.image.load(f'images/unit_type_scout.png')