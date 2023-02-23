Laser Flag, a tactical shooting game by Jesse Stuart Leitch


################################################################################
RUNNING THE GAME
################################################################################

Laser Flag is written in Python 3.10.2; the only non-standard module you might
need to install is Pygame. I used version 2.1.2

__launcher.py will display a menu allowing you to choose a map or open the Map
Editor. You can run laser_flag.py directly, but it will just load a tsting map.



#############################################
NOTES FOR BETA TESTERS
#############################################

I'm not sure about all the roll modifiers or movement speeds; those parts of the
rules will require some playtesting in order to get the best balance. The end
goal is a game that rewards offensive risk-taking and defensive prudence in
about equal measure.

After a few rounds of playtesting, I found that the Player 1 gains a noticeable
advantage by moving first. I was concerned by this, but then I remembered that
even Chess is asymmetrical: at the Grandmaster level, it's quite rare for Black
to checkmate White. For a fair match, both players must play as Black and White
an equal number of times in a series of games. So, some of the maps have certain
asymmetries in an attempt to reduce or accentuate the Player 1 advantage. Use
the included map editor to help come up with different game modes!



################################################################################
RULES
################################################################################

Players take turns controlling teams of units in a game of laser tag. Each unit
may perform three actions per turn. An action point (AP) may be used to move a
certain number of squares, or to fire a laser. Firing consumes the remainder of
that unit's turn (except for Sniper units; see below).

The map consists of floor, cover, and walls. A unit adjacent to a wall or cover
is IN COVER in a 180° arc in that direction. Units may climb on cover tiles to
an ELEVATED position, but climbing consumes the remainder of one AP (except for
Scouts, who can climb freely). An elevated unit may still take cover next to
walls.

Lasers may be fired at any opposing unit within line-of-sight. A successful hit
(determined by by the sum of two D6 dice) is worth one point, and deactivates
the target's laser. To reactivate a laser, the unit must step on a base tile.
Bases can be specific to one team, or universal.

A unit that retains some AP at the end of the turn may return fire during enemy
moves; but with a roll penalty. If multiple units have line of sight, they will
take turns until a hit is scored. Available snap shots are triggered any time a
unit moves into or fires from a tile within line-of-sight.

Laser Flag was designed to be fully playable as a board game. It should be easy
to play with nothing more than a Lego set, a pair of six-sided dice, and a piece
of string to determine lines-of-sight. The larger "Duplo" blocks might make more
sense.

NOTE: not all maps include bases for both teams, or universal bases. If there is
no valid recharging base for its team, any unit hit by a laser is disqualified
and removed from the room.

UNIT CLASSES:
Plain unit: move 4 squares per AP
            roll 7 or greater to hit
            +1 defense bonus if in cover
            -1 defense penalty if on elevated ground
            -1 attack bonus (low rolls are better) if on elevated ground
            max 2 AP carried into enemy turn for snapshots
            +1 attack penalty for snap shots
Other classes use these rules unless specified below:

Scout:  climbing onto elevated ground doesn't consume the whole AP
        move 5 squares per AP
        roll 8 or greater to hit

Sniper: firing only consumes 1 AP, but may not move after firing
        move 3 squares per AP
        roll 6 or greater to hit

Grunt:  max 3 AP carry over for snap shots
        +2 attack penalty for snap shots
        +2 defense bonus if in cover
        -2 defense penalty if on elevated ground
        -2 attack bonus if on elevated ground

VICTORY CONDITIONS:
CHECKMATE: deactivate all of a team's lasers and occupy any bases they could use
ELIMINATION: disqualify all units of a team
SCORE: first team to the map's score limit


Several possible game modes are implied, depending on the map conditions:

    Capture the Flag: each team has at least one base
    Victory conditions: all enemy lasers are discharged and bases are blocked AND/OR
                        first to a set score AND/OR
                        highest score after set number of turns AND/OR

    Assault: only one team has a base
    Victory conditions:  Capture the Flag victory conditions AND/OR:
                            team with no base is on offense
                            other team is on defense
                            offense tries to score as many points
                                as possible before all their units
                                are eliminated

    Elimination: no bases on the map
    Victory conditions: Capture the Flag victory conditions AND/OR:
                            last man standing wins


Line-of-sight rules:
    If a line can be drawn from any part of a unit's square to any part of a
    target tile, without a wall blocking it, then the unit can hit that tile
    with his laser.


################################################################################
PROJECT ROADMAP
################################################################################


make the victory screen look a little nicer

revise line of sight to draw from edge midpoints as well; but only from the nearest 5 points:
    _Tile class should contain 8 dictionaries, each one containing a set of
        corner points
    LOS calculator just needs another elif to generate a new set of test lines

maybe build a GUI main menu / map loader? 

################################################
When all of the above are complete, issue v1.0.0
################################################

Maybe: fog of war option

Add sounds and music