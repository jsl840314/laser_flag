import sys

import pygame
from settings import Settings
from game_map import GameMap

from lf_functions import game_caption


class MapEditor:
    """overall class to manage the map editor program"""

    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode(
                (self.settings.screen_width, self.settings.screen_height))
        res = f"{self.settings.screen_width}x{self.settings.screen_height}"
        pygame.display.set_caption(f"Map Editor for {game_caption()}")

        self.game_map = GameMap(self, 'maps/_testing ground.txt')

        self._update_screen()


################################################################################
#   MAIN PROGRAM LOOP
################################################################################

    def run(self):
        while True:
            self._check_events()

    def _check_events(self):
        """respond to keypresses & mouse events"""
        for event in pygame.event.get():
            # if click on window X
            if event.type == pygame.QUIT:
                self._quit()
            # respond to other mouse clicks
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._mouse_down_events(mouse_pos)
                self._update_screen()



    def _mouse_down_events(self, mouse_pos):
        """respond to mouse clicks"""
        for tile in self.game_map.all_tiles:
            tile_clicked = tile.rect.collidepoint(mouse_pos)
            if tile_clicked:
                tile.change_type('elevated')





    def _quit(self):
        pygame.quit()
        sys.exit()

################################################################################
# UPDATE SCREEN
################################################################################

    def _update_screen(self):
        """update images and flip to the new screen"""

        self.game_map.draw_map()

        pygame.display.flip()

################################################################################
#   
################################################################################

if __name__ == "__main__":
    mapeditor = MapEditor()
    mapeditor.run()
