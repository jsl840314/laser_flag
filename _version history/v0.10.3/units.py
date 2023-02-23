# units.py

import pygame
from pygame.sprite import Sprite

from lf_functions import CARDINALS, determine_range, determine_los, tile_direction

################################################################################
#   SUPERCLASS
################################################################################

class BasicUnit(Sprite):
    """The base class for player units. Sniper, Scout, and Grunt are subclasses"""
    def __init__(self, game_map, team):
        super().__init__()
        self.game_map = game_map
        self.screen   = game_map.screen
        self.settings = game_map.settings

        self.team       = team
        self.unit_class = 'basic'

        # load default settings
        self.max_ap              = self.settings.base_max_ap
        self.move_speed          = self.settings.base_move_speed
        self.to_hit              = self.settings.base_to_hit
        self.elevated_hit_bonus  = self.settings.base_elevated_hit_bonus
        self.cover_defense_bonus = self.settings.base_cover_defense_bonus
        self.elev_defense_malus  = self.settings.base_elev_defense_malus
        self.overwatch_penalty   = self.settings.base_overwatch_penalty
        self.max_overwatch       = self.settings.base_max_overwatch
        # only Scout subclasses can climb onto cover and keep moving
        self.can_climb = self.settings.base_can_climb

        # store walking range tiles and line-of-sight tiles
        self.reachable_tiles = None
        self.visible_tiles   = None
        # selection flags
        self.selected        = False
        self.visible         = False
        self.targeted        = False
        # in-game status flags
        self.can_move        = True
        self.laser_charged        = True
        self.current_ap      = self.max_ap
        self.laser_uncharged = False
        self.laser_charging  = False
        self.elevated        = False

        # fill in_cover dictionary and load cover images
        self.in_cover    = {}
        self.cover_image = {}
        for direction in CARDINALS:
            self.in_cover[direction] = False
            self.cover_image[direction] = pygame.image.load(
                f'images/unit_status_cover_{direction}.png')

        # load rest of sprite images and get rect
        self.base_image      = pygame.image.load(
            f'images/unit_outline.png')
        self.uncharged_image = pygame.image.load(
            'images/unit_status_uncharged.png')
        self.charging_image  = pygame.image.load(
            'images/unit_status_charging.png')
        self.selected_image  = pygame.image.load(
            'images/unit_status_selected.png')
        self.visible_image   = pygame.image.load(
            'images/unit_status_visible.png')
        self.targeted_image  = pygame.image.load(
            'images/unit_status_targeted.png')
        self.move_y_image    = pygame.image.load(
            'images/unit_status_move_y.png')
        self.move_n_image    = pygame.image.load(
            'images/unit_status_move_n.png')
        self.elevated_image  = pygame.image.load(
            'images/unit_status_elevated.png')
        self.class_image     = None
        self.ap_image = {}
        for i in ['-3', '-2', '-1', '0', '1', '2', '3']:
            self.ap_image[i] = pygame.image.load(
                f'images/unit_status_ap_{i}.png')
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


    def is_in_cover(self, attacking_unit):
        """return True if unit is in cover against enemy unit"""
        # tile_direction returns a string with one or two letters
        found_cover = False
        enemy_direction = tile_direction(
            self.tile, attacking_unit.tile)
        for direction in enemy_direction[:]:
            if self.in_cover[direction]:
                found_cover = True
        return found_cover


    def move(self, lf_game, tile):
        """Move the selected unit to the selected tile"""
        if not self.can_move: return
        if tile == self.tile: return
        # move the unit
        self.rect.x = tile.rect.x
        self.rect.y = tile.rect.y
        # unflag the old tile, assign the new tile to the unit, flag the new tile
        self.tile.occupied = None
        self.tile          = tile
        self.tile.occupied = self
        # determine which directions the unit is covered in
        self.check_cover()
        # flag whether the unit is on elevated terrain
        if self.tile.type == 'elevated':
            self.elevated = True
        else:
            self.elevated = False
        # test if the unit has touched base:
        self._check_for_base()
        # determine new walking range and line-of-sight
        determine_range(lf_game, self)
        determine_los(lf_game, self)
        # charge one action point
        self.current_ap -= 1
        if self.current_ap == 0:
            self.can_move = False


    def end_turn(self):
        """actions at the end of the unit's team's turn"""
        self.finish_charging()
        self.selected = False
        if self.current_ap > self.max_overwatch:
            self.current_ap = self.max_overwatch
        if self.laser_uncharged or not self.can_move:
            self.current_ap = 0
        self.current_ap = -self.current_ap


    def begin_turn(self):
        """actions at the beginning of the unit's team's turn"""
        self.finish_charging()
        self.selected   = False
        self.current_ap = self.max_ap
        self.can_move   = True



    def _check_for_base(self):
        """check if the unit is on a friendly base"""
        if ((self.tile.type  == 'base_u' or
             self.tile.type  == f'base_{self.team}') and
            self.laser_uncharged):
            self.begin_charging()


    def hit(self):
        """when the unit is hit by an enemy laser"""
        self.targeted        = False
        # if unit was on overwatch, remove his APs
        if self.current_ap < 0:
            self.current_ap  = 0
        self.laser_charged        = False
        self.laser_uncharged = True
        self.laser_charging  = False
        self.game_map.eliminate_unit(self)
        self._check_for_base()

    def begin_charging(self):
        """when a deactivated unit touches his own base"""
        self.laser_uncharged = False
        self.laser_charging  = True
        self.laser_charged        = False

    def finish_charging(self):
        """after the recharged unit's turn has ended, recharge its laser"""
        if not self.laser_uncharged:
            self.laser_charging = False
            self.laser_charged  = True


    def fire(self, overwatch = False):
        """some classes override this function;
            make sure any changes here are copied if necessary"""
        self.selected = False
        self.can_move = False
        # overwatch shots do not require recharging
        if overwatch:
            self.current_ap += 1
        # regular shots
        else:
            self.laser_charged   = False
            self.current_ap = 0


    def blitme(self):
        """draw the unit"""
        pygame.draw.circle(self.screen, self.settings.team_color[self.team],
            self.rect.center, 19)
        self._draw_class_images()
        self.screen.blit(self.base_image, self.rect)

        if self.class_image:
            self.screen.blit(self.class_image[self.settings.b_w_team_color[self.team]], self.rect)


        # self.class_image = pygame.image.load(f'images/unit_class_{self.unit_class}_{self.settings.b_w_team_color[self.team]}.png')

        if self.visible:
            self.screen.blit(self.visible_image, self.rect)
        if self.selected:
            self.screen.blit(self.selected_image, self.rect)
        if self.laser_uncharged:
            self.screen.blit(self.uncharged_image, self.rect)
        if self.laser_charging:
            self.screen.blit(self.charging_image, self.rect)
        if self.targeted:
            self.screen.blit(self.targeted_image, self.rect)
        if self.can_move and self.current_ap > 0:
            self.screen.blit(self.move_y_image, self.rect)
        elif self.current_ap >= 0:
            self.screen.blit(self.move_n_image, self.rect)
        if self.elevated:
            self.screen.blit(self.elevated_image, self.rect)
        ap = str(self.current_ap)
        self.screen.blit(self.ap_image[ap], self.rect)
        for direction in CARDINALS:
            if self.in_cover[direction]:
                self.screen.blit(self.cover_image[direction], self.rect)


    def _draw_class_images(self):
        """basic units get a small circle of the team's alt color"""
        # draw a black circle for an outline
        pygame.draw.circle(self.screen,
            self.settings.b_w_team_color[self.team],
            self.rect.center, 7)
        # draw the colored circle
        pygame.draw.circle(self.screen,
            self.settings.alt_team_color[self.team],
            self.rect.center, 5)






