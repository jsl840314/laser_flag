import pygame

from mtext import MText


class NewButton:
    """a single button"""
    def __init__(self, master_window, msg,
        color, text_color, border_color, border_weight,
        sel_color=None, sel_text_color=None, sel_border_color=None,
        grid_position=(0,0), width=1, height=1, visible=True,
        font_factor=0.75, alt_image=None):
        """initialize button attributes"""
        self.screen       = master_window.screen
        self.settings     = master_window.settings
        self.tile_size    = self.settings.tile_size
        self.font_size    = int(font_factor * self.tile_size)
        self.visible      = visible

        self.msg = msg

        # set dimensions and properties of the button
        self.width        = self.tile_size * width
        self.height       = self.tile_size * height
        self.button_color = color
        self.text_color   = text_color
        self.border_color = border_color

        self.sel_button_color = sel_color
        self.sel_text_color   = sel_text_color
        self.sel_border_color = sel_border_color

        self.font         = pygame.font.SysFont(
                              self.settings.font, self.font_size)

        # build the button's border object and place it
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.x = self.tile_size*grid_position[0]
        self.rect.y = self.tile_size*grid_position[1]

        # build the button's main color and place it
        self.color_rect = pygame.Rect(0, 0, self.width-2*border_weight, self.height-2*border_weight)
        self.color_rect.x = self.tile_size*grid_position[0] + border_weight
        self.color_rect.y = self.tile_size*grid_position[1] + border_weight

        # put the button in an unselected state
        self.unselect()

        if alt_image:
            self.alt_image = alt_image
            self.alt_image_rect = self.alt_image.get_rect()
            self.alt_image_rect.center = self.rect.center
        else:
            self.alt_image = None



    def select(self):
        """draw the button in a selected state"""
        self.selected = True
        self.prep_msg(self.sel_text_color, self.sel_button_color)

    def unselect(self):
        """draw the button in an unselected state"""
        self.selected = False
        self.prep_msg(self.text_color, self.button_color)




    def prep_msg(self, text_color, bg_color):
        """turn msg into a rendered image and center text on the button"""

        self.msg_image = self.font.render(self.msg, True,
                                          text_color,
                                          bg_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center



    def draw_button(self):
        """draw blank button and then draw message"""
        if self.visible:
            if not self.selected:
                self.screen.fill(self.border_color, self.rect)
                self.screen.fill(self.button_color, self.color_rect)
            else:
                self.screen.fill(self.sel_border_color, self.rect)
                self.screen.fill(self.sel_button_color, self.color_rect)
            self.screen.blit(self.msg_image, self.msg_image_rect)



