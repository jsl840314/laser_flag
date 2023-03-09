# rules.py

import pygame

from tile import Tile
from units import BasicUnit, Sniper, Grunt, Scout
from mtext import MText


class Rules():
    """a frame to show the game rules"""

    def __init__(self, lf_game):
        self.screen = lf_game.screen
        self.settings = lf_game.settings
        self.tile_size = self.settings.tile_size
        self.grid_size = self.settings.grid_size

        self.text_size = 20
        self.text_color = 'gray'

        # set dimensions and properties of the rules frame
        self.width, self.height = self.tile_size * 29, self.tile_size * 20
        self.frame_color = (50, 50, 80)# self.settings.bg_color

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.x = self.tile_size
        self.rect.y = self.tile_size

        self._draw_unit_icons()
        self._draw_misc_icons()
        self._draw_tile_icons()
        self._create_strings()
        self._draw_text()


    def _draw_unit_icons(self):
        """draw the units on the rules pane"""

        t = self.tile_size
        self.units = []
        col = 1.5

        for team in self.settings.teams:

            basic  = BasicUnit(self, team=team)
            basic.rect.x = (col + 0.5) * t
            basic.rect.y = (8.5) * t
            basic.tile = Tile(self,  {'row': 8, 'col': col, 'occupied': False,
                    'type': 'level', 'ID': 0})
            self.units.append(basic)

            scout  = Scout(self,     team=team)
            scout.rect.x = (col + 0.5) * t
            scout.rect.y = (13) * t
            scout.tile = Tile(self,  {'row': 12.5, 'col': col, 'occupied': False,
                    'type': 'level', 'ID': 0})
            self.units.append(scout)

            sniper = Sniper(self,    team=team)
            sniper.rect.x = (col + 0.5) * t
            sniper.rect.y = (15.5) * t
            sniper.tile = Tile(self,  {'row': 15, 'col': col, 'occupied': False,
                    'type': 'level', 'ID': 0})
            self.units.append(sniper)

            grunt  = Grunt(self,     team=team)
            grunt.rect.x = (col + 0.5) * t
            grunt.rect.y = (18) * t
            grunt.tile = Tile(self,  {'row': 17.5, 'col': col, 'occupied': False,
                    'type': 'level', 'ID': 0})
            self.units.append(grunt)

            col += 1.5






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
                                 'type': f'base_{self.settings.teams[0]}', 'ID': 0}),
                      Tile(self, {'row': 9.5, 'col': 20.2, 'occupied': False,
                                 'type': f'base_{self.settings.teams[1]}', 'ID': 0})]


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
        self.rules_main_image = MText(self, self.rules['main'],
            self.text_size, self.text_color, line_space_factor=1)
        self.rules_plain_image = MText(self, self.rules['plain unit'],
            self.text_size, self.text_color, line_space_factor=1)
        self.rules_units_image = MText(self, self.rules['unit classes'],
            self.text_size, self.text_color, line_space_factor=1)
        self.rules_tiles_image = MText(self, self.rules['tile types'],
            self.text_size, self.text_color, line_space_factor=1)
        self.rules_basenote_image = MText(self, self.rules['base note'],
            self.text_size, self.text_color, line_space_factor=1)
        self.rules_victory_image = MText(self, self.rules['victory'],
            self.text_size, self.text_color, line_space_factor=1)
        self.rules_icons_image = MText(self, self.rules['icons'],
            self.text_size, self.text_color, line_space_factor=1)


    def show(self):
        """show the rules"""
        t = self.tile_size

        # fill the screen
        self.screen.fill(self.frame_color, self.rect)


        # show MText
        self.rules_main_image.blitme(self.rect.x + t, self.rect.y + t)
        self.rules_plain_image.blitme(self.rect.x + t*4, self.rect.y + t*7.9)
        self.rules_units_image.blitme(self.rect.x + t*4, self.rect.y + t*12.4)
        self.rules_tiles_image.blitme(self.rect.x + t*20.5, self.rect.y + t*1.3)
        self.rules_basenote_image.blitme(self.rect.x + t*18.5, self.rect.y + t*10.5)
        self.rules_icons_image.blitme(self.rect.x + t*16, self.rect.y + t*12.5)
        self.rules_victory_image.blitme(self.rect.x + t*15, self.rect.y + t*17)


        # show the units
        for unit in self.units:
            unit.blitme()

        # show the tiles
        for tile in self.tiles:
            tile.blitme()

        # show the misc icons
        self.screen.blit(self.icon_el, (                # elevated
            self.rect.x + t*15, self.rect.y + t*13.2))
        self.screen.blit(self.icon_cv, (                # covered
            self.rect.x + t*21, self.rect.y + t*13.3))
        self.screen.blit(self.icon_mv, (                # can move
            self.rect.x + t*15.6, self.rect.y + t*14.1))
        self.screen.blit(self.icon_nm, (                # no move
            self.rect.x + t*15.9, self.rect.y + t*14.1))
        self.screen.blit(self.icon_ap_1, (              # 1 AP
            self.rect.x + t*15.6, self.rect.y + t*14.1))
        self.screen.blit(self.icon_ap_2, (              # 2 AP
            self.rect.x + t*15.9, self.rect.y + t*14.1))
        self.screen.blit(self.icon_sn, (                # snapshot eyes
            self.rect.x + t*21.2, self.rect.y + t*14))
        self.screen.blit(self.icon_un, (                # uncharged (red)
            self.rect.x + t*15.3, self.rect.y + t*15))
        self.screen.blit(self.icon_ch, (                # charging (blue)
            self.rect.x + t*20.9, self.rect.y + t*15))








    def _create_strings(self):
        """build the strings to display on the Rules screen
                self.rules['main']
                self.rules['plain unit']
                self.rules['unit subclasses']
                self.rules['tile types']
                self.rules['base note']
                self.rules['victory']
                self.rules['icons']
        """
        self.rules = {}

        self.rules['main'] = """
Players take turns controlling teams of units in a game of laser tag. Each unit may perform three actions
per turn. An action point (AP) may be used to move a certain number of squares, or to fire a laser. Firing
consumes the remainder of that unit's turn (except for Sniper units; see below).

The map consists of floor, cover, and walls. A unit adjacent to a wall or cover is IN COVER in a 180° arc in
that direction. Units may climb on cover tiles to an ELEVATED position, but climbing consumes the remainder
of one AP (except for Scouts, who can climb freely). An elevated unit may still take cover next to walls.

Lasers may be fired at any opposing unit within line-of-sight. A successful hit (determined by by the sum
of two D6 dice) is worth one point, and deactivates the target's laser. To reactivate a laser, the unit
must step on a base tile. Bases can be specific to one team, or universal.

A unit that retains some AP at the end of the turn may return fire during enemy moves; but with a roll
penalty. If multiple units have line of sight, they will take turns until a hit is scored. Available
snap shots are triggered any time a unit moves into or fires from a tile within line-of-sight.""".strip()



        self.rules['plain unit'] = """
Plain unit: move 4 squares per AP
                 roll 7 or greater to hit
                 +1 defense bonus if in cover
                 -1 defense penalty if on elevated ground
                 -1 attack bonus (low rolls are better) if on elevated ground
                 max 2 AP carried into enemy turn for snapshots
                 +1 attack penalty for snap shots

Other classes use these rules unless specified below:""".strip()



        self.rules['unit classes'] = """
Scout:  climbing onto elevated ground doesn't consume the whole AP
            move 5 squares per AP
            roll 8 or greater to hit



Sniper: firing only consumes 1 AP, but may not move after firing
            move 3 squares per AP
            roll 6 or greater to hit




Grunt:  max 3 AP carry over for snap shots
            +2 attack penalty for snap shots
            +2 defense bonus if in cover
            -2 defense penalty if on elevated ground
            -2 attack bonus if on elevated ground
        """.strip()



        self.rules['tile types'] = """
Wall:  blocks movement and line-of-sight




Cover: slows movement except for scouts





Floor: no movement restrictions




Universal Base: any unit may recharge here




     Team Base: only one team's units
                can use this base""".strip()



        self.rules['base note'] = """
NOTE: not all maps include bases for both teams, or universal
bases. If there is no valid recharging base for its team, any
unit hit by a laser is disqualified and removed from the room.""".strip()



        self.rules['victory'] = """
Victory conditions:

CHECKMATE:  deactivate all of a team's lasers and occupy any bases they could use
ELIMINATION:  disqualify all units of a team
SCORE:            first team to the map's score limit
""".strip()



        self.rules['icons'] = """
Status icons:

     on elevated terrain                              indicates cover direction


     AP counter (red: no move)                  snapshot counter


     laser uncharged                                 laser charging""".strip()