################################################################################
# SUBCLASSES
################################################################################



class Sniper(BasicUnit):
    """A sniper has higher accuracy and lower mobility; it may fire twice
        roll to hit : 6
        tiles per AP: 4
        EXTRA: can fire multiple times
                - only loses 1 AP on firing (base class loses all)
                - but can_move remains False until next turn"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unit_class   = 'sniper'
        self.to_hit      += self.settings.sniper_to_hit
        self.move_speed  += self.settings.sniper_move_speed
        self.class_image = {'black': pygame.image.load(f'images/unit_class_{self.unit_class}_black.png'),
                            'white': pygame.image.load(f'images/unit_class_{self.unit_class}_white.png')}


    def fire(self, overwatch = False):
        """Snipers must stop moving but can continue firing in place"""
        self.selected = False
        self.can_move = False
        # overwatch shots do not require recharging
        if overwatch:
            self.current_ap += 1
        # regular shots
        else:
            self.laser_charged   = True
            self.current_ap -=1


    def _draw_class_images(self):
        """Fill in the Sniper's lasergun symbol"""
        pygame.draw.polygon(self.screen,
            self.settings.alt_team_color[self.team],
            ((self.tile.CEN.x-12, self.tile.CEN.y-4),
                (self.tile.CEN.x-9, self.tile.CEN.y-6),
                (self.tile.CEN.x, self.tile.CEN.y-6),
                (self.tile.CEN.x, self.tile.CEN.y+1),
                (self.tile.CEN.x-6, self.tile.CEN.y+1),
                (self.tile.CEN.x-8, self.tile.CEN.y+6),
                (self.tile.CEN.x-11, self.tile.CEN.y+6),
                (self.tile.CEN.x-9, self.tile.CEN.y+1))
            )
        pygame.draw.circle(self.screen, self.settings.alt_team_color[self.team], (self.tile.CEN.x+11, self.tile.CEN.y-2), 2)



