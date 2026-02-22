class Renderer:
    def __init__(self, ctx):
        self.ctx = ctx

    def render(self):
        """
        Takes the games display surface, gives it to the world to let it render
        all the GameObjects, Tiles and Entities, and then adds all speical FX
        to the Surface (e.g. Bloom, HUD, etc.)
        """

        surf = self.ctx.window.display
        self.ctx.scene_manager.render(surf)
