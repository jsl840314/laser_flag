# button.py

import pygame.font

class Button:


    def __init__(self, lf_game, msg, color, text_color, grid_position, width):
        """initialize button attributes"""
        self.screen = lf_game.screen
        self.settings = lf_game.settings
        self.frame_rect = lf_game.button_frame.rect
        self.tile_size = self.settings.tile_size
        self.font_size = int(0.75 * self.tile_size)

        # set dimensions and properties of the button
        self.width, self.height = self.tile_size * width, self.tile_size
        self.button_color = color
        self.text_color = text_color
        self.font = pygame.font.SysFont('tickerbit', self.font_size)

        # build the button's rect object and place it
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.x = self.frame_rect.x + self.tile_size*grid_position[0]
        self.rect.y = self.frame_rect.y + self.tile_size*grid_position[1]


        # the button message needs to be prepped only once
        self._prep_msg(msg)


    def _prep_msg(self, msg):
        """turn msg into a rendered image and center text on the button"""
        self.msg_image = self.font.render(msg, True,
                            self.text_color, self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center


    def draw_button(self):
        """draw blank button and then draw message"""
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)



if __name__ == "__main__":
    print(pygame.font.get_fonts())