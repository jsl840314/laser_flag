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
        self.bg_color       =       (20, 20, 30)
        self.team_color     = {'g': ('green'),
                               'm': ('magenta')}
        self.alt_team_color =  {'g': ('blue'),
                                'm': ('yellow')}

        # default unit settings
        self.base_max_ap              = 3
        self.base_move_speed          = 5   # higher value -> faster mover
        self.base_to_hit              = 8   # lower value  -> better shooter
        self.base_elevated_hit_bonus  = -2  # better shooting if elevated
        self.base_cover_defense_bonus = 2   # better defense in cover
        self.base_elev_defense_malus  = -2  # poorer defense if elevated

        # defaiult scoring values
        self.points_per_unit = 2
        self.points_per_base = 5

        # dictionary to interpret ASCII codes from map files
        self.tile_dict = {
            'X': 'wall',
            'c': 'elevated',
            '_': 'level',
            'G': 'base_g',
            'M': 'base_m',
            'g': 'unit_g_basic',
            'h': 'unit_g_sniper',
            'i': 'unit_g_grunt',
            'j': 'unit_g_scout',
            'm': 'unit_m_basic',
            'n': 'unit_m_sniper',
            'o': 'unit_m_grunt',
            'p': 'unit_m_scout'
        }

        # how many milliseconds between animation frames
        self.animation_speed = 50