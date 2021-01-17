import pathlib
from pathlib import Path
import sys
from typing import Tuple
import random
import math

import pygame

from gamesystem import scene_transision as scenetrans

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
    def __init__(self, x, y, terrain, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = x
        self.y = y
        self.terrain = terrain
        self.dx = 0
        self.dy = 0
        self.max_sightrange = 160
        self.min_sightrange = 0
        self.target_pos = None
        self.rect = pygame.Rect(self.x, self.y, 6, 8)
        self.sheet = SpriteSheet(assets_path.img_path(
            "human.png"), 4, 4, 6, 8, BLACK)
        self.image = self.sheet.image_by_cell(1, 1)

    def update(self, *args, **kwargs):
        self.random_direction()
        self.x += self.dx * 2
        self.y += self.dy * 2
        self.update_img_pos()
        search_result = self.search_tile("Tree", 3)
        if search_result:
            print("can find")
        # self.can_see_in_sightrange((0, 0))

    def random_direction_y(self):
        self.dy = random.randint(-1, 1)

    def random_direction_x(self):
        self.dx = random.randint(-1, 1)

    def random_direction(self):
        self.random_direction_x()
        self.random_direction_y()

    def update_img_pos(self):
        self.rect.x = self.x
        self.rect.y = self.y

    def can_see_in_sightrange(self, obj_be_seen_pos) -> bool:
        dist_two_point_x = obj_be_seen_pos[0] - self.x
        dist_two_point_y = obj_be_seen_pos[1] - self.y
        dist_two_point = math.sqrt(dist_two_point_x**2 + dist_two_point_y**2)
        if self.min_sightrange <= dist_two_point <= self.max_sightrange:
            return True
        else:
            return False

    def pos_as_tilemap(self):
        col = self.x // self.terrain.tilesize
        row = self.y // self.terrain.tilesize
        return col, row

    def search_tile(self, tile, layer) -> bool:
        tilemap = self.terrain.map[layer]
        tile_id = self.terrain.tile_id_assign[tile]
        tilesize = self.terrain.tilesize
        search_result = False
        for y in range(len(tilemap)):
            for x in range(len(tilemap[y])):
                if tilemap[y][x] == tile_id:
                    search_result = self.can_see_in_sightrange(
                        (x*tilesize+tilesize//2, y*tilesize+tilesize//2))
                    if search_result:
                        break
        return search_result

    def set_target_pos(self, pos):
        self.target_pos = pos


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


def get_swap_dict(dictionary):
    return {value: key for key, value in dictionary.items()}


class Terrain:
    def __init__(self):
        self.tile_id_assign = {None: 0, "Glass": 1,
                               "Dirt": 2, "Water": 3, "Tree": 4, "Mount": 5}
        self.tile_type_from_id = get_swap_dict(self.tile_id_assign)
        self.map = [[[]]]
        self.tilesize = 16

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


class GameSceneManager(scenetrans.SceneManager):
    def __init__(self, screen: pygame.Surface, game):
        super().__init__()
        self.screen = screen
        self.game = game


class TitleScene(scenetrans.Scene):
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


class GameScene(scenetrans.Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.terrain = Terrain()
        self.TILESIZE = self.terrain.tilesize  # to be short
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
        self.mouse_pos_history = []
        self.terrain.reset_map(4, self.MAP_HEIGHT, self.MAP_WIDTH)
        self.terrain.fill_map(2, 0, 64, 0, 64, "Glass")
        self.map_surface = pygame.Surface(
            (self.MAP_WIDTH*self.TILESIZE, self.MAP_HEIGHT*self.TILESIZE)
        ).convert_alpha()
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
        self.destroy_tile_btn = ButtonSprite(
            "Eraser", 16 + btn_size[0]*2 + 16*2,
            SCRN_HEIGHT - 139 + 16 + btn_size[1] + 16)
        self.btn_group = pygame.sprite.RenderUpdates()
        self.btn_group.add(self.water_btn, self.dirt_btn,
                           self.mount_btn, self.tree_btn,
                           self.human_btn,
                           self.save_btn, self.load_btn,
                           self.destroy_tile_btn)
        self.mob_group = pygame.sprite.Group()

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
            is_btn_pressing = False
            for btn_sprite in iter(self.btn_group):
                if btn_sprite.is_pressed:
                    is_btn_pressing = True
                    break
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
                        if btn_sprite.id == "Eraser":
                            self.rewrite_tile_with_mouse(
                                3, None, event.pos
                            )
        # scroll map
        self.scroll_x += self.scroll_vx
        self.scroll_y += self.scroll_vy
        self.scroll_vx = 0
        self.scroll_vy = 0

    def is_pos_on_map(self, pos):
        return (self.MAP_VIEWER_X <= pos[0] <=
                (self.MAP_VIEWER_WIDTH + self.TILESIZE) and
                self.MAP_VIEWER_Y <= pos[1] <=
                (self.MAP_VIEWER_HEIGHT + self.TILESIZE))

    def spawn_human_with_mouse(self, mouse_pos):
        spawn_x = (self.scroll_x+mouse_pos[0]-self.MAP_VIEWER_X)
        spawn_y = (self.scroll_y+mouse_pos[1]-self.MAP_VIEWER_Y)
        human_sprite = HumanSprite(spawn_x, spawn_y, self.terrain)
        self.mob_group.add(human_sprite)

    def rewrite_tile_with_mouse(self, layer_id, tile_type, mouse_pos):
        tile_x = (self.scroll_x+mouse_pos[0]-self.MAP_VIEWER_X)//self.TILESIZE
        tile_y = (self.scroll_y+mouse_pos[1]-self.MAP_VIEWER_Y)//self.TILESIZE
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
        self.destroy_tile_btn.set_image_with_icon(2, 4)
        self.mob_group.draw(self.map_surface)
        self.btn_group.draw(self.sm.screen)
        for mob in self.mob_group:
            self.render_mob_sightrange(mob)
        self.sm.screen.blit(self.map_surface,
                            (self.MAP_VIEWER_X, self.MAP_VIEWER_Y),
                            (0+self.scroll_x,
                             0+self.scroll_y,
                             self.MAP_VIEWER_WIDTH,
                             self.MAP_VIEWER_HEIGHT))
        self.mob_group.update()
        font = pygame.font.Font(
            str(assets_path.font_path("misaki_gothic_2nd.ttf")), 32)
        cursor_pos_text = font.render(
            f"x:{pygame.mouse.get_pos()[0]} y:{pygame.mouse.get_pos()[1]}",
            True, WHITE)
        self.sm.screen.blit(cursor_pos_text, (0, 0))

    def render_mob_sightrange(self, mob):
        pygame.draw.circle(self.map_surface, (255, 0, 0),
                           (mob.x+mob.rect.width//2, mob.y+mob.rect.height//2),
                           mob.max_sightrange, 1)

    def render_terrain(self, terrain_map):
        sprite = SpriteSheet(assets_path.img_path(
            "skyeyebg.png"), 1, 1, self.TILESIZE, self.TILESIZE, BLACK)
        for z in range(len(terrain_map)):
            for y in range(len(terrain_map[0])):
                for x in range(len(terrain_map[0][0])):
                    if terrain_map[z][y][x] == 1:
                        self.map_surface.blit(
                            sprite.image_by_cell(1, 1),
                            (self.TILESIZE*x, self.TILESIZE*y))
                    elif terrain_map[z][y][x] == 2:
                        self.map_surface.blit(
                            sprite.image_by_cell(1, 2),
                            (self.TILESIZE*x, self.TILESIZE*y))
                    elif terrain_map[z][y][x] == 3:
                        self.map_surface.blit(
                            sprite.image_by_cell(3, 1),
                            (self.TILESIZE*x, self.TILESIZE*y))
                    elif terrain_map[z][y][x] == 4:
                        self.map_surface.blit(
                            sprite.image_by_cell(2, 7),
                            (self.TILESIZE*x, self.TILESIZE*y))
                    elif terrain_map[z][y][x] == 5:
                        self.map_surface.blit(
                            sprite.image_by_cell(1, 5),
                            (self.TILESIZE*x, self.TILESIZE*y))

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


class WorldSelectScene(scenetrans.Scene):
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


class Game:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(KEY_REPEAT_DELAY, KEY_REPEAT_INTERVAL)
        pygame.display.set_caption(GAME_TITLE)
        self.screen = pygame.display.set_mode(SCRN_SIZE)
        self.world_manager = WorldDataManager(MAIN_PRG_DIR / "saves")
        # sm means "screen manager"
        self.sm = GameSceneManager(self.screen, self)
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
