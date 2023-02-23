"""_roll_checker.py

displays roll probabilities for all units & tactical situations for various
dice combinations
"""

def find_index(find_value, list):
    """checks a list for the first instance of find_value and returns its index"""
    for index, value in enumerate(list):
        if value == find_value:
            return index

def calc_dice_percentages(die_sides, num_dice = 2):
    """calculates the probabilities of rolling greater than each possible result
    of the seclected die size and dice number"""

    # make a list of all results for one die
    die = range(1, die_sides+1)

    # calculate all possible results
    min_roll = num_dice
    max_roll = num_dice*die_sides
    possible_results = range(min_roll, max_roll+1)

    all_results = []
    if num_dice == 2:
        maxresults = die_sides**2
        for d1 in die:
            for d2 in die:
                all_results.append(d1 + d2)
    else:
        maxresults = die_sides
        for d in die:
            all_results.append(d)
    all_results.sort()
    all_probabilities = {}

    for i in range(-10, 2):
        all_probabilities[i] = 100
    for i in range(2, 100):
        all_probabilities[i] = 0

    for result in possible_results:
        probability = (maxresults - find_index(result, all_results)) / maxresults
        all_probabilities[result] = round((probability * 100), 2)
    return all_probabilities



class AttackRolls:
    def __init__(self, settings, filename, die_sides = 6, dice_number = 2):
        """show roll table for all combinations of attack and defense bonuses"""

        # initialize the dice for this table
        self.die_sides   = range(1, die_sides+1)
        self.dice_number = dice_number
        self.prob_dict   = calc_dice_percentages(die_sides, dice_number)

        # initialize the units
        self.units = {
            'basic':  TestUnit(settings),
            'grunt':  TestUnit(settings, 'grunt'),
            'scout':  TestUnit(settings, 'scout'),
            'sniper': TestUnit(settings, 'sniper')}

        self.targets = {'basic':  TestUnit(settings),
                        'grunt':  TestUnit(settings, 'grunt')}

        # track how many 0% or 100% shots are in the table
        self.zeroes   = 0
        self.hundreds = 0

        msg =  f"Rolling {dice_number} {die_sides}-sided dice:\n"
        msg += f"(base roll {settings.base_to_hit}) "
        msg += f"(tactics modifier {settings.modifier_tactical_position }) "
        msg += f"(grunt extra tactics modifier {settings.modifier_extra_grunt_pos}) "
        msg += f"(sniper/scout hit modifier {settings.modifier_unit_class})\n\n"

        self.f = open(filename, 'w')

        self.f.write(msg)
        self._build_table()
        self.f.write(f"zeroes: {self.zeroes}\thundreds: {self.hundreds}")
        self.f.close


    def _build_table(self):

        for unit_class, unit in self.units.items():
            self.f.write(f"{unit_class.upper()} as shooter\n")
            self.f.write("\t\tnormal\t\t\tshooter elevated\tshooter on overwatch\n")
            self.f.write(self._create_line(unit, ' normal', 0))
            self.f.write(self._create_line(unit, ' basic elev.'  , self.targets['basic'].elev_defense_malus))
            self.f.write(self._create_line(unit, ' basic cover', self.targets['basic'].cover_defense_bonus))
            self.f.write(self._create_line(unit, ' grunt elev.'  , self.targets['grunt'].elev_defense_malus))
            self.f.write(self._create_line(unit, ' grunt cover', self.targets['grunt'].cover_defense_bonus))
            self.f.write('\n\n')


    def _create_line(self, unit, target_situation, roll_modifier):
        message = f'{target_situation}:\t'
        base_roll = unit.to_hit + roll_modifier
        base_prob = self.prob_dict[base_roll]
        if base_prob == 0:
            self.zeroes += 1
        elif base_prob == 100:
            self.hundreds += 1
        message += f"{base_roll} ({base_prob}%)\t\t"

        elevated_roll = base_roll + unit.elevated_hit_bonus
        elevated_prob = self.prob_dict[elevated_roll]
        if elevated_prob == 0:
            self.zeroes += 1
        elif elevated_prob == 100:
            self.hundreds += 1
        message += f"{elevated_roll} ({elevated_prob}%)\t\t"

        overwatch_roll = base_roll + unit.overwatch_penalty
        overwatch_prob = self.prob_dict[overwatch_roll]
        if overwatch_prob == 0:
            self.zeroes += 1
        elif overwatch_prob == 100:
            self.hundreds += 1
        message += f"{overwatch_roll} ({overwatch_prob}%)\n"

        return message


class TestUnit:
    def __init__(self, settings, unit_class = 'basic'):
        """define roll values for a basic unit"""
        self.to_hit                     = settings.base_to_hit
        self.modifier_tactical_position = settings.modifier_tactical_position
        self.modifier_extra_grunt_pos   = settings.modifier_extra_grunt_pos
        self.modifier_unit_class        = settings.modifier_unit_class

        self.elevated_hit_bonus  = -self.modifier_tactical_position
        self.cover_defense_bonus = +self.modifier_tactical_position
        self.elev_defense_malus  = -self.modifier_tactical_position
        self.overwatch_penalty   = +self.modifier_tactical_position


        self.unit_class = unit_class
        if unit_class == 'grunt':
            self._become_grunt()
        elif unit_class == 'scout':
            self._become_scout()
        elif unit_class == 'sniper':
            self._become_sniper()

    def _become_grunt(self):
        """roll as a Grunt"""
        self.unit_class           = 'grunt'
        self.elevated_hit_bonus  -= self.modifier_extra_grunt_pos
        self.cover_defense_bonus += self.modifier_extra_grunt_pos
        self.elev_defense_malus  -= self.modifier_extra_grunt_pos
        self.overwatch_penalty   += self.modifier_extra_grunt_pos

    def _become_scout(self):
        """roll as a Scout"""
        self.unit_class           = 'scout'
        self.to_hit              += self.modifier_unit_class

    def _become_sniper(self):
        """roll as a Sniper"""
        self.unit_class           = 'sniper'
        self.to_hit              -= self.modifier_unit_class






class Settings:
    def __init__(self):
        self.dice_sides                 = 6     # type of dice
        self.dice_num                   = 2     # number of dice
        self.base_to_hit                = 6     # base to-hit roll for all units
        self.modifier_tactical_position = 1     # modifer for cover or elevation
        self.modifier_extra_grunt_pos   = 1     # grunt extra positional modifier
        self.modifier_unit_class        = 1     # sniper/scout to hit modifier

settings = Settings()

filename =  f"{settings.dice_num}D{settings.dice_sides}"
filename += f"_base{settings.base_to_hit}"
filename += f"_tact{settings.modifier_tactical_position}"
filename += f"_grunt{settings.modifier_extra_grunt_pos}"
filename += f"_modclass{settings.modifier_unit_class}"

attack_rolls = AttackRolls(settings, f'{filename}.txt', settings.dice_sides, settings.dice_num)

