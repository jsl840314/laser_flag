"""_roll_checker.py

print out roll probabilities for various dice combinations



roll 2D6:

required roll    ways to hit exact     ways to be >=      final chance
      2                1/36               36/36              100% 
      3                2/36               35/36               97% 
      4                3/36               33/36               92% 
      5                4/36               30/36               83% 
      6                5/36               26/36               72% 
      7                6/36               21/36               58% 
      8                5/36               15/36               42% 
      9                4/36               10/36               28% 
     10                3/36                6/36               17% 
     11                2/36                3/36                8% 
     12                1/36                1/36                3% 
"""

def find_index(find_value, list):
    for index, value in enumerate(list):
        if value == find_value:
            return index

def calc_two_dice(die_sides):
    die = range(1, die_sides+1)
    possible_results = range(2, 2*die_sides + 1)

    all_results = []
    for d1 in die:
        for d2 in die:
            all_results.append(d1 + d2)

    all_results.sort()

    all_probabilities = {}
    square = die_sides**2
    for result in possible_results:
        probability = (square - find_index(result, all_results)) / square
        all_probabilities[result] = probability
        print(f'roll {result} or greater: {probability}')

calc_two_dice(8)






class AttackRolls:
    def __init__(self, die_sides = 6, dice_number = 2):
        """show roll table for all combinations of attack and defense bonuses"""

        # initialize the dice for this table
        self.die_sides   = range(1, die_sides+1)
        self.dice_number = dice_number

        # initialize the units
        self.basic  = TestUnit()
        self.grunt  = TestUnit('grunt')
        self.scout  = TestUnit('scout')
        self.sniper = TestUnit('sniper')

    def roll_dice(self):
        """roll the given number of dice"""
        pass






class TestUnit:
    def __init__(self, unit_class = 'basic'):
        """define roll values for a basic unit"""
        self.unit_class          = 'basic'
        self.to_hit              = +7

        self.elevated_hit_bonus  = -2
        self.cover_defense_bonus = +2
        self.elev_defense_malus  = -2
        self.overwatch_penalty   = +2
        self.max_overwatch       = +2
        if unit_class == 'grunt':
            self._become_grunt()
        elif unit_class == 'scout':
            self._become_scout()
        elif unit_class == 'sniper':
            self._become_sniper()

    def _become_grunt(self):
        """roll as a Grunt"""
        self.unit_class           = 'grunt'
        self.cover_defense_bonus += 1
        self.elevated_hit_bonus  -= 1
        self.elev_defense_malus  += 1
        self.overwatch_penalty   += 1
        self.max_overwatch       += 1

    def _become_scout(self):
        """roll as a Scout"""
        self.unit_class           = 'scout'
        self.to_hit              += 1

    def _become_sniper(self):
        """roll as a Sniper"""
        self.unit_class           = 'sniper'
        self.to_hit              -= 1