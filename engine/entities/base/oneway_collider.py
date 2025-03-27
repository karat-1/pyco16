import pygame

from engine.entities.base.entity import Entity


class OnewayCollider(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flags.oneway_collider = 1

    def render(self, surf: pygame.Surface, offset=(0, 0)) -> None:
        super().render(surf, offset)
        """pygame.draw.rect(surf, (255, 255, 0),
                         pygame.Rect(self.position.x - offset[0], self.position.y - offset[1], self.size.x,
                                     self.size.y))"""



