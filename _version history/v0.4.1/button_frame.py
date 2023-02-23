# button_frame.py

import pygame
import pygame.font


class ButtonFrame():
    """a frame to hold buttons to control the game"""

    def __init__(self, lf_game):
        self.screen = lf_game.screen
        self.settings = lf_game.settings
        tile_size = self.settings.tile_size
        grid_size = self.settings.grid_size

        # set dimensions and properties of the button frame
        self.width, self.height = tile_size * 9, tile_size * grid_size
        self.frame_color = (50, 50, 50)

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.x = tile_size * (grid_size+1)
        self.rect.y = tile_size / 2

    def draw_frame(self):
        self.screen.fill(self.frame_color, self.rect)



class Button:
    """a single button"""
    def __init__(self, lf_game, msg,
        color, text_color, border_color, border_weight,
        grid_position, width=1, height=1, visible=True,
        font_factor=0.75):
        """initialize button attributes"""
        self.screen     = lf_game.screen
        self.settings   = lf_game.settings
        self.frame_rect = lf_game.button_frame.rect
        self.tile_size  = self.settings.tile_size
        self.font_size  = int(font_factor * self.tile_size)
        self.visible    = visible
        self.two_lines  = False

        # set dimensions and properties of the button
        self.width        = self.tile_size * width
        self.height       = self.tile_size * height
        self.button_color = color
        self.text_color   = text_color
        self.border_color = border_color
        self.font         = pygame.font.SysFont(
                              'tickerbit', self.font_size)

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


    def prep_msg(self, msg):
        """turn msg into a rendered image and center text on the button"""
        msg_list = msg.split('\n')
        if len(msg_list) == 2:
            tile_size     = self.settings.tile_size
            half_tile     = self.settings.tile_size * 1/2
            twothird_tile = self.settings.tile_size * 2/3
            self.two_lines = True
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

        else:
            self.two_lines = False
            self.msg_image = self.font.render(msg, True,
                                              self.text_color,
                                              self.button_color)
            self.msg_image_rect = self.msg_image.get_rect()
            self.msg_image_rect.center = self.rect.center


    def draw_button(self):
        """draw blank button and then draw message"""
        self.screen.fill(self.border_color, self.rect)
        self.screen.fill(self.button_color, self.color_rect)
        if self.two_lines:
            self.screen.blit(self.top_line, self.top_line_rect)
            self.screen.blit(self.bot_line, self.bot_line_rect)
        else:
            self.screen.blit(self.msg_image, self.msg_image_rect)



if __name__ == "__main__":
    print(pygame.font.get_fonts())