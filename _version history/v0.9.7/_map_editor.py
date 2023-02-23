import sys

import pygame
from settings import Settings
from game_map import GameMap
from newbutton import NewButton
from units import BasicUnit, Sniper, Grunt, Scout

from lf_functions import game_caption

TESTMAP = '_test_map_save.txt'

class MapEditor:
    """overall class to manage the map editor program"""

    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode(
                (self.settings.screen_width, self.settings.screen_height))
        # res = f"{self.settings.screen_width}x{self.settings.screen_height}"
        pygame.display.set_caption(f"Map Editor for {game_caption()}")

        # build the game map and place the units
        self.game_map = GameMap(self, TESTMAP)
        self.all_units = []
        self.teams     = {self.settings.teams[0]: pygame.sprite.Group(),
                          self.settings.teams[1]: pygame.sprite.Group()}
        self.game_map.build_teams(self)

        self.button_colors = {'color': 'gray', 'text': 'white', 'border': 'dark blue',
            'sel color': 'yellow', 'sel text': 'black', 'sel border': 'white'}

        # track editing mode
        self.modes = ['none', 'terrain', 'base', 'team 1', 'team 2']
        self.edit_mode = self.modes[0]

        # create buttons
        self.mode_button = {}
        self.mode_button[self.modes[1]] = NewButton(self, "EDIT TERRAIN",
            color=self.button_colors['color'],
            text_color=self.button_colors['text'],
            border_color=self.button_colors['border'],
            sel_color=self.button_colors['sel color'],
            sel_text_color=self.button_colors['sel text'],
            sel_border_color=self.button_colors['sel border'],
            border_weight = 1,
            grid_position = (22, 1), width=5, height=1, visible=True)
        self.mode_button[self.modes[2]] = NewButton(self, "EDIT BASES",
            color=self.button_colors['color'],
            text_color=self.button_colors['text'],
            border_color=self.button_colors['border'],
            sel_color=self.button_colors['sel color'],
            sel_text_color=self.button_colors['sel text'],
            sel_border_color=self.button_colors['sel border'],
            border_weight = 1,
            grid_position = (22, 3), width=5, height=1, visible=True)
        self.mode_button[self.modes[3]] = NewButton(self, "TEAM 1 UNITS",
            color=self.button_colors['color'],
            text_color=self.button_colors['text'],
            border_color=self.button_colors['border'],
            sel_color=self.button_colors['sel color'],
            sel_text_color=self.button_colors['sel text'],
            sel_border_color=self.button_colors['sel border'],
            border_weight = 1,
            grid_position = (22, 5), width=5, height=1, visible=True)
        self.mode_button[self.modes[4]] = NewButton(self, "TEAM 2 UNITS",
            color=self.button_colors['color'],
            text_color=self.button_colors['text'],
            border_color=self.button_colors['border'],
            sel_color=self.button_colors['sel color'],
            sel_text_color=self.button_colors['sel text'],
            sel_border_color=self.button_colors['sel border'],
            border_weight = 1,
            grid_position = (22, 7), width=5, height=1, visible=True)
        self.save_button = NewButton(self, "SAVE MAP",
            color='red', text_color='black', border_color='red', border_weight=2,
            grid_position = (25, 20), width=5, height=1, visible=True)

        self._update_screen()


################################################################################
#   MAIN PROGRAM LOOP
################################################################################

    def run(self):
        while True:
            self._check_events()


    def _check_events(self):
        """respond to keypresses & mouse events"""
        for event in pygame.event.get():
            # if click on window X
            if event.type == pygame.QUIT:
                self._quit()
            # respond to other mouse clicks
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_button_clicks(mouse_pos)
                self._check_tile_clicks(mouse_pos)
                self._update_screen()


    def _check_button_clicks(self, mouse_pos):
        """respond to clicks on buttons"""
        edit_button_clicked = []
        for mode in self.modes[1:]:
            mode_button_clicked = self.mode_button[mode].rect.collidepoint(mouse_pos)
            save_button_clicked = self.save_button.rect.collidepoint(mouse_pos)
            if mode_button_clicked:
                self._change_edit_mode(mode)
        if save_button_clicked:
            self._save_map()


    def _check_tile_clicks(self, mouse_pos):
        """respond to clicks on tiles"""
        for tile in self.game_map.all_tiles:
            tile_clicked = tile.rect.collidepoint(mouse_pos)
            if tile_clicked:
                if self.edit_mode == 'terrain':
                    self._edit_terrain(tile)
                elif self.edit_mode == 'base':
                    self._edit_base(tile)
                elif self.edit_mode == 'team 1':
                    self._edit_team(tile, team='1')
                elif self.edit_mode == 'team 2':
                    self._edit_team(tile, team='2')
                break


    def _quit(self):
        pygame.quit()
        sys.exit()

