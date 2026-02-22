import pygame

from project.projectsettings import WindowSettings


class Renderer:
    def __init__(self, ctx):
        self.ctx = ctx

    def render(self, screensurf, world):
        """
        Takes the games display surface, gives it to the world to let it render
        all the GameObjects, Tiles and Entities, and then adds all speical FX
        to the Surface (e.g. Bloom, HUD, etc.)
        """

        surf = self.ctx.window.display
        world.render(surf)

        pygame.transform.scale_by(
            self.ctx.window.display,
            (
                WindowSettings.resoloution_scale,
                WindowSettings.resoloution_scale,
            ),
            self.ctx.window.screen,
        )

        ox = int(-world.wctx.camera.screen_shake.x)
        oy = int(-world.wctx.camera.screen_shake.y)

        self.ctx.window.screen.scroll(ox, oy)

        # world.render_ui(self.ctx.window.screen)
