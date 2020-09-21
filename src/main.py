import sys
import pygame


def main():
    pygame.init()
    size = width, height = 512, 434
    black = 0, 0, 0
    screen = pygame.display.set_mode(size)
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        screen.fill(black)
        # --draw here--

        # ----
        pygame.display.update()


if __name__ == "__main__":
    main()