################################################################################
#   EDITING THE MAP
################################################################################


    def _change_edit_mode(self, mode):
        """change edit mode"""
        # if currently selected mode is chosen, just unselect
        if mode == self.edit_mode:
            self.edit_mode = self.modes[0]
            self.mode_button[mode].unselect()
        else:
            # if a different mode was chosen, unselect it first
            if self.edit_mode != 'none':
                self.mode_button[self.edit_mode].unselect()
            # then select the chosen mode
            self.edit_mode = mode
            self.mode_button[mode].select()
        # prove it works
        print(self.edit_mode)


    def _edit_terrain(self, tile):
        """loop through the three terrain types"""
        if tile.type == 'level':
            tile.change_type('elevated')
        elif tile.type == 'elevated':
            if tile.occupied:
                tile.change_type('base_u')
            else:
                tile.change_type('wall')
        elif tile.type == 'wall':
            tile.change_type('base_u')
        elif 'base' in tile.type:
            tile.change_type('level')
        self.game_map.determine_adjoiners()
        self.game_map.determine_wallcaps()


    def _edit_base(self, tile):
        if tile.type == 'base_u':
            tile.change_type('base_1')
        elif tile.type == 'base_1':
            tile.change_type('base_2')
        elif tile.type == 'base_2':
            tile.change_type('base_u')


    def _edit_team(self, tile, team):

        # if tile is a wall, do nothing
        if tile.type != 'level':
            return

        # if tile is unoccupied, place a basic uit
        elif not tile.occupied:
            self._create_unit(tile, team, 'basic')

        # if tile is occupied with the other team, do nothing
        elif tile.occupied.team != team:
            return

        elif tile.occupied.unit_class == 'basic':
            self._delete_unit(tile)
            self._create_unit(tile, team, 'sniper')

        elif tile.occupied.unit_class == 'sniper':
            self._delete_unit(tile)
            self._create_unit(tile, team, 'scout')

        elif tile.occupied.unit_class == 'scout':
            self._delete_unit(tile)
            self._create_unit(tile, team, 'grunt')


        # delete the unit
        else:
            self._delete_unit(tile)


    def _create_unit(self, tile, team, unit_class):
        if unit_class == 'basic':
            unit = BasicUnit(self, team = team)
        elif unit_class == 'sniper':
            unit = Sniper(self, team = team)
        elif unit_class == 'grunt':
            unit = Grunt(self, team = team)
        elif unit_class == 'scout':
            unit = Scout(self, team = team)

        unit.tile = tile
        unit.rect.x = tile.rect.x
        unit.rect.y = tile.rect.y
        tile.occupied = unit
        self.all_units.append(unit)
        self.teams[team].add(unit)


    def _delete_unit(self, tile):
        unit = tile.occupied
        tile.occupied = False
        self.all_units.remove(unit)
        unit.kill()
        self._update_screen()




################################################################################
# SAVE AND LOAD
################################################################################

    def _save_map(self):
        map_string = ''
        for row in self.game_map.tiles:
            for tile in row:
                if tile.type == 'wall':
                    char = 'X'
                elif tile.type == 'elevated':
                    char = 'c'
                elif tile.type == 'level':
                    char = '_'
                elif tile.type == 'base_u':
                    char = 'B'
                elif tile.type == 'base_1':
                    char = '1'
                elif tile.type == 'base_2':
                    char = '2'

                if tile.occupied:
                    print(tile.row, tile.col)
                    print(tile.occupied.team, tile.occupied.unit_class)
                    if tile.occupied.team == '1':
                        if tile.occupied.unit_class == 'basic':
                            char = 'g'
                        if tile.occupied.unit_class == 'sniper':
                            char = 'h'
                        if tile.occupied.unit_class == 'grunt':
                            char = 'i'
                        if tile.occupied.unit_class == 'scout':
                            char = 'j'

                    elif tile.occupied.team == '2':
                        if tile.occupied.unit_class == 'basic':
                            char = 'm'
                        if tile.occupied.unit_class == 'sniper':
                            char = 'n'
                        if tile.occupied.unit_class == 'grunt':
                            char = 'o'
                        if tile.occupied.unit_class == 'scout':
                            char = 'p'

                map_string += char + ' '
            map_string += '\n'
        map_string.strip()

        with open(TESTMAP, 'w') as f:
            f.write(map_string)



################################################################################
# UPDATE SCREEN
################################################################################

    def _update_screen(self):
        """update images and flip to the new screen"""

        self.game_map.draw_map()

        for unit in self.all_units:
            unit.blitme()

        for mode, button in self.mode_button.items():
            button.draw_button()
        self.save_button.draw_button()

        pygame.display.flip()

################################################################################
#   NEW BUTTON CLASSm FOR THIS MODULE ONLY SO FAR
################################################################################



if __name__ == "__main__":
    mapeditor = MapEditor()
    mapeditor.run()
