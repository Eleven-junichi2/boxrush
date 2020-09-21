import pathlib
import sys
from typing import Tuple

import pygame

MAIN_PRG_DIR = pathlib.Path(__file__).absolute().parent
ASSET_DIR = MAIN_PRG_DIR / "assets"
FONT_DIR = ASSET_DIR / "fonts"
SCRN_WIDTH = 512
SCRN_HEIGHT = 434
SCRN_SIZE = SCRN_WIDTH, SCRN_HEIGHT
BLACK = 0, 0, 0
WHITE = 255, 255, 255


def text_pos_to_center(screen_size: Tuple, text_size: Tuple,
                       multiply_to_fix_pos_x=1, multiply_to_fix_pos_y=1, ):
    """find coordinate to center text
    screen_size: (width, height)
    text_size: (width, height)
    """
    return ((screen_size[0]*0.5-text_size[0]*0.5)*multiply_to_fix_pos_x,
            (screen_size[1]*0.5-text_size[1]*0.5)*multiply_to_fix_pos_y)


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCRN_SIZE)
    pygame.display.set_caption("Boxrush")
    font = pygame.font.Font(str(FONT_DIR / "misaki_gothic_2nd.ttf"), 32)
    title_text = font.render("Boxrush", True, WHITE)
    title_pos = (
        text_pos_to_center(
            screen.get_size(), title_text.get_size(), 1, 0.25))
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        screen.fill(BLACK)
        # --draw here--
        screen.blit(title_text, title_pos)
        # ----
        pygame.display.update()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
