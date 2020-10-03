import pathlib
from pathlib import Path
import sys

import pygame

MAIN_PRG_DIR = pathlib.Path(__file__).absolute().parent
SCRN_WIDTH = 512
SCRN_HEIGHT = 434
SCRN_SIZE = SCRN_WIDTH, SCRN_HEIGHT
BLACK = 0, 0, 0
WHITE = 255, 255, 255
KEY_REPEAT_DELAY = 125
KEY_REPEAT_INTERVAL = 125


class AssetPathGetter():
    def __init__(self, asset_dir_path, font_dir_name, img_dir_name):
        self.asset_dir = Path(asset_dir_path)
        self.font_dir_name = font_dir_name
        self.img_dir_name = img_dir_name

    def font_path(self, filename) -> pathlib.Path:
        return self.asset_dir / self.font_dir_name / filename

    def img_path(self, filename) -> pathlib.Path:
        return self.asset_dir / self.img_dir_name / filename


class SpriteSheet:
    def __init__(self, filename) -> None:
        self.sheet = pygame.image.load(filename).convert_alpha()

    def get_image(self, x, y, width, height) -> pygame.Surface:
        image = pygame.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        return image


class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.spritesheet = SpriteSheet()
        # self.image =

    def update(self, *args, **kwargs) -> None:
        pass


def text_pos_to_center(screen_size, text_size,
                       multiply_to_fix_pos_x=1, multiply_to_fix_pos_y=1, ):
    """find coordinate to center text
    screen_size: (width, height)
    text_size: (width, height)
    """
    return ((screen_size[0]*0.5-text_size[0]*0.5)*multiply_to_fix_pos_x,
            (screen_size[1]*0.5-text_size[1]*0.5)*multiply_to_fix_pos_y)


def main():
    pygame.init()
    pygame.key.set_repeat(KEY_REPEAT_DELAY, KEY_REPEAT_INTERVAL)
    screen = pygame.display.set_mode(SCRN_SIZE)
    pygame.display.set_caption("Boxrush")
    asset_path = AssetPathGetter(MAIN_PRG_DIR / "assets", "fonts", "imgs")
    font = pygame.font.Font(
        str(asset_path.font_path("misaki_gothic_2nd.ttf")), 48)
    title_text = font.render("Boxrush", True, WHITE)
    font = pygame.font.Font(
        str(asset_path.font_path("misaki_gothic_2nd.ttf")), 32)
    title_pos = (
        text_pos_to_center(
            screen.get_size(), title_text.get_size(), 1, 0.25))
    menu_items = ["game", "config", "exit"]
    menu_item_num = len(menu_items)
    menu_select_num = 0
    game_scene = 0
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_UP or
                        event.key == pygame.K_LEFT):
                    menu_select_num -= 1
                    if menu_select_num < 0:
                        menu_select_num = menu_item_num-1
                elif (event.key == pygame.K_DOWN or
                        event.key == pygame.K_RIGHT):
                    menu_select_num += 1
                    if menu_select_num > menu_item_num-1:
                        menu_select_num = 0
                elif (event.key == pygame.K_z):
                    if menu_select_num == 2:
                        sys.exit()
        screen.fill(BLACK)
        # --draw here--
        screen.blit(title_text, title_pos)
        for index in range(menu_item_num):
            start_text = font.render(menu_items[index], True, WHITE)
            screen.blit(
                start_text, (title_pos[0], title_pos[1] * (index+3)))
            menu_cursor = font.render(">", True, WHITE)
            screen.blit(
                menu_cursor,
                (title_pos[0] * 0.75, title_pos[1] * (menu_select_num+3)))
        # ----
        pygame.display.update()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
