import pygame

from mtext import MText


class Button:
    """a single button"""
    def __init__(self, master_window, msg,
        color, text_color, border_color, border_weight=0,
        sel_color=None, sel_text_color=None, sel_border_color=None,
        grid_position=(0,0), width=1, height=1, visible=True,
        font_factor=0.75, alt_image=None, justify = 'left', line_space = 2):
        """initialize button attributes"""
        self.screen       = master_window.screen
        self.settings     = master_window.settings
        self.tile_size    = self.settings.tile_size
        self.font_size    = int(font_factor * self.tile_size)
        self.visible      = visible
        self.justify      = justify
        self.line_space   = line_space

        self.msg = msg

        # set dimensions and properties of the button
        self.width        = self.tile_size * width
        self.height       = self.tile_size * height
        self.button_color = color
        self.text_color   = text_color
        self.border_color = border_color

        if sel_color        != None: self.sel_button_color = sel_color
        else:                        self.sel_button_color = color

        if sel_text_color   != None: self.sel_text_color   = sel_text_color
        else:                        self.sel_text_color   = text_color

        if sel_border_color != None: self.sel_border_color = sel_border_color
        else:                        self.sel_border_color = border_color

        # self.font         = pygame.font.SysFont(
        #                       self.settings.font, self.font_size)

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
        self._create_mtext(self.sel_text_color)



    def unselect(self):
        """draw the button in an unselected state"""
        self.selected = False
        self._create_mtext(self.text_color)



    def prep_msg(self, msg):
        self.msg = msg
        self.unselect()


    def _create_mtext(self, text_color):
        """turn msg into a rendered image and center text on the button"""
        self.mtext = MText(self, self.msg, self.font_size, text_color, self.justify, self.line_space)



    def draw_button(self):
        """draw blank button and then draw message"""
        if self.visible:
            if not self.selected:
                self.screen.fill(self.border_color, self.rect)
                self.screen.fill(self.button_color, self.color_rect)
            else:
                self.screen.fill(self.sel_border_color, self.rect)
                self.screen.fill(self.sel_button_color, self.color_rect)

            x_add = (self.width  - self.mtext.width ) // 2
            y_add = (self.height - self.mtext.height) // 2
            self.mtext.blitme(self.rect.x + x_add, self.rect.y + y_add)

        elif self.alt_image:
            self.screen.blit(self.alt_image, self.alt_image_rect)