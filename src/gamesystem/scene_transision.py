class SceneManager:
    def __init__(self):
        self.scene_list = {}
        self.current_scene = None

    def append_scene(self, scene_name, scene):
        self.scene_list[scene_name] = scene

    def set_current_scene(self, scene_name):
        self.current_scene = self.scene_list[scene_name]


class Scene:
    def __init__(self, scene_manager):
        self.sm = scene_manager

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def render(self):
        pass
