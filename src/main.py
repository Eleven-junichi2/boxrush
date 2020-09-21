# import pathlib
import sys
from typing import Tuple

import pygame

SCRN_WIDTH = 512
SCRN_HEIGHT = 434
SCRN_SIZE = SCRN_WIDTH, SCRN_HEIGHT
BLACK = 0, 0, 0
WHITE = 255, 255, 255


def text_coordinate_to_center(screen_size: Tuple, text_size: Tuple) -> Tuple:
    """find coordinate to center text
    screen_size: (width, height)
    text_size: (width, height)
    """
    coodinate = (screen_size[0]*0.5-text_size[0]*0.5,
                 screen_size[1]*0.5-text_size[1]*0.5)
    return coodinate


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCRN_SIZE)
    pygame.display.set_caption("Boxrush")
    font = pygame.font.Font("./assets/fonts/misaki_gothic_2nd.ttf", 32)
    title_text = font.render("美咲フォントおすすめ", True, WHITE)
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        screen.fill(BLACK)
        # --draw here--
        screen.blit(title_text, text_coordinate_to_center(
            screen.get_size(), title_text.get_size()))
        # ----
        pygame.display.update()


if __name__ == "__main__":
    main()
