from typing import Optional
from engine.content.contentmanager_new import ContentManager
from engine.core.gamecontext import GameContext
from engine.eventsystem.eventbus import EventBus
from engine.input.input import Input
from engine.render.moderngl.renderer import Renderer
from engine.render.moderngl.window import Window
from engine.scene.scenemanager import SceneManager
from examples.scenes.examplescene import ExampleScene
from engine.core.savegame import SaveGame
from engine.sound.soundmanager import SoundManager
from engine.config.projectconfig import WindowSettings, GameSettings, ResourcePaths


class Game:
    def __init__(
        self,
        window_settings: Optional[WindowSettings] = None,
        game_settings: Optional[GameSettings] = None,
        resource_paths: Optional[ResourcePaths] = None
    ) -> None:
        self.window_settings: WindowSettings = window_settings or WindowSettings()
        self.game_settings: GameSettings = game_settings or GameSettings()
        self.resource_paths: ResourcePaths = resource_paths or ResourcePaths()

        self.ctx: GameContext = GameContext()

        # Settings first
        self.ctx.set_game_settings(self.game_settings)
        self.ctx.set_window_settings(self.window_settings)
        self.ctx.set_resource_paths(self.resource_paths)

        # Initialize services with settings
        self.ctx.set_window(Window(self.ctx))
        self.ctx.set_input(Input(self.ctx))
        self.ctx.set_global_eventmanager(EventBus())
        self.ctx.set_content(ContentManager(self.ctx))
        self.ctx.set_renderer(Renderer(self.ctx))
        self.ctx.set_savegame(SaveGame(self.ctx))
        self.ctx.set_sound(SoundManager(self.ctx))
        self.ctx.set_scene_manager(SceneManager(self.ctx))

        self.ctx.freeze()

        # Initialize the scene
        self.example_scene: ExampleScene = ExampleScene(self.ctx)
        self.ctx.scene_manager.register_scene(self.example_scene)
        self.ctx.scene_manager.set_active_scene(self.example_scene)

        self.running: bool = True

    def update(self) -> None:
        self.ctx.input.update()
        self.ctx.scene_manager.update()
        self.ctx.renderer.render()
        self.ctx.window.render_frame()

    def run(self) -> None:
        try:
            while self.running:
                self.update()
        except KeyboardInterrupt:
            print("Game stopped by user.")
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        print("Shutting down game.")


if __name__ == "__main__":
    game = Game().run()
