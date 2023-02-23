import os
import sys
import json

import pygame

import tkinter.filedialog

from settings import Settings
from game_map import GameMap
from button import Button
from units import BasicUnit, Sniper, Grunt, Scout

from lf_functions import game_caption

from color_picker import ColorPicker



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
        self.filename = tkinter.filedialog.askopenfilename(
            title='Load map file or Cancel to load an enpty map',
            initialdir='maps')
        if self.filename == '':
            self.filename = 'maps/__empty map.txt'
        self.game_map = GameMap(self, self.filename)
        self.all_units = []
        self.teams     = {self.settings.teams[0]: pygame.sprite.Group(),
                          self.settings.teams[1]: pygame.sprite.Group()}
        self.game_map.build_teams(self)

        self.button_colors = {'color': 'gray', 'text': 'white', 'border': 'dark blue',
            'sel color': 'yellow', 'sel text': 'black', 'sel border': 'white'}

        # editing mode
        self.modes = ['none', 'terrain', 'base', 'team 1', 'team 2']
        self.edit_mode = self.modes[0]
        self.mode_button = {}
        self.mode_button[self.modes[1]] = Button(self, "EDIT TERRAIN",
            color=self.button_colors['color'],
            text_color=self.button_colors['text'],
            border_color=self.button_colors['border'],
            sel_color=self.button_colors['sel color'],
            sel_text_color=self.button_colors['sel text'],
            sel_border_color=self.button_colors['sel border'],
            border_weight = 1,
            grid_position = (22, 1), width=4, height=1, visible=True)
        self.mode_button[self.modes[2]] = Button(self, "EDIT BASES",
            color=self.button_colors['color'],
            text_color=self.button_colors['text'],
            border_color=self.button_colors['border'],
            sel_color=self.button_colors['sel color'],
            sel_text_color=self.button_colors['sel text'],
            sel_border_color=self.button_colors['sel border'],
            border_weight = 1,
            grid_position = (27, 1), width=4, height=1, visible=True)
        self.mode_button[self.modes[3]] = Button(self, "EDIT TEAM 1",
            color=self.button_colors['color'],
            text_color=self.button_colors['text'],
            border_color=self.button_colors['border'],
            sel_color=self.button_colors['sel color'],
            sel_text_color=self.button_colors['sel text'],
            sel_border_color=self.button_colors['sel border'],
            border_weight = 1,
            grid_position = (22, 3), width=4, height=1, visible=True)
        self.mode_button[self.modes[4]] = Button(self, "EDIT TEAM 2",
            color=self.button_colors['color'],
            text_color=self.button_colors['text'],
            border_color=self.button_colors['border'],
            sel_color=self.button_colors['sel color'],
            sel_text_color=self.button_colors['sel text'],
            sel_border_color=self.button_colors['sel border'],
            border_weight = 1,
            grid_position = (27, 3), width=4, height=1, visible=True)


        # color pickers
        self.color_pickers = {
            '1 main': ColorPicker(self, (22, 5), label='Main Color'),
            '2 main': ColorPicker(self, (27, 5), label='Main Color'),
            '1 alt': ColorPicker(self, (22, 10), label='Secondary Color'),
            '2 alt': ColorPicker(self, (27, 10), label='Secondary Color')
        }
        self.slider_picked = None

        self.b_w_button = {}
        self.b_w_button['1'] = Button(self, "ICON COLOR",
            color='black',
            text_color='white',
            border_color='white',
            sel_color='white',
            sel_text_color='black',
            sel_border_color='black',
            border_weight = 3,
            grid_position = (22, 15), width=4, height=1, visible=True)
        self.b_w_button['2'] = Button(self, "ICON COLOR",
            color='black',
            text_color='white',
            border_color='white',
            sel_color='white',
            sel_text_color='black',
            sel_border_color='black',
            border_weight = 3,
            grid_position = (27, 15), width=4, height=1, visible=True)

        self.score_buttons = {
            'down arrow 1': Button(self, "<",
                    color='black',
                    text_color='white',
                    border_color='white',
                    border_weight = 0,
                    grid_position = (22, 18), width=1, height=1, visible=True),
            'score 1': Button(self, "0",
                    color='black',
                    text_color='white',
                    border_color='black',
                    border_weight = 0,
                    grid_position = (23, 18), width=1, height=1, visible=True),
            'up arrow 1': Button(self, ">",
                    color='black',
                    text_color='white',
                    border_color='white',
                    border_weight = 0,
                    grid_position = (24, 18), width=1, height=1, visible=True),
            'down arrow 2': Button(self, "<",
                    color='black',
                    text_color='white',
                    border_color='white',
                    border_weight = 0,
                    grid_position = (28, 18), width=1, height=1, visible=True),
            'score 2': Button(self, "0",
                    color='black',
                    text_color='white',
                    border_color='black',
                    border_weight = 0,
                    grid_position = (29, 18), width=1, height=1, visible=True),
            'up arrow 2': Button(self, ">",
                    color='black',
                    text_color='white',
                    border_color='white',
                    border_weight = 0,
                    grid_position = (30, 18), width=1, height=1, visible=True)
        }


        # save & load
        self.save_button = Button(self, "SAVE MAP",
            color='red', text_color='black', border_color='red', border_weight=2,
            grid_position = (25, 20), width=5, height=1, visible=True)

        self._load_default_settings()
        self._update_screen()


