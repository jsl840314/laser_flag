import pygame


class ColorPicker:
    """sliders for red green and blue to choose a custom color"""

    def __init__(self, master_window, grid_position, team='', width=4, height=6):
        self.screen    = master_window.screen
        self.settings  = master_window.settings
        self.tile_size = self.settings.tile_size

        self.color  = 'gray'

        self.width  = width  * self.tile_size
        self.height = height * self.tile_size
        self.rect   = pygame.Rect(0, 0, self.width, self.height)
        self.rect.x = grid_position[0] * self.tile_size
        self.rect.y = grid_position[1] * self.tile_size

        self.font_size  = int(self.tile_size / 1.5)
        self.font       = pygame.font.SysFont(self.settings.font, self.font_size)
        self.label      = self.font.render(f'Team {team} Colors', True, 'black')
        self.label_rect = self.label.get_rect()
        self.label_rect.x = self.rect.x + (self.width-self.label_rect.width)//2
        self.label_rect.y = self.rect.y + 10

    def draw(self):

        self.screen.fill(self.color, self.rect)
        self.screen.blit(self.label, self.label_rect)