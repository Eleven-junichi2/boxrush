import sys
import pygame


def main():
    pygame.init()
    SCRN_WIDTH = 512
    SCRN_HEIGHT = 434
    SCRN_SIZE = SCRN_WIDTH, SCRN_HEIGHT
    BLACK = 0, 0, 0
    screen = pygame.display.set_mode(SCRN_SIZE)
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        screen.fill(BLACK)
        # --draw here--

        # ----
        pygame.display.update()


if __name__ == "__main__":
    main()
