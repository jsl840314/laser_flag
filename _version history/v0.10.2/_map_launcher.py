
import os
from laser_flag import LaserFlag
from lf_functions import game_caption

map_list = os.listdir('maps')
while True:
    os.system('cls')
    print("*"*60)
    print(game_caption())
    print("*"*60)
    print()
    print("Choose a map or (Q) to quit:\n")

    i = 0
    for map_file in map_list:
        print(f'{i}) ', map_file)
        i += 1

    print()
    user_input = input()
    if user_input.upper() == 'Q':
        break

    try:
        os.system('cls')
        print('close this console window to end the game')
        user_input = int(user_input)
        filename = f'maps/{map_list[user_input]}'
        lf = LaserFlag(filename)
        lf.run_game()

    except:
        continue