import pathlib
from pathlib import Path
import sys
from typing import Tuple

import pygame

GAME_TITLE = "YUMA"
MAIN_PRG_DIR = pathlib.Path(__file__).absolute().parent
SCRN_WIDTH = 768  # 512*1.5
SCRN_HEIGHT = 651  # 434*1.5
SCRN_SIZE = SCRN_WIDTH, SCRN_HEIGHT
BLACK = 0, 0, 0
WHITE = 255, 255, 255
KEY_REPEAT_DELAY = 125
KEY_REPEAT_INTERVAL = 125


class AssetPathGetter:
    def __init__(self, root_dir_path, font_dir_name, img_dir_name,
                 saves_dir_name):
        self.asset_dir = Path(root_dir_path)
        self.font_dir_name = font_dir_name
        self.img_dir_name = img_dir_name
        self.saves_dir_name = saves_dir_name

    def font_path(self, filename) -> pathlib.Path:
        return self.asset_dir / self.font_dir_name / filename

    def img_path(self, filename) -> pathlib.Path:
        return self.asset_dir / self.img_dir_name / filename

    def saved_assets_path(self, filename):
        return self.asset_dir / self.saves_dir_name / filename


assets_path = AssetPathGetter(
    MAIN_PRG_DIR / "assets", "fonts", "imgs", "saves")


class SceneManager:
    def __init__(self, screen: pygame.Surface, game):
        self.screen = screen
        self.game = game
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
        pass


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
                    self.sm.set_current_scene("world_select")
                if self.menu_select_num == 2:
                    sys.exit()

    def update(self):
        pass

    def render(self):
        self.sm.screen.fill(BLACK)
        font = pygame.font.Font(
            str(assets_path.font_path("misaki_gothic_2nd.ttf")), 48)
        title_text = font.render(GAME_TITLE, True, WHITE)
        font = pygame.font.Font(
            str(assets_path.font_path("misaki_gothic_2nd.ttf")), 32)
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


class GameScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.terrain = Terrain()
        # self.TILE_SIZE = 16
        self.MAP_HEIGHT = 64
        self.MAP_WIDTH = 64
        self.MAP_VIEWER_X = 16
        self.MAP_VIEWER_Y = 16
        self.MAP_VIEWER_HEIGHT = 480
        self.MAP_VIEWER_WIDTH = 608
        self.scroll_x = 0
        self.scroll_y = 0
        self.scroll_vx = 0
        self.scroll_vy = 0
        self.terrain.reset_map(4, self.MAP_HEIGHT, self.MAP_WIDTH)
        self.terrain.fill_map(2, 0, 64, 0, 64, "Glass")
        self.map_surface = pygame.Surface(
            (self.MAP_WIDTH*16, self.MAP_HEIGHT*16)).convert_alpha()
        self.minimap_surface = pygame.Surface(
            (self.MAP_WIDTH, self.MAP_HEIGHT))
        self.water_btn = ButtonSprite("Water", 16, SCRN_HEIGHT - 139 + 16)
        btn_size = self.water_btn.rect.size
        self.dirt_btn = ButtonSprite(
            "Dirt", 16 + btn_size[0] + 16, SCRN_HEIGHT - 139 + 16)
        self.mount_btn = ButtonSprite(
            "Mount", 16 + btn_size[0]*2 + 16*2, SCRN_HEIGHT - 139 + 16)
        self.tree_btn = ButtonSprite(
            "Tree", 16 + btn_size[0]*3 + 16*3, SCRN_HEIGHT - 139 + 16)
        self.human_btn = ButtonSprite(
            "Human", 16 + btn_size[0]*4 + 16*4, SCRN_HEIGHT - 139 + 16)
        self.save_btn = ButtonSprite(
            "Save", 16, SCRN_HEIGHT - 139 + 16 + btn_size[1] + 16)
        self.load_btn = ButtonSprite(
            "Load", 16 + btn_size[0] + 16,
            SCRN_HEIGHT - 139 + 16 + btn_size[1] + 16)
        self.btn_group = pygame.sprite.RenderUpdates()
        self.btn_group.add(self.water_btn, self.dirt_btn,
                           self.mount_btn, self.tree_btn,
                           self.human_btn,
                           self.save_btn, self.load_btn)
        self.mob_group = pygame.sprite.Group()
        self.mouse_pos_history = []

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if pygame.key.get_pressed()[pygame.K_UP]:
                self.scroll_vy = -9
            if pygame.key.get_pressed()[pygame.K_DOWN]:
                self.scroll_vy = 9
            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                self.scroll_vx = 9
            if pygame.key.get_pressed()[pygame.K_LEFT]:
                self.scroll_vx = -9
        if pygame.mouse.get_pressed()[0]:
            print(pygame.mouse.get_pressed())
            is_btn_pressing = False
            for btn_sprite in iter(self.btn_group):
                if btn_sprite.is_pressed:
                    is_btn_pressing = True
                    break
            print(is_btn_pressing)
            if not is_btn_pressing and self.is_pos_on_map(
                    pygame.mouse.get_pos()):
                # move map viewer with mouse dragging
                mouse_pos = pygame.mouse.get_pos()
                self.mouse_pos_history.append(mouse_pos)
                if 2 < len(self.mouse_pos_history):
                    self.scroll_vx = - \
                        (self.mouse_pos_history[1][0] -
                         self.mouse_pos_history[0][0])
                    self.scroll_vy = - \
                        (self.mouse_pos_history[1][1] -
                         self.mouse_pos_history[0][1])
                    self.mouse_pos_history.pop(0)
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.mouse_pos_history.clear()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn_sprite in iter(self.btn_group):
                if btn_sprite.rect.collidepoint(event.pos):
                    btn_sprite.is_pressed = not btn_sprite.is_pressed
                    for other_btn in iter(self.btn_group):
                        if other_btn.id != btn_sprite.id:
                            other_btn.is_pressed = False
                if self.is_pos_on_map(event.pos):
                    if btn_sprite.is_pressed:
                        if btn_sprite.id == "Water":
                            self.rewrite_tile_with_mouse(
                                2, None, event.pos)
                            self.rewrite_tile_with_mouse(
                                0, "Water", event.pos)
                        if btn_sprite.id == "Dirt":
                            self.rewrite_tile_with_mouse(
                                2, "Dirt", event.pos)
                        if btn_sprite.id == "Mount":
                            self.rewrite_tile_with_mouse(
                                3, "Mount", event.pos)
                        if btn_sprite.id == "Tree":
                            self.rewrite_tile_with_mouse(
                                3, "Tree", event.pos)
                        if btn_sprite.id == "Human":
                            self.spawn_human_with_mouse(event.pos)
                            print("spawned")
        # scroll map
        self.scroll_x += self.scroll_vx
        self.scroll_y += self.scroll_vy
        self.scroll_vx = 0
        self.scroll_vy = 0

    def is_pos_on_map(self, pos):
        return (self.MAP_VIEWER_X <= pos[0] <=
                (self.MAP_VIEWER_WIDTH + 16) and
                self.MAP_VIEWER_Y <= pos[1] <=
                (self.MAP_VIEWER_HEIGHT + 16))

    def spawn_human_with_mouse(self, mouse_pos):
        spawn_x = (self.scroll_x+mouse_pos[0]-self.MAP_VIEWER_X)
        spawn_y = (self.scroll_y+mouse_pos[1]-self.MAP_VIEWER_Y)
        human_sprite = HumanSprite(x=spawn_x, y=spawn_y)
        self.mob_group.add(human_sprite)

    def rewrite_tile_with_mouse(self, layer_id, tile_type, mouse_pos):
        tile_x = (self.scroll_x+mouse_pos[0]-self.MAP_VIEWER_X)//16
        tile_y = (self.scroll_y+mouse_pos[1]-self.MAP_VIEWER_Y)//16
        self.terrain.rewrite_map_tile(layer_id, tile_x, tile_y, tile_type)

    def render(self):
        self.sm.screen.fill(BLACK)
        self.render_terrain(self.terrain.map)
        self.render_minimap(self.terrain.map)
        self.sm.screen.blit(self.minimap_surface,
                            (16 + self.MAP_VIEWER_WIDTH + 8, 16),
                            (0, 0, self.MAP_WIDTH, self.MAP_HEIGHT))
        self.sm.screen.fill(
            (144, 78, 144), (0, SCRN_HEIGHT - 139, 768, 139))
        self.water_btn.set_image_with_icon(1, 2)
        self.dirt_btn.set_image_with_icon(1, 1)
        self.mount_btn.set_image_with_icon(1, 3)
        self.human_btn.set_image_with_icon(1, 4)
        self.tree_btn.set_image_with_icon(2, 1)
        self.save_btn.set_image_with_icon(2, 2)
        self.load_btn.set_image_with_icon(2, 3)
        self.btn_group.draw(self.sm.screen)
        self.mob_group.draw(self.map_surface)
        self.sm.screen.blit(self.map_surface,
                            (self.MAP_VIEWER_X, self.MAP_VIEWER_Y),
                            (0+self.scroll_x,
                             0+self.scroll_y,
                             self.MAP_VIEWER_WIDTH,
                             self.MAP_VIEWER_HEIGHT))

    def render_terrain(self, terrain_map):
        sprite = SpriteSheet(assets_path.img_path(
            "skyeyebg.png"), 1, 1, 16, 16, BLACK)
        for z in range(len(terrain_map)):
            for y in range(len(terrain_map[0])):
                for x in range(len(terrain_map[0][0])):
                    if terrain_map[z][y][x] == 1:
                        self.map_surface.blit(
                            sprite.image_by_cell(1, 1), (16*x, 16*y))
                    elif terrain_map[z][y][x] == 2:
                        self.map_surface.blit(
                            sprite.image_by_cell(1, 2), (16*x, 16*y))
                    elif terrain_map[z][y][x] == 3:
                        self.map_surface.blit(
                            sprite.image_by_cell(3, 1), (16*x, 16*y))
                    elif terrain_map[z][y][x] == 4:
                        self.map_surface.blit(
                            sprite.image_by_cell(2, 7), (16*x, 16*y))
                    elif terrain_map[z][y][x] == 5:
                        self.map_surface.blit(
                            sprite.image_by_cell(1, 5), (16*x, 16*y))

    def render_minimap(self, terrain_map):
        for z in range(len(terrain_map)):
            for y in range(len(terrain_map[0])):
                for x in range(len(terrain_map[0][0])):
                    minimap_tile_color = (0, 0, 0)
                    if terrain_map[0][y][x] != 0:
                        minimap_tile_color = (123, 0, 0)
                        self.minimap_surface.fill((66, 66, 0), (x, y, 1, 1))
                    if terrain_map[1][y][x] != 0:
                        minimap_tile_color = (123, 123, 0)
                        self.minimap_surface.fill((123, 123, 0), (x, y, 1, 1))
                    if terrain_map[2][y][x] != 0:
                        minimap_tile_color = (255, 255, 0)
                    if terrain_map[3][y][x] != 0:
                        minimap_tile_color = (78, 255, 125)
                    self.minimap_surface.fill(minimap_tile_color, (x, y, 1, 1))


class WorldSelectScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wm = self.sm.game.world_manager
        self.menu_items = ["P", ]
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
                    self.sm.set_current_scene("title")

    def update(self):
        pass

    def render(self):
        self.sm.screen.fill(BLACK)
        font = pygame.font.Font(
            str(assets_path.font_path("misaki_gothic_2nd.ttf")), 24)
        world_preview_frame_img = pygame.image.load(
            str(assets_path.img_path("world_picture_frame.png"))
        ).convert_alpha()
        MENU_ITEM_WIDTH = 496
        MENU_ITEM_HEIGHT = 64
        MENU_ITEM_X_POS = SCRN_WIDTH * 0.5 - MENU_ITEM_WIDTH * 0.5
        self.sm.screen.fill(
            (122, 122, 122),
            (SCRN_WIDTH * 0.5 - MENU_ITEM_WIDTH * 0.5, 48,
             MENU_ITEM_WIDTH, MENU_ITEM_HEIGHT))
        self.sm.screen.blit(world_preview_frame_img, (0, 0))
        text = font.render("Create new world", True, WHITE)
        self.sm.screen.blit(
            text,
            (MENU_ITEM_X_POS + MENU_ITEM_WIDTH * 0.5
             - text.get_size()[0] * 0.5,
             48 + MENU_ITEM_HEIGHT * 0.5
             - text.get_size()[1] * 0.5))


