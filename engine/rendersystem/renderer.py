import pygame


class Renderer:
    def __init__(self, game):
        self.game = game

    def render(self, screensurf):
        """
        Takes the games display surface, gives it to the world to let it render
        all the GameObjects, Tiles and Entities, and then adds all speical FX
        to the Surface (e.g. Bloom, HUD, etc.)
        """

        surf = self.game.window.display
        self.game.world.render(surf)

        pygame.transform.scale_by(self.game.window.display,
                                  (self.game.window.window_resolution[0] // self.game.window.base_resolution[0],
                                   self.game.window.window_resolution[1] // self.game.window.base_resolution[1]),
                                  self.game.window.screen)

        self.game.world.render_ui(self.game.window.screen)
