# button_frame.py

import pygame
import pygame.font

from button import Button

class ButtonFrame():
    """a frame to hold buttons to control the game"""

    def __init__(self, lf_game):
        self.screen = lf_game.screen
        self.settings = lf_game.settings
        self.teams = self.settings.teams

        tile_size = self.settings.tile_size
        grid_size = self.settings.grid_size

        # set dimensions and properties of the button frame
        self.width, self.height = tile_size * 9, tile_size * grid_size
        self.frame_color = self.settings.btn_frame_color

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.x = tile_size * (grid_size+1)
        self.rect.y = tile_size / 2

    def draw_frame(self):
        self.screen.fill(self.frame_color, self.rect)

    def create_buttons(self, lf_game):
        lf_game.turn_button  = {}
        lf_game.score_label  = {}
        lf_game.status_label = {}

        # create the buttons; use buttons for score labels too
        lf_game.turn_button[self.teams[0]] = Button(self, msg="END TURN",
            color=self.settings.team_color[self.teams[0]],
            text_color=self.settings.b_w_team_color[self.teams[0]],
            border_color=self.settings.alt_team_color[self.teams[0]],
            border_weight = 2,
            grid_position=(25, 1.5), # need to add (22, 0.5) to convert to NewButton
            width=3,
            alt_image=pygame.image.load('images/the_ever_seeing_eye.png'))

        lf_game.score_label[self.teams[0]] = Button(lf_game, msg='0',
            color=self.settings.team_color[self.teams[0]],
            text_color=self.settings.b_w_team_color[self.teams[0]],
            border_color=self.settings.alt_team_color[self.teams[0]],
            border_weight = 5,
            grid_position=(24, 3),
            width=5, height=2,
            font_factor = 1.5)

        lf_game.status_label[self.teams[0]] = Button(lf_game, msg='',
            color=self.settings.team_color[self.teams[0]],
            text_color=self.settings.b_w_team_color[self.teams[0]],
            border_color=self.settings.alt_team_color[self.teams[0]],
            border_weight = 5,
            grid_position=(23, 5.5),
            width=7, height=3,
            font_factor=0.55)

        lf_game.turn_button[self.teams[1]] = Button(lf_game, msg="END TURN",
            color=self.settings.team_color[self.teams[1]],
            text_color=self.settings.b_w_team_color[self.teams[1]],
            border_color=self.settings.alt_team_color[self.teams[1]],
            border_weight = 2,
            grid_position=(25, 19.5),
            width=3,
            alt_image=pygame.image.load('images/the_ever_seeing_eye.png'),
            visible=False)

        lf_game.score_label[self.teams[1]] = Button(lf_game, msg='0',
            color=self.settings.team_color[self.teams[1]],
            text_color=self.settings.b_w_team_color[self.teams[1]],
            border_color=self.settings.alt_team_color[self.teams[1]],
            border_weight = 5,
            grid_position=(24, 17),
            width=5, height=2,
            font_factor = 1.5)

        lf_game.status_label[self.teams[1]] = Button(lf_game, msg='',
            color=self.settings.team_color[self.teams[1]],
            text_color=self.settings.b_w_team_color[self.teams[1]],
            border_color=self.settings.alt_team_color[self.teams[1]],
            border_weight = 5,
            grid_position=(23, 13.5),
            width=7, height=3,
            font_factor=0.55)

        lf_game.laser_button = Button(lf_game, "",
            color='black', text_color='red',
            border_color='red', border_weight = 2,
            grid_position=(22.5, 9.5),
            width=8, height=3,
            visible=False)

        lf_game.roll_result_message = Button(lf_game, "",
            color='red', text_color='black',
            border_color='black', border_weight = 5,
            grid_position=(5, 9),
            width=12, height=4, visible=False)

        lf_game.rules_button = Button(lf_game, "SHOW RULES",
            color=self.settings.btn_frame_color, text_color='gray',
            border_color='white', border_weight = 1,
            grid_position=(24.5, 10.5),
            width=4, height=1, visible=True)

        lf_game.buttons = (
            lf_game.turn_button[self.teams[0]],
            lf_game.score_label[self.teams[0]],
            lf_game.status_label[self.teams[0]],
            lf_game.turn_button[self.teams[1]],
            lf_game.score_label[self.teams[1]],
            lf_game.status_label[self.teams[1]],
            lf_game.rules_button,
            lf_game.roll_result_message,
            lf_game.laser_button)


if __name__ == "__main__":
    print(pygame.font.get_fonts())