class WorldDataManager:
    def __init__(self, saves_dir_path):
        self.saves_dir = Path(saves_dir_path)

    def list_worlds(self):
        return self.saves_dir.iterdir()

    def save_world(self):
        pass


class SpriteSheet:
    def __init__(self, filename, row_num: int, column_num: int,
                 cell_width: int, cell_height: int, colorkey: Tuple):
        self.sheet = pygame.image.load(str(filename)).convert_alpha()
        self.colorkey = colorkey
        # self.sheet.set_colorkey(self.colorkey)
        self.row_num = row_num
        self.column_num = column_num
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.current_row = 0
        self.current_column = 0
        self.cell_anims = {"animation_name": ((0, 0), (0, 0))}

    def set_current_cell(self, row, column):
        self.current_row = row
        self.current_column = column

    def define_new_cell_anim(self, new_animation_name):
        self.cell_anims[new_animation_name] = []

    def append_cell_anim(self, animation_name, row, colmun):
        self.cell_anims[animation_name].append([row, colmun])

    def animation_cell(self, animation_name, start, end):
        yield self.cell_anims[animation_name][start:end]

    def image_by_area(self, x, y, width, height) -> pygame.Surface:
        image = pygame.Surface((width, height))
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(self.colorkey)
        return image

    def image_by_cell(self, row, column) -> pygame.Surface:
        image = pygame.Surface(
            (self.cell_width, self.cell_height))
        image.blit(self.sheet, (0, 0),
                   (self.cell_width * (column - 1),
                    self.cell_height * (row - 1),
                    self.cell_width, self.cell_height))
        image.set_colorkey(self.colorkey)
        return image

    def image_by_current(self) -> pygame.Surface:
        return self.image_by_cell(self.current_row, self.current_column)


class HumanSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, 6, 8)
        self.sheet = SpriteSheet(assets_path.img_path(
            "human.png"), 4, 4, 6, 8, BLACK)
        self.image = self.sheet.image_by_cell(1, 1)

    def update(self, *args, **kwargs):
        pass


class ButtonSprite(pygame.sprite.Sprite):
    def __init__(self, id, x, y, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id
        self.rect = pygame.Rect(x, y, 48, 48)
        # This value is for moving y of the icon when button pressing.
        self.y_pressing = 2
        # self.rect = pygame.Rect(x, y, self.width, self.height)
        self.btn_sheet = SpriteSheet(assets_path.img_path(
            "button.png"), 1, 2, self.rect.width, self.rect.height, BLACK)
        self.icon_sheet = SpriteSheet(assets_path.img_path(
            "btn_icon.png"), 1, 3, self.rect.width, self.rect.height, BLACK)
        self.is_pressed = False

    def update(self, *args, **kwargs):
        pass

    def set_image_with_icon(self, icon_sheet_row,
                            icon_sheet_column) -> pygame.Surface:
        if self.is_pressed:
            btn_row = 1
            btn_column = 2
            icon_y = self.y_pressing
        else:
            btn_row = 1
            btn_column = 1
            icon_y = 0
        btn_surface = pygame.Surface(
            (self.rect.width, self.rect.height))
        btn_surface.set_colorkey(self.btn_sheet.colorkey)
        btn_surface.blit(self.btn_sheet.image_by_cell(
            btn_row, btn_column), (0, 0))
        btn_surface.blit(self.icon_sheet.image_by_cell(
            icon_sheet_row, icon_sheet_column), (0, icon_y))
        self.image = btn_surface


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
        self.tile_id_assign = {None: 0, "Glass": 1,
                               "Dirt": 2, "Water": 3, "Tree": 4, "Mount": 5}
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
        self.world_manager = WorldDataManager(MAIN_PRG_DIR / "saves")
        # sm means "screen manager"
        self.sm = SceneManager(self.screen, self)
        self.sm.append_scene("title", TitleScene(self.sm))
        self.sm.append_scene("game", GameScene(self.sm))
        self.sm.append_scene("world_select", WorldSelectScene(self.sm))
        self.sm.set_current_scene("title")

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                self.sm.current_scene.handle_event(event)
            self.sm.current_scene.update()
            self.sm.current_scene.render()
            pygame.display.update()
            clock.tick(60)


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
