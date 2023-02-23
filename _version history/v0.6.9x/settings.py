# settings.py

TILE_BITMAP_SIZE = 40

class Settings:
    """a class to store all settings for Laser Flag"""

    def __init__(self):
        """initialize game settings"""

        # default map settings
        #   grid_size can be altered by maps but should never exceed 21
        self.tile_size  = TILE_BITMAP_SIZE
        self.grid_size  = 21
        self.map_width  = self.grid_size * self.tile_size
        self.map_height = self.grid_size * self.tile_size

        # screen settings
        #   button frame is 9 tiles wide, plus 0.5 tile buffer
        #   at edges and between map and button frame
        self.screen_width  = int(self.map_width  + 10.5*self.tile_size)
        self.screen_height = int(self.map_height + 1*self.tile_size)

        # color settings
        self.bg_color        =       (20, 20, 30)
        self.btn_frame_color =       (50, 50, 50)
        self.team_color      = {}
        self.alt_team_color  = {}
        self.b_w_team_color  = {}

        self.team_color     ['g'] = (30, 30, 30) #"black"
        self.alt_team_color ['g'] = (180, 20, 20) #"red"
        self.b_w_team_color ['g'] = 'white'

        self.team_color     ['m'] = (180, 40, 180) #"magenta"
        self.alt_team_color ['m'] = (000, 200, 200) #"cyan"
        self.b_w_team_color ['m'] = 'black'

        # default unit settings
        self.base_max_ap              = +3
        self.base_move_speed          = +3  # higher value -> faster mover
        self.base_to_hit              = +6  # lower value  -> better shooter
        self.base_elevated_hit_bonus  = -1  # TACTICAL MODIFIER; better shooting if elevated
        self.base_cover_defense_bonus = +1  # TACTICAL MODIFIER; better defense in cover
        self.base_elev_defense_malus  = -1  # TACTICAL MODIFIER; poorer defense if elevated
        self.base_overwatch_penalty   = +1  # TACTICAL MODIFIER; overwatch shots are lower accuracy
        self.base_max_overwatch       = +2  # most units only get 2 overwatch shots

        # only Scout subclasses can climb onto cover and keep moving
        self.base_can_climb  = False

        self.scout_can_climb = True               # a bonus
        self.scout_to_hit              =    +1    # a malus
        self.scout_move_speed          =    +1    # a bonus

        # Snipers also get bonus shots; see their unique fire() method
        self.sniper_to_hit             =    -1    # a bonus
        self.sniper_move_speed         =    -1    # a malus

        # grunts have no special ability but their positioning is more critical
        self.grunt_cover_defense_bonus =    +1    # a bonus
        self.grunt_elevated_hit_bonus  =    -1    # a bonus
        self.grunt_elev_defense_malus  =    +1    # a malus
        self.grunt_overwatch_penalty   =    +1    # a malus
        self.grunt_max_overwatch       =    +1    # a bonus



        # allow different score limits for asymmetrical maps
        self.score_limit = {}
        self.score_limit['g']   = "..."
        self.score_limit['m']   = "..."

        # I think base shooting is not a necessary part of this game;
        #   base blocking is more interesting and I can call it "checkmate"
        # self.points_per_base = 5

        # dictionary to interpret ASCII codes from map files
        self.tile_dict = {
            'X': 'wall',
            'c': 'elevated',
            '_': 'level',
            'B': 'base_u',
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