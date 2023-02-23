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
        self.frame_color = self.settings.bg_color

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.x = self.tile_size
        self.rect.y = self.tile_size

        self._draw_unit_icons()
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
        self.tiles = [Tile(self, {'row': 1.5, 'col': 19.5, 'occupied': False, 'type': 'wall', 'ID': 0}),
                      Tile(self, {'row': 4.5, 'col': 19.5, 'occupied': False, 'type': 'elevated', 'ID': 0}),
                      Tile(self, {'row': 7.5, 'col': 19.5, 'occupied': False, 'type': 'level', 'ID': 0}),
                      Tile(self, {'row': 10.5, 'col': 19.5, 'occupied': False, 'type': 'base', 'ID': 0})]




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
            self.rect.x + t*20.5, self.rect.y + t*4.5))
        self.screen.blit(self.rules_level_image , (
            self.rect.x + t*20.5, self.rect.y + t*7.5))
        self.screen.blit(self.rules_base_image, (
            self.rect.x + t*20.5, self.rect.y + t*10.5))

        self.screen.blit(self.rules_victory_image, (
            self.rect.x + t*17, self.rect.y + t*18))