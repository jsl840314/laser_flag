# settings.py

TILESIZE = 40

class Settings:
    """a class to store all settings for Laser Flag"""

    def __init__(self):
        """initialize game settings"""

        # default map settings
        #   grid_size can be altered by maps but should never exceed 21
        self.tile_size = TILESIZE
        self.grid_size = 21

        self.map_width  = self.grid_size * self.tile_size
        self.map_height = self.grid_size * self.tile_size

        # screen settings
        #   button frame is 9 tiles wide, plus 0.5 tile buffer
        #   at edges and between map and button frame
        self.screen_width  = int(self.map_width  + 10.5*self.tile_size)
        self.screen_height = int(self.map_height + 1*self.tile_size)

        # color settings
        self.bg_color = (20, 20, 30)
        self.team_g_color = (0, 255, 0)
        self.team_m_color = (255, 0, 255)

        # how many milliseconds between animation frames
        self.animation_speed = 25


