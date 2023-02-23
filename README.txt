Laser Flag, by Jesse Stuart Leitch

Version History:
v0.10.5 02/22/2023  fixed bug where Grunts had too high elevation defense
v0.10.4 02/22/2023  added team names to main game and map editor; added a call
                        to a tkinter dialog box in each to change them; updated
                        all mpa files to include team names
v0.10.3 02/22/2023  implemented score buttons; put colors & score limits
                        into the JSON builder and implemented them in
                        game_map._read_map() as well
                    saved all maps with the new JSON format
v0.10.2 02/21/2023  wrapped up the color picker; minor bug in that unit icons
                        do not switch with the b/w switch unless unit is killed
                        and recreated; need to load both images in unit def to
                        fix, but maybe not necessary
                    still need to make score limit buttons work, and then add
                        color & score limit settings into JSON save and load
                        methods in game_map and map_editor
v0.10.1 02/21/2023  corrected yesterdays dates in this list
                    started a color picker class for the map editor
v0.10.0 02/20/2023  changed map format to JSON; new _load_map method in game map
                        and _save_map in map editor (renamed old methods for now)
v0.9.10 02/20/2023  raised base to-hit back to 7
                    tweaked rules screen to fit with new mtext definition
v0.9.9  02/20/2023  I think mtext and buttons are playing well together now
v0.9.8  02/20/2023  got rid of the old Button class and replaced it with the new
                        one with MText capability. Still need to work out mtext
                        positioning kinks but it's pretty decent.
v0.9.7  02/19/2023  map editor now has ability to adjust units
v0.9.6  02/19/2023  map editor half functional; can load/save but still need to
                        be able to adjust units, team colors, score limit
                    also need to come up with a more elaborate map format:
                        - need to be able to start units on elevated ground
                        - need to save team colors and score limit with the map
                    made a new button class with alt colors; need to incorporate
                        the MText class into its labeling and then use it for
                        the main game button frame
v0.9.5  02/19/2023  started work on a map editor:
                        moved Tile class image loader out of __init__
                            into a public method
                        fixed a few more instances of "g" and "m" as team names
                        should be '1' and '2' everywhere BUT controlled entirely
                            by the list settings.teams
                            (I think the only place it still shows up is in the
                                ASCII decoder ditionary)
v0.9.4  02/19/2023  made MText class; overhauled Rules screen to use it
                        deleted rules text images
v0.9.3  02/19/2023  found one more bug in the team naming system
v0.9.2  02/19/2023  made a subfolder in images for tilesets for different looks
                    changed all team name references to refer to settings.teams
                        there should be no more traces of the old 'g' and 'm'
v0.9.1  02/18/2023  needed to call a screen update when showing inactive los
v0.9.0  02/18/2023  implemented victory conditions
v0.8.2  02/18/2023  made one Laser class for shot lasers and the background
v0.8.1  02/18/2023  moved the line that deselects AP-0 from _end_overwatch() to
                        _hide_result()
v0.8.0  02/18/2023  fixed most of the bugs in the overwatch system
                        needs testing but I think it's working properly
                    put the call to _run_overwatch() in the main _run_game
v0.7.0  02/18/2023  finished roll_result window and linked it up with overwatch
                        mode. Still need to tweak the way overwatch displays
                        roll info in the status boxes.
v0.6.10 02/18/2023  cleaned up unit and target selection functions
                    put roll message into a separate frame 
                    changes to check_events: if roll result or rules screen are
                        active, the next mouseclick will ONLY clear that window
                    temporarily deactivated overwatch mode
v0.6.9x 02/17/2023  lots of refactoring in the main module; still need to clean
                        up the fire and overwatch funcs and selection
v0.6.9  02/17/2023  removed walking-range animation - was distracting,
                        and it needed access to a protected method
                    changed all 4 tactical hit modifiers from +/- 2 to 1
                    changed base to-hit from 7 to 6
                    changed base move speed from 5 to 3
v0.6.8  02/17/2023  made module _roll_checker.py to create hit tables
                        based on different modifiers & dice
v0.6.7  02/16/2023  moved all unit roll modifiers into settings
                    moved the overwatch message over onto the map;
            ########    NEED TO USE THAT BOX TO DISPLAY HIT INFO FOR
            ########    REGULAR SHOTS TOO
                    began building a roll tester module
v0.6.6  02/16/2023  moved the map launcher to a separate module; running
                    laser_flag.py as "__main__" will load the test map
v0.6.5  02/16/2023  worked out a few bugs with showing cover in status boxes
v0.6.4  02/16/2023  cleaned up status displays to properly display shooter vs 
                    target in the proper active/inactive boxes,in both phases
v0.6.3  02/15/2023  finished all listed below
                    some map edits to reflect the new base system
