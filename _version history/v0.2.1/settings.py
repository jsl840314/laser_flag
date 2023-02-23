# settings.py

TILESIZE = 40

class Settings:
    """a class to store all settings for Laser Flag"""

    def __init__(self):
        """initialize game settings"""

        # default map settings
        #   grid_size can be altered by maps but should never exceed 21
        self.tile_size  = TILESIZE
        self.grid_size  = 21
        self.map_width  = self.grid_size * self.tile_size
        self.map_height = self.grid_size * self.tile_size

        # screen settings
        #   button frame is 9 tiles wide, plus 0.5 tile buffer
        #   at edges and between map and button frame
        self.screen_width  = int(self.map_width  + 10.5*self.tile_size)
        self.screen_height = int(self.map_height + 1*self.tile_size)

        # color settings
        self.bg_color     = (20, 20, 30)
        self.team_g_color = (0, 255, 0)
        self.team_m_color = (255, 0, 255)

        # default unit settings
        self.base_to_hit      = 7
        self.base_move_speed  = 5
        self.base_cover_bonus = 2
        self.base_max_ap      = 3

        # dictionary to interpret ASCII codes from map files
        self.tile_dict = {
            'X': 'wall',
            'c': 'cover',
            '_': 'level',
            'G': 'base_g',
            'M': 'base_m',
            'g': 'unit_g_plain',
            'h': 'unit_g_sniper',
            'i': 'unit_g_grunt',
            'j': 'unit_g_scout',
            'm': 'unit_m_plain',
            'n': 'unit_m_sniper',
            'o': 'unit_m_grunt',
            'p': 'unit_m_scout'
        }

        # how many milliseconds between animation frames
        self.animation_speed = 25