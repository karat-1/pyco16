import pygame
from engine.overlay.overlay import Overlay
from engine.overlay.blockflags import BlockFlags

class FadeOverlay(Overlay):
    def __init__(self, duration=1.0, on_complete=None, ctx=None, wctx=None):
        super().__init__(ctx, wctx)
        self.duration = duration
        self.progress = 0.0
        self.on_complete = on_complete

    def update(self, dt):
        self.progress += dt / self.duration
        if self.progress >= 1.0:
            self.progress = 1.0
            if self.on_complete:
                self.on_complete()
                self.on_complete = None

    def render(self, surf: pygame.Surface):
        if self.progress <= 0:
            return

        # Create a surface with per-pixel alpha
        overlay = pygame.Surface(surf.get_size(), flags=pygame.SRCALPHA)

        # Fill with black and set the alpha channel
        alpha = int(255 * self.progress)
        overlay.fill((0, 0, 0, alpha))

        # Blit onto the target surface
        surf.blit(overlay, (0, 0))

    def blocks(self) -> BlockFlags:
        # blocks everything during fade
        return BlockFlags(world=True, entities=True, camera=True, vfx=True, input=True)