################################################################################
#   MAIN PROGRAM LOOP
################################################################################

    def run(self):
        while True:
            self._check_events()
            if self.slider_picked != None:
                mouse_pos = pygame.mouse.get_pos()
                y_value = mouse_pos[1]
                self.slider_picked.set_circle_position(y_value)
                self._update_screen()


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
                self._check_slider_clicks(mouse_pos)
                self._check_tile_clicks(mouse_pos)
                self._update_screen()

            elif event.type == pygame.MOUSEBUTTONUP:
                if self.slider_picked != None:
                    mouse_pos = pygame.mouse.get_pos()
                    y_value = mouse_pos[1]
                    self.slider_picked.set_circle_position(y_value)
                    self.slider_picked = None
                    self._update_team_colors()
                    self._update_screen()


    def _check_button_clicks(self, mouse_pos):
        """respond to clicks on buttons"""
        # edit_button_clicked = []
        for mode in self.modes[1:]:
            mode_button_clicked = self.mode_button[mode].rect.collidepoint(mouse_pos)
            if mode_button_clicked:
                self._change_edit_mode(mode)

        save_button_clicked = self.save_button.rect.collidepoint(mouse_pos)
        if save_button_clicked:
            self._save_map()

        for button in self.b_w_button.values():
            button_clicked = button.rect.collidepoint(mouse_pos)
            if button_clicked:
                if button.selected:
                    button.unselect()
                else:
                    button.select()
                self._update_team_colors()


    def _check_slider_clicks(self, mouse_pos):
        """respond to clicks on the color sliders"""
        for color_picker in self.color_pickers.values():
            for slider in color_picker.sliders:
                slider_clicked = slider.rect.collidepoint(mouse_pos)
                if slider_clicked:
                    y_value = mouse_pos[1]
                    slider.set_circle_position(y_value)
                    self.slider_picked = slider
                    break



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
        if tile.type == 'wall':
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
# CHANGING COLORS
################################################################################

    def _update_team_colors(self):
        """update the team colors from the pickers and buttons"""
        # team 1
        self.settings.team_color ['1'] = self.color_pickers['1 main'].color
        self.settings.alt_team_color ['1'] = self.color_pickers['1 alt'].color
        if self.b_w_button['1'].selected:
            self.settings.b_w_team_color['1'] = 'black'
        else:
            self.settings.b_w_team_color['1'] = 'white'
        # team 2
        self.settings.team_color ['2'] = self.color_pickers['2 main'].color
        self.settings.alt_team_color ['2'] = self.color_pickers['2 alt'].color
        if self.b_w_button['2'].selected:
            self.settings.b_w_team_color['2'] = 'black'
        else:
            self.settings.b_w_team_color['2'] = 'white'




    def _load_default_settings(self):
        """load default team colors and score limits from settings"""
        # team 1
        self.color_pickers['1 main'].set_color(self.settings.team_color ['1'])
        self.color_pickers['1 alt'].set_color(self.settings.alt_team_color ['1'])
        if self.settings.b_w_team_color['1'] == 'black':
            self.b_w_button['1'].select()
        else:
            self.b_w_button['1'].unselect()
        self.score_buttons['score 1'].prep_msg(str(self.settings.score_limit['1']))

        # team 2
        self.color_pickers['2 main'].set_color(self.settings.team_color ['2'])
        self.color_pickers['2 alt'].set_color(self.settings.alt_team_color ['2'])
        if self.settings.b_w_team_color['2'] == 'black':
            self.b_w_button['2'].select()
        else:
            self.b_w_button['2'].unselect()
        self.score_buttons['score 2'].prep_msg(str(self.settings.score_limit['2']))

################################################################################
# SAVE AND LOAD
################################################################################

    def _save_map(self):
        tile_list = []
        unit_list = []
        for row in self.game_map.tiles:
            row_list = []
            for tile in row:
                row_list.append(tile.type)
            tile_list.append(row_list)


        for unit in self.all_units:
            unit_data = tuple((unit.team, unit.unit_class, unit.tile.row, unit.tile.col))
            unit_list.append(unit_data)

        map_dict = {'tiles': tile_list,
                    'units': unit_list}

        map_json = json.dumps(map_dict, indent=4)


        filename = tkinter.filedialog.asksaveasfilename(
            defaultextension='.txt', title='Save map file', initialdir='maps')

        if filename != '':

            if filename[-4:] != '.txt':
                filename += '.txt'

            with open(f'{filename}', 'w') as f:
                f.write(map_json)




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

        for color_picker in self.color_pickers.values():
            color_picker.draw()

        self.b_w_button['1'].draw_button()
        self.b_w_button['2'].draw_button()

        for button in self.score_buttons.values():
            button.draw_button()

        pygame.display.flip()

################################################################################
#   NEW BUTTON CLASSm FOR THIS MODULE ONLY SO FAR
################################################################################


if __name__ == "__main__":
    mapeditor = MapEditor()
    mapeditor.run()
