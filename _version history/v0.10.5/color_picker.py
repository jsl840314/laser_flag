import pygame


class ColorPicker:
    """sliders for red green and blue to choose a custom color"""

    def __init__(self, master_window, grid_position, label='', width=4, height=4):
        self.screen    = master_window.screen
        self.settings  = master_window.settings
        self.tile_size = self.settings.tile_size

        self.bg_color  = 'gray'

        self.width  = width  * self.tile_size
        self.height = height * self.tile_size
        self.rect   = pygame.Rect(0, 0, self.width, self.height)
        self.rect.x = grid_position[0] * self.tile_size
        self.rect.y = grid_position[1] * self.tile_size

        self.font_size  = int(self.tile_size / 1.5)
        self.font       = pygame.font.SysFont(self.settings.font, self.font_size)
        self.label      = self.font.render(label, True, 'black')
        self.label_rect = self.label.get_rect()
        self.label_rect.x = self.rect.x + (self.width-self.label_rect.width)//2
        self.label_rect.y = self.rect.y + 10

        self.sliders = [Slider(self, 'red', -60),
                        Slider(self, 'green', -30),
                        Slider(self, 'blue', 0)]

        self.swatch = pygame.Rect(0,0, 45, self.height*0.7)
        self.swatch.x = self.rect.centerx+20
        self.swatch.bottom = self.rect.bottom-10


    def set_color(self, color=(0,0,0)):
        """set the sliders and self.color from a given value"""
        self.sliders[0].set_value(color[0])
        self.sliders[1].set_value(color[1])
        self.sliders[2].set_value(color[2])



    def draw(self):
        """draw the elements of the picker"""
        self.screen.fill(self.bg_color, self.rect)
        self.screen.blit(self.label, self.label_rect)
        for slider in self.sliders:
            slider.draw()

        value_r = self.sliders[0].value
        value_g = self.sliders[1].value
        value_b = self.sliders[2].value
        self.color = (value_r, value_g, value_b)
        # print(color)
        self.screen.fill(self.color, self.swatch)






class Slider:
    """a single slider for the color picker"""
    def __init__(self, master, color, x_offset):
        self.w      = 12
        self.screen = master.screen
        self.color  = color
        self.rect   = pygame.Rect(0, 0, self.w*2, int(master.height*0.7))
        self.rect.centerx = master.rect.centerx + x_offset
        self.rect.bottom  = master.rect.bottom-10
        self.circle_position = (self.rect.centerx, self.rect.bottom-self.w)
        self.set_value(0)


    def draw(self):
        self.screen.fill('black', self.rect)
        pygame.draw.circle(self.screen, 'black', self.circle_position, self.w)
        pygame.draw.circle(self.screen, self.color, self.circle_position, self.w-2)



    def set_circle_position(self, y_value):
        """move the slider's circle to the chosen y_value"""
        # keep the circle on the slider
        if y_value > self.rect.bottom - self.w:
            y_value = self.rect.bottom - self.w
        elif y_value < self.rect.top + self.w:
            y_value = self.rect.top + self.w

        self.circle_position = (self.rect.centerx, y_value)
        self._determine_value(y_value)


    def set_value(self, value):
        """set the slider's position from a given 0-255 value"""
        self.value = value
        y_difference = (value * (self.rect.height-self.w*2)) // 255
        self.circle_position = (self.rect.centerx, (self.rect.bottom-self.w) - y_difference)




    def _determine_value(self, y_value):
        """determine the 0-255 value from the slider's position"""
        y_difference = (self.rect.bottom-self.w) - y_value
        self.value = (y_difference * 255) // (self.rect.height-self.w*2)




