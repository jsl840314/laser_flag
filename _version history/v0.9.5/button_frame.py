# button_frame.py

import pygame
import pygame.font


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
        lf_game.turn_button[self.teams[0]] = Button(lf_game, msg="END TURN",
            color=self.settings.team_color[self.teams[0]],
            text_color=self.settings.b_w_team_color[self.teams[0]],
            border_color=self.settings.alt_team_color[self.teams[0]],
            border_weight = 2,
            grid_position=(3, 1),
            width=3,
            alt_image=pygame.image.load('images/the_ever_seeing_eye.png'))

        lf_game.score_label[self.teams[0]] = Button(lf_game, msg='0',
            color=self.settings.team_color[self.teams[0]],
            text_color=self.settings.b_w_team_color[self.teams[0]],
            border_color=self.settings.alt_team_color[self.teams[0]],
            border_weight = 5,
            grid_position=(2, 2.5),
            width=5, height=2,
            font_factor = 1.5)

        lf_game.status_label[self.teams[0]] = Button(lf_game, msg='',
            color=self.settings.team_color[self.teams[0]],
            text_color=self.settings.b_w_team_color[self.teams[0]],
            border_color=self.settings.alt_team_color[self.teams[0]],
            border_weight = 5,
            grid_position=(1, 5),
            width=7, height=3,
            font_factor=0.55)

        lf_game.turn_button[self.teams[1]] = Button(lf_game, msg="END TURN",
            color=self.settings.team_color[self.teams[1]],
            text_color=self.settings.b_w_team_color[self.teams[1]],
            border_color=self.settings.alt_team_color[self.teams[1]],
            border_weight = 2,
            grid_position=(3, 19),
            width=3,
            alt_image=pygame.image.load('images/the_ever_seeing_eye.png'),
            visible=False)

        lf_game.score_label[self.teams[1]] = Button(lf_game, msg='0',
            color=self.settings.team_color[self.teams[1]],
            text_color=self.settings.b_w_team_color[self.teams[1]],
            border_color=self.settings.alt_team_color[self.teams[1]],
            border_weight = 5,
            grid_position=(2, 16.5),
            width=5, height=2,
            font_factor = 1.5)

        lf_game.status_label[self.teams[1]] = Button(lf_game, msg='',
            color=self.settings.team_color[self.teams[1]],
            text_color=self.settings.b_w_team_color[self.teams[1]],
            border_color=self.settings.alt_team_color[self.teams[1]],
            border_weight = 5,
            grid_position=(1, 13),
            width=7, height=3,
            font_factor=0.55)

        lf_game.laser_button = Button(lf_game, "",
            color='black', text_color='red',
            border_color='red', border_weight = 2,
            grid_position=(0.5, 9),
            width=8, height=3,
            visible=False)

        lf_game.roll_result_message = Button(lf_game, "",
            color='red', text_color='black',
            border_color='black', border_weight = 5,
            grid_position=(-17, 8.5),
            width=12, height=4, visible=False)

        lf_game.rules_button = Button(lf_game, "SHOW RULES",
            color=self.settings.btn_frame_color, text_color='gray',
            border_color='white', border_weight = 1,
            grid_position=(2.5, 10),
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



class Button:
    """a single button"""
    def __init__(self, lf_game, msg,
        color, text_color, border_color, border_weight,
        grid_position, width=1, height=1, visible=True,
        font_factor=0.75, alt_image=None):
        """initialize button attributes"""
        self.screen      = lf_game.screen
        self.settings    = lf_game.settings
        self.frame_rect  = lf_game.button_frame.rect
        self.tile_size   = self.settings.tile_size
        self.font_size   = int(font_factor * self.tile_size)
        self.visible     = visible
        self.two_lines   = False
        self.three_lines = False

        # set dimensions and properties of the button
        self.width        = self.tile_size * width
        self.height       = self.tile_size * height
        self.button_color = color
        self.text_color   = text_color
        self.border_color = border_color
        self.font         = pygame.font.SysFont(
                              self.settings.font, self.font_size)

        # build the button's border object and place it
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.x = self.frame_rect.x + self.tile_size*grid_position[0]
        self.rect.y = self.frame_rect.y + self.tile_size*grid_position[1]

        # build the button's main color and place it
        self.color_rect = pygame.Rect(0, 0, self.width-2*border_weight, self.height-2*border_weight)
        self.color_rect.x = self.frame_rect.x + self.tile_size*grid_position[0] + border_weight
        self.color_rect.y = self.frame_rect.y + self.tile_size*grid_position[1] + border_weight

        # render the text image
        self.prep_msg(msg)

        if alt_image:
            self.alt_image = alt_image
            self.alt_image_rect = self.alt_image.get_rect()
            self.alt_image_rect.center = self.rect.center
        else:
            self.alt_image = None


    def prep_msg(self, msg):
        """turn msg into a rendered image and center text on the button"""
        msg_list = msg.split('\n')
        if len(msg_list) == 2:
            tile_size     = self.settings.tile_size
            half_tile     = self.settings.tile_size * 1/2
            twothird_tile = self.settings.tile_size * 2/3
            self.two_lines = True
            self.three_lines = True
            self.top_line = self.font.render(msg_list[0], True,
                                              self.text_color,
                                              self.button_color)
            self.top_line_rect = self.msg_image.get_rect()
            self.top_line_rect.top = self.rect.top + twothird_tile
            self.top_line_rect.left = self.rect.left + half_tile

            self.bot_line = self.font.render(msg_list[1], True,
                                              self.text_color,
                                              self.button_color)
            self.bot_line_rect = self.msg_image.get_rect()
            self.bot_line_rect.bottom = self.rect.bottom - twothird_tile
            self.bot_line_rect.left = self.rect.left + half_tile

        elif len(msg_list) == 3:
            tile_size     = self.settings.tile_size
            half_tile     = self.settings.tile_size * 1/2
            twothird_tile = self.settings.tile_size * 2/3
            self.two_lines = False
            self.three_lines = True
            self.top_line = self.font.render(msg_list[0], True,
                                              self.text_color,
                                              self.button_color)
            self.top_line_rect = self.msg_image.get_rect()
            self.top_line_rect.top = self.rect.top + twothird_tile
            self.top_line_rect.left = self.rect.left + half_tile

            self.mid_line = self.font.render(msg_list[1], True,
                                              self.text_color,
                                              self.button_color)
            self.mid_line_rect = self.msg_image.get_rect()
            self.mid_line_rect.center = self.rect.center
            self.mid_line_rect.left = self.rect.left + half_tile

            self.bot_line = self.font.render(msg_list[2], True,
                                              self.text_color,
                                              self.button_color)
            self.bot_line_rect = self.msg_image.get_rect()
            self.bot_line_rect.bottom = self.rect.bottom - twothird_tile
            self.bot_line_rect.left = self.rect.left + half_tile

        elif len(msg_list) == 1:
            self.two_lines = False
            self.three_lines = False
            self.msg_image = self.font.render(msg, True,
                                              self.text_color,
                                              self.button_color)
            self.msg_image_rect = self.msg_image.get_rect()
            self.msg_image_rect.center = self.rect.center

        else:
            print(msg_list)
            print(1/0)


    def draw_button(self):
        """draw blank button and then draw message"""
        if self.visible:
            self.screen.fill(self.border_color, self.rect)
            self.screen.fill(self.button_color, self.color_rect)
            if self.two_lines:
                self.screen.blit(self.top_line, self.top_line_rect)
                self.screen.blit(self.bot_line, self.bot_line_rect)
            elif self.three_lines:
                self.screen.blit(self.top_line, self.top_line_rect)
                self.screen.blit(self.mid_line, self.mid_line_rect)
                self.screen.blit(self.bot_line, self.bot_line_rect)
            else:
                self.screen.blit(self.msg_image, self.msg_image_rect)

        elif self.alt_image:
            self.screen.blit(self.alt_image, self.alt_image_rect)



if __name__ == "__main__":
    print(pygame.font.get_fonts())