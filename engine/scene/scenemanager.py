import pygame

from engine.scene.scene import Scene


class SceneManager:
    def __init__(self, ctx):
        self.scenes: dict[str, Scene] = {}  # alle registrierten Szenen
        self.active_scene: Scene | None = None
        self.master_clock: float = 0.0
        self.dt: float = 0.0
        self.ctx = ctx

    def switch_scene(self, name: str):
        scene = self.scenes.get(name)
        if not scene:
            raise ValueError(f"Scene '{name}' nicht gefunden")

        if self.active_scene:
            self.active_scene.exit_scene()

        self.active_scene = scene
        self.active_scene.init_scene()
        self.active_scene.load_scene()
        self.active_scene.enter_scene()

    def register_scene(self, scene: Scene):
        if scene.name in self.scenes.keys():
            raise ValueError(f"Scene '{scene.name}' already exists")
        self.scenes[scene.name] = scene
        scene.init_scene()
        scene.load_scene()
        scene.enter_scene()

    def set_active_scene(self, scene):
        if not scene.name in self.scenes.keys():
            raise ValueError(f"Scene '{scene.name}' nicht gefunden")
        self.active_scene = self.scenes.get(scene.name)

    def update(self):
        _dt = self.ctx.window.dt
        self.dt = _dt
        self.master_clock += _dt
        if self.active_scene:
            self.active_scene.update()

    def render(self, surf: pygame.Surface):
        if self.active_scene:
            self.active_scene.render(surf)
