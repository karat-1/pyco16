from engine.content.contentmanager_new import ContentManager
from engine.inputsystem.input import Input
from engine.rendersystem.renderer import Renderer
from engine.rendersystem.window import Window
from project.simple_world import SimpleWorld
from engine.core.savegame import SaveGame


class Game:
    def __init__(self):
        self.window = Window(self)
        self.input = Input(self)
        self.content_manager = ContentManager()
        self.renderer = Renderer(self)
        self.savegame = SaveGame(self)
        self.world = SimpleWorld(self)
        self.world.init_world()

    def update(self):
        self.input.update()
        self.world.update()
        self.renderer.render(self.window.screen)
        self.window.render_frame()

    def run(self):
        while True:
            self.update()


# Entrypoint
Game().run()