################################################################################



class Scout(BasicUnit):
    """A scout has higher mobility and lower accuracy; it can move after firing
        roll to hit : 8
        tiles per AP: 6
        EXTRA: can climb cover tiles with no penalty"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unit_class  = 'scout'
        self.can_climb   = self.settings.scout_can_climb
        self.to_hit     += self.settings.scout_to_hit
        self.move_speed += self.settings.scout_move_speed
        self.class_image = {'black': pygame.image.load(f'images/unit_class_{self.unit_class}_black.png'),
                            'white': pygame.image.load(f'images/unit_class_{self.unit_class}_white.png')}

    def _draw_class_images(self):
        """Fill in the Scout's foot symbol"""
        pygame.draw.polygon(self.screen,
            self.settings.alt_team_color[self.team],
            ((self.tile.CEN.x-8, self.tile.CEN.y-1),
                (self.tile.CEN.x-3, self.tile.CEN.y-10),
                (self.tile.CEN.x-2, self.tile.CEN.y-9),
                (self.tile.CEN.x+3, self.tile.CEN.y-6),
                (self.tile.CEN.x+12, self.tile.CEN.y),
                (self.tile.CEN.x+13, self.tile.CEN.y+1),
                (self.tile.CEN.x+11, self.tile.CEN.y+4),
                (self.tile.CEN.x+4, self.tile.CEN.y+4))
            )



################################################################################



class Grunt(BasicUnit):
    """A grunt has average mobility and accuracy; it loves cover and low ground
        roll to hit : 7
        tiles per AP: 5
        EXTRA: Grunts get more extreme tactical advantages and disadvantages.
            If a normal unit gets 2, a Grunt gets 3; whether good or bad"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unit_class    = 'grunt'
        self.cover_defense_bonus += self.settings.grunt_cover_defense_bonus
        self.elevated_hit_bonus  += self.settings.grunt_elevated_hit_bonus
        self.elev_defense_malus  += self.settings.grunt_elev_defense_malus
        self.overwatch_penalty   += self.settings.grunt_overwatch_penalty
        self.max_overwatch       += self.settings.grunt_max_overwatch
        self.class_image = {'black': pygame.image.load(f'images/unit_class_{self.unit_class}_black.png'),
                            'white': pygame.image.load(f'images/unit_class_{self.unit_class}_white.png')}


    def _draw_class_images(self):
        """fill in the Grunt's shield symbol"""
        pygame.draw.circle(self.screen,
            self.settings.alt_team_color[self.team],
            (self.tile.CEN.x-1, self.tile.CEN.y+2), 7)
        pygame.draw.circle(self.screen,
            self.settings.alt_team_color[self.team],
            (self.tile.CEN.x, self.tile.CEN.y+2), 7)
        pygame.draw.polygon(self.screen,
            self.settings.alt_team_color[self.team],
            ((self.tile.CEN.x-8, self.tile.CEN.y-8),
                (self.tile.CEN.x, self.tile.CEN.y-6),
                (self.tile.CEN.x+6, self.tile.CEN.y-8),
                (self.tile.CEN.x+6, self.tile.CEN.y),
                (self.tile.CEN.x-8, self.tile.CEN.y))
            )
