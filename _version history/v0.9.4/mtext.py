import pygame


class MText:
    """create a pygame render of a multi-line piece of text"""

    def __init__(self, lf_game, msg, font_size, text_color):
        self.screen = lf_game.screen
        self.settings = lf_game.settings
        self.teams = self.settings.teams
        self.font = pygame.font.SysFont(self.settings.font, font_size)
        self.color = text_color
        self.line_spacing_factor = font_size * 0.8
        self.msg_lines = msg.split('\n')


    def blitme(self, x, y):
        """draw the lines of text"""

        for i, line in enumerate(self.msg_lines):
            line_image = self.font.render(line, True, self.color)
            line_position = (x, y + (i*self.line_spacing_factor))
            self.screen.blit(line_image, line_position)



"""
                self.rules[]
                self.rules[]
                self.rules[]
                self.rules[]
                self.rules[]

"""