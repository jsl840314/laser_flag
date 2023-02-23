import pygame

class Victory:
    """methods for when one team wins the game"""

    def __init__(self, lf_game, victory_type, winner=None, loser=None):
        """three victory types are 'score' 'elimination' and 'checkmate'"""
        self.lf_game  = lf_game
        self.screen   = lf_game.screen
        self.settings = lf_game.settings

        self.bg_color = self.settings.bg_color

        self.teams    = self.settings.teams

        if winner:
            self.winner = winner
            self.teams.remove(winner)
            self.loser = self.teams[0]

        elif loser:
            self.loser = loser
            self.teams.remove(loser)
            self.winner = self.teams[0]

        self.victory_type = victory_type

        self.victory_message  = f"{self.victory_type.upper()}!"
        self.victory_message += f" Team {self.winner} wins!"


    def show_victory(self):
        """show a victory message"""

        font = pygame.font.SysFont(self.settings.font, 50)

        Cx = self.settings.map_width / 2
        Cy = self.settings.map_height / 2

        text_rect = pygame.Rect(Cx, Cy, 100, 100)

        text_image = font.render(self.victory_message, 'red', 'red')


        self.screen.fill(self.bg_color)
        self.screen.blit(text_image, text_rect)
        pygame.display.flip()