import pygame

WIDTH = 3

class Laser:
    """draws a three-color laser using one team's colors"""

    def __init__(self, lf_game, team, A, B):
        self.screen = lf_game.screen
        self.settings = lf_game.settings


        self.color_1 = self.settings.team_color[team]
        self.color_2 = self.settings.alt_team_color[team]
        self.color_3 = self.settings.b_w_team_color[team]

        self.A = A
        self.B = B

        self.width = self.settings.laser_width


    def draw(self):
        """draw the laser on the screen; need to flip afterward though"""
        pygame.draw.line(self.screen, self.color_1,
            (self.A.x, self.A.y),
            (self.B.x, self.B.y), self.width*5)
        pygame.draw.line(self.screen, self.color_2,
            (self.A.x, self.A.y),
            (self.B.x, self.B.y), self.width*3)
        pygame.draw.line(self.screen, self.color_3,
            (self.A.x, self.A.y),
            (self.B.x, self.B.y), self.width)
