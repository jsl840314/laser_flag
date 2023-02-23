# rules.py

import pygame

from tile import Tile
from units import BasicUnit, Sniper, Grunt, Scout

class Rules():
    """a frame to show the game rules"""

    def __init__(self, lf_game):
        self.screen = lf_game.screen
        self.settings = lf_game.settings
        self.tile_size = self.settings.tile_size
        self.grid_size = self.settings.grid_size

        # set dimensions and properties of the rules frame
        self.width, self.height = self.tile_size * 29, self.tile_size * 20
        self.frame_color = (50, 50, 80)# self.settings.bg_color

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.x = self.tile_size
        self.rect.y = self.tile_size

        self._draw_unit_icons()
        self._draw_misc_icons()
        self._draw_tile_icons()
        self._draw_text()


    def _draw_unit_icons(self):
        """draw the units on the rules pane"""
        self.units = [BasicUnit(self, team='g'),
                      BasicUnit(self, team='m'),
                      Scout(self,     team='g'),
                      Scout(self,     team='m'),
                      Sniper(self,    team='g'),
                      Sniper(self,    team='m'),
                      Grunt(self,     team='g'),
                      Grunt(self,     team='m')]
        t = self.tile_size
        row = 10
        col = 1.5
        for unit in self.units:
            unit.rect.x = (col + 0.5) * t
            unit.rect.y = (row + 0.5) * t
            unit.tile = Tile(self,  {'row': row, 'col': col, 'occupied': False,
                    'type': 'level', 'ID': 0})
            col += 1.5
            if col >= 3.5:
                row += 2.5
                col = 1.5


    def _draw_tile_icons(self):
        """draw the map tiles on the rules pane"""
        self.tiles = [Tile(self, {'row': 1.5, 'col': 19.5, 'occupied': False,
                                 'type': 'wall', 'ID': 0}),
                      Tile(self, {'row': 3.5, 'col': 19.5, 'occupied': False,
                                 'type': 'elevated', 'ID': 0}),
                      Tile(self, {'row': 5.5, 'col': 19.5, 'occupied': False,
                                 'type': 'level', 'ID': 0}),
                      Tile(self, {'row': 7.5, 'col': 19.5, 'occupied': False,
                                  'type': 'base_u', 'ID': 0}),
                      Tile(self, {'row': 9.5, 'col': 18.8, 'occupied': False,
                                 'type': 'base_g', 'ID': 0}),
                      Tile(self, {'row': 9.5, 'col': 20.2, 'occupied': False,
                                 'type': 'base_m', 'ID': 0})]


    def _draw_misc_icons(self):
        self.icon_el = pygame.image.load('images/unit_status_elevated.png')
        self.icon_cv = pygame.image.load('images/unit_status_cover_n.png')
        self.icon_ap_1 = pygame.image.load('images/unit_status_ap_1.png')
        self.icon_ap_2 = pygame.image.load('images/unit_status_ap_2.png')
        self.icon_mv = pygame.image.load('images/unit_status_move_y.png')
        self.icon_nm = pygame.image.load('images/unit_status_move_n.png')
        self.icon_sn = pygame.image.load('images/unit_status_ap_-3.png')
        self.icon_un = pygame.image.load('images/unit_status_uncharged.png')
        self.icon_ch = pygame.image.load('images/unit_status_charging.png')




    def _draw_text(self):
        self.rules_main_image    = pygame.image.load('images/rules_main.png')
        self.rules_plain_image   = pygame.image.load('images/rules_plain.png')
        self.rules_scout_image   = pygame.image.load('images/rules_scout.png')
        self.rules_sniper_image  = pygame.image.load('images/rules_sniper.png')
        self.rules_grunt_image   = pygame.image.load('images/rules_grunt.png')
        self.rules_base_image    = pygame.image.load('images/rules_base.png')
        self.rules_cover_image   = pygame.image.load('images/rules_cover.png')
        self.rules_wall_image    = pygame.image.load('images/rules_wall.png')
        self.rules_level_image   = pygame.image.load('images/rules_level.png')
        self.rules_victory_image = pygame.image.load('images/rules_victory.png')
        self.rules_icons_image = pygame.image.load('images/rules_icons.png')




    def show(self):
        """show the rules"""
        t = self.tile_size

        # fill the screen
        self.screen.fill(self.frame_color, self.rect)

        # draw the units
        for unit in self.units:
            unit.blitme()

        # draw the tiles
        for tile in self.tiles:
            tile.blitme()


        # draw the misc icons
        self.screen.blit(self.icon_el, (
            self.rect.x + t*19, self.rect.y + t*14.2))
        self.screen.blit(self.icon_cv, (
            self.rect.x + t*24, self.rect.y + t*14.3))

        self.screen.blit(self.icon_mv, (
            self.rect.x + t*19.6, self.rect.y + t*15))
        self.screen.blit(self.icon_nm, (
            self.rect.x + t*19.9, self.rect.y + t*15))
        self.screen.blit(self.icon_ap_1, (
            self.rect.x + t*19.6, self.rect.y + t*15))
        self.screen.blit(self.icon_ap_2, (
            self.rect.x + t*19.9, self.rect.y + t*15))
        self.screen.blit(self.icon_sn, (
            self.rect.x + t*24.2, self.rect.y + t*14.9))

        self.screen.blit(self.icon_un, (
            self.rect.x + t*19.3, self.rect.y + t*15.6))
        self.screen.blit(self.icon_ch, (
            self.rect.x + t*23.9, self.rect.y + t*15.6))






        # draw text images
        self.screen.blit(self.rules_main_image, (
            self.rect.x + t*0.5, self.rect.y + t*0.5))
        self.screen.blit(self.rules_plain_image, (
            self.rect.x + t*3.1, self.rect.y + t*9))
        self.screen.blit(self.rules_scout_image, (
            self.rect.x + t*4, self.rect.y + t*12.4))
        self.screen.blit(self.rules_sniper_image, (
            self.rect.x + t*4, self.rect.y + t*14.9))
        self.screen.blit(self.rules_grunt_image, (
            self.rect.x + t*4, self.rect.y + t*17.4))

        self.screen.blit(self.rules_wall_image , (
            self.rect.x + t*20.5, self.rect.y + t*1.5))
        self.screen.blit(self.rules_cover_image, (
            self.rect.x + t*20.5, self.rect.y + t*3.5))
        self.screen.blit(self.rules_level_image , (
            self.rect.x + t*20.5, self.rect.y + t*5.5))
        self.screen.blit(self.rules_base_image, (
            self.rect.x + t*19.5, self.rect.y + t*7.5))

        self.screen.blit(self.rules_icons_image, (
            self.rect.x + t*20, self.rect.y + t*13.5))

        self.screen.blit(self.rules_victory_image, (
            self.rect.x + t*18, self.rect.y + t*17.5))