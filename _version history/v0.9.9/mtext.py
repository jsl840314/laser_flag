import pygame


class MText:
    """create a pygame render of a multi-line piece of text"""

    def __init__(self, lf_game, msg, font_size, text_color, justify='left', line_space = 0.8):
        self.screen = lf_game.screen
        self.settings = lf_game.settings
        self.teams = self.settings.teams
        self.font = pygame.font.SysFont(self.settings.font, font_size)
        self.color = text_color
        self.justify = justify
        self.line_space = line_space
        # self.line_spacing_factor = font_size * line_space
        self.msg_lines = msg.split('\n')
        self._render_and_dimension()


    def _render_and_dimension(self):
        """render all lines of text and determine dimensions of the entire MText object"""

        self.width = 0
        self.line_images = []

        for i, line in enumerate(self.msg_lines):
            line_image = self.font.render(line, True, self.color)
            self.line_images.append(line_image)
            line_rect = line_image.get_rect()

            # check if this line is wider than the current maximum
            if line_rect.width > self.width:
                self.width = line_rect.width

            # self.height += line_rect.height


            if i == 0:
                self.rect = line_rect
                self.line_spacing_factor = self.rect.height * self.line_space

        self.height = self.rect.height + (self.line_spacing_factor * (len(self.msg_lines)-1))



    def blitme(self, x, y):
        """draw the lines of text"""
        for i, line in enumerate(self.line_images):
            line_rect = line.get_rect()

            if self.justify == 'left':
                j_factor = 0
            elif self.justify == 'right':
                j_factor = self.width - line_rect.width
            elif self.justify == 'center':
                j_factor = (self.width - line_rect.width) // 2

            line_position = (x + j_factor, y + (i*self.line_spacing_factor))
            self.screen.blit(line, line_position)