v0.6.2  02/15/2023  brought back team bases concept. Still need to reinstate
                        Elimination mode, update Rules screen, and make team
                        base sprites. Refer to teams G and M as 1 and 2 ingame.
v0.6.1  02/15/2023  cleaned up map loader a bit
v0.6.0  02/15/2023  ALPHA?
                    made a simple map loader so friends can easily test them
                    changed map loader dictionary so "B" makes a base
v0.5.8  02/15/2023  eliminated concept of "team bases" entirely
                    completed rules screen
v0.5.7  02/15/2023  implemented most of rules screen; eliminating team bases
                        before proceeding
v0.5.6  02/15/2023  made the game pause after each shot so you can read the roll
                        info; any click or keypress will continue
                            (need to add a message for the user)
v0.5.5  02/15/2023  made it so only relevant cover is included in target status
                        still need to clean it up so it displays a nice string though
v0.5.4  02/14/2023  started adding a rules screen
                    added cover info to status boxes
                    gave buttons/labels the ability to show 3 lines
v0.5.3  02/14/2023  revised overwatch rules; reaction shots are triggered by
                        firing as well as moving
                    more image revisions; probably good enough for alpha
v0.5.2  02/14/2023  changed rule for scouts: eliminated free move after shot but
                        they can now climb onto elevated ground without
                        consuming the remainder of the AP
                    implemented alt team colors
                    new unit icons
                    cleaned up a few more images
v0.5.1  02/14/2023  had some bugs in the overwatch system so moved all unit
                        firing action into one base method, to be overridden by
                        sniper and scout classes. Seems to work smoothly.
                    revised unit icons and added alt color polygons to class defs
v0.5.0  02/13/2023  basic overwatch rules implemented
v0.4.6  02/13/2023  moved lf_game.tiles to game_map.all_tiles
                    moved lf_game.walls to game_map.all_walls
                    added function to eliminate units if they have no bases
                        - for assault (one team has a recharging base) or
                          elimination (no recharging bases on the map) rules
v0.4.5  02/13/2023  cleaned up conditionals so that units with no laser can't
                        click targets
                    simplified Grunt rules: "everything +/-3 instead of 2"
v0.4.4  02/13/2023  invented Grunt overwatch rules (3 shots but +3 penalty)
v0.4.3  02/13/2023  added some additional methods to the Unit superclass so
                        that each subclass has a place to implement bonuses
                    changed status indicator rules:
                        - black dots indicate remaining AP
                        - cyan / red to indicate whether unit can move
                        - laser recharge symbol if unit cannot fire
                    added option to view enemy sight lines
v0.4.2  02/12/2023  linked all color settings including unit circle
                    tweaked hit/miss report message and timer
                    fixed so target symbol disappears immediately after firing
v0.4.1  02/12/2023  added all roll calculations to status labels - still need
                    to actually implement them in the roll however
v0.4.0  02/12/2023  refactored unit and target selection methods
                    implemented roll calculation method and dictionary
                    cover & elevation systems seem to work
                    still need to report to labels
v0.3.6  02/12/2023  moved determine_range() and determine_los() calls from
                        main game loop into to the unit_move() method and stored
                        those values with unit class variables
v0.3.5  02/12/2023  moved build_teams to the game_map module
                    changed team-related buttons to dictionary entries
                    started refactoring _on_select_unit and _on_target_unit
                    moved Tile class to its own module
v0.3.4  02/11/2023  fixed the background lasers
v0.3.3  02/11/2023  organized the haphazard tile.point system
                    but something broke the background lasers
v0.3.2  02/11/2023  implemented scoring
v0.3.1  02/11/2023  put in some code to read version info from this file
v0.3.0  02/11/2023  implemented laser hits (on units) and recharging
v0.2.1  02/10/2023  moved the "move unit" method to the unit class
                    added a little D6 function
                    moved selection and deselection into their own methods
v0.2.0  02/10/2023  implemented flags in the LOS functions to decide corner
                            permissiveness
                    converted ASCII reader to a dictionary in settings
                    changed self.teams from a list to a dictionary
v0.1.1  02/10/2023  line-of-sight seems to be working properly
v0.1.0  02/10/2023  implemented basic line-of-sight; still buggy
v0.0.2  02/09/2023  a bit more refactoring; fixed a bug with climbing units
v0.0.1  02/08/2023  refactored a bunch of shit
v0.0.0  02/08/2023  map-loading and movement rules complete

################################################################################
RUNNING THE GAME
################################################################################

Laser Flag is written in Python 3.10.2; the only non-standard module you might
need to install is Pygame. I used version 2.1.2

Run _map_launcher.py to select from the levels in the "maps" folder. Running 
laser_flag.py directly will load the "testing ground" map. Or, try making your
own maps with _map_editor.py

################################################################################
LASER FLAG RULES:
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
of string to determine lines-of-sight.

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