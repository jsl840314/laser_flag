# settings.py

class Settings:
    """a class to store all settings for Laser Flag"""

    def __init__(self):
        """initialize game settings"""

        # map settings
        self.tile_size = 40
        self.grid_size = 21

        self.map_width  = self.grid_size * self.tile_size
        self.map_height = self.grid_size * self.tile_size

        # screen settings
        self.screen_width  = self.map_width  + 12*self.tile_size
        self.screen_height = self.map_height + 2*self.tile_size

        # color settings
        self.bg_color = (20, 20, 30)
        self.player_1_color = (0, 255, 0)
        self.player_2_color = (255, 0, 255)


