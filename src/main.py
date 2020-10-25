import pathlib
from pathlib import Path
import sys

import pygame

GAME_TITLE = "YUMA"
MAIN_PRG_DIR = pathlib.Path(__file__).absolute().parent
SCRN_WIDTH = 512
SCRN_HEIGHT = 434
SCRN_SIZE = SCRN_WIDTH, SCRN_HEIGHT
BLACK = 0, 0, 0
WHITE = 255, 255, 255
KEY_REPEAT_DELAY = 125
KEY_REPEAT_INTERVAL = 125


class SceneManager:
    def __init__(self, screen: pygame.Surface, asset_path):
        self.screen = screen
        self.asset_path = asset_path
        self.scene_list = {}
        self.current_scene = None

    def append_scene(self, scene_name, scene):
        self.scene_list[scene_name] = scene

    def set_current_scene(self, scene_name):
        self.current_scene = self.scene_list[scene_name]


class Scene:
    def __init__(self, scene_manager: SceneManager):
        self.sm = scene_manager

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def render(self):
        self.sm.screen.fill(BLACK)
        pygame.display.update()


class TitleScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menu_items = ["game", "config", "exit"]
        self.menu_item_num = len(self.menu_items)
        self.menu_select_num = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_UP or
                    event.key == pygame.K_LEFT):
                self.menu_select_num -= 1
                if self.menu_select_num < 0:
                    self.menu_select_num = self.menu_item_num-1
            elif (event.key == pygame.K_DOWN or
                    event.key == pygame.K_RIGHT):
                self.menu_select_num += 1
                if self.menu_select_num > self.menu_item_num-1:
                    self.menu_select_num = 0
            elif (event.key == pygame.K_z):
                if self.menu_select_num == 0:
                    self.sm.set_current_scene("game")
                if self.menu_select_num == 2:
                    sys.exit()

    def update(self):
        pass

    def render(self):
        self.sm.screen.fill(BLACK)
        font = pygame.font.Font(
            str(self.sm.asset_path.font_path("misaki_gothic_2nd.ttf")), 48)
        title_text = font.render(GAME_TITLE, True, WHITE)
        font = pygame.font.Font(
            str(self.sm.asset_path.font_path("misaki_gothic_2nd.ttf")), 32)
        title_pos = (
            text_pos_to_center(
                self.sm.screen.get_size(), title_text.get_size(), 1, 0.25))
        self.sm.screen.blit(title_text, title_pos)
        for index in range(self.menu_item_num):
            start_text = font.render(self.menu_items[index], True, WHITE)
            self.sm.screen.blit(
                start_text, (title_pos[0], title_pos[1] * (index+3)))
            menu_cursor = font.render(">", True, WHITE)
            self.sm.screen.blit(
                menu_cursor,
                (title_pos[0] * 0.75, title_pos[1] * (self.menu_select_num+3)))
        pygame.display.update()


class GameScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prepared_terrain_map = False
        self.terrain = Terrain()
        MAP_HEIGHT = 16
        MAP_WIDTH = 16
        self.terrain.reset_map(3, MAP_HEIGHT, MAP_WIDTH)
        self.terrain.fill_map(2, 3, 1, 4, 6, "Glass")

    def render(self):
        self.sm.screen.fill(BLACK)
        self.render_terrain(self.terrain.map)
        pygame.display.update()

    def render_terrain(self, terrain_map):
        sprite = SpriteSheet(self.sm.asset_path.img_path("skyeyebg.png"))
        for z in range(len(terrain_map)):
            for y in range(len(terrain_map[0])):
                for x in range(len(terrain_map[0][0])):
                    if terrain_map[z][y][x] == 1:
                        self.sm.screen.blit(
                            sprite.get_image(0, 0, 16, 16), (16*x, 16*y))
                    elif terrain_map[z][y][x] == 2:
                        self.sm.screen.blit(
                            sprite.get_image(16, 0, 16, 16), (16*x, 16*y))


class AssetPathGetter:
    def __init__(self, asset_dir_path, font_dir_name, img_dir_name):
        self.asset_dir = Path(asset_dir_path)
        self.font_dir_name = font_dir_name
        self.img_dir_name = img_dir_name

    def font_path(self, filename) -> pathlib.Path:
        return self.asset_dir / self.font_dir_name / filename

    def img_path(self, filename) -> pathlib.Path:
        return self.asset_dir / self.img_dir_name / filename


class SpriteSheet:
    def __init__(self, filename):
        self.sheet = pygame.image.load(str(filename)).convert_alpha()

    def get_image(self, x, y, width, height) -> pygame.Surface:
        image = pygame.Surface((width, height))
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        return image


class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.spritesheet = SpriteSheet()
        # self.image =

    def update(self, *args, **kwargs) -> None:
        pass


class Tile:
    def __init__(self):
        self.layer = 0
        self.barrier = False
        self.name = ""


class WaterTile(Tile):
    def __init__(self):
        super().__init__()
        self.name = "Water"
        self.layer = 0


class DirtTile(Tile):
    def __init__(self):
        super().__init__()
        self.name = "Dirt"
        self.layer = 1


class GlassTile(Tile):
    def __init__(self):
        super().__init__()
        self.name = "Dirt"
        self.layer = 2


def get_swap_dict(dictionary):
    return {value: key for key, value in dictionary.items()}


class Terrain:
    def __init__(self):
        self.tile_img_assign = {"Glass": "", "Dirt": "", "Water": ""}
        self.tile_id_assign = {None: 0, "Glass": 1, "Dirt": 2, "Water": 3}
        self.tile_type_from_id = get_swap_dict(self.tile_id_assign)
        self.map = [[[]]]

    def reset_map(self, layer_num, height, width, init_tile=None):
        self.map = [[[self.tile_id_assign[init_tile] for x in range(
            width)] for y in range(height)] for z in range(layer_num)]

    def rewrite_map_tile(self, layer_id, x, y, tile):
        self.map[layer_id][y][x] = self.tile_id_assign[tile]

    def fill_map(self, layer_id, start_x, width, start_y, height, tile):
        for y in range(start_y, start_y + height):
            self.map[
                layer_id][
                    y][
                start_x: start_x + width] = [
                    self.tile_id_assign[tile] for x in range(width)]


class Game:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(KEY_REPEAT_DELAY, KEY_REPEAT_INTERVAL)
        pygame.display.set_caption(GAME_TITLE)
        self.screen = pygame.display.set_mode(SCRN_SIZE)
        self.asset_path = AssetPathGetter(
            MAIN_PRG_DIR / "assets", "fonts", "imgs")
        self.sm = SceneManager(self.screen, self.asset_path)
        self.sm.append_scene("title", TitleScene(self.sm))
        self.sm.append_scene("game", GameScene(self.sm))
        self.sm.set_current_scene("title")

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                self.sm.current_scene.handle_event(event)
                self.sm.current_scene.update()
                self.sm.current_scene.render()


def text_pos_to_center(screen_size, text_size,
                       multiply_to_fix_pos_x=1, multiply_to_fix_pos_y=1, ):
    """find coordinate to center text
    screen_size: (width, height)
    text_size: (width, height)
    """
    return ((screen_size[0]*0.5-text_size[0]*0.5)*multiply_to_fix_pos_x,
            (screen_size[1]*0.5-text_size[1]*0.5)*multiply_to_fix_pos_y)


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    try:
        # this game program start from here
        main()
    except SystemExit:
        pass
