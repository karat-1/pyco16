import pygame

from engine.scene.scene import Scene


class ExampleScene(Scene):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.rect_position: pygame.Vector2 = pygame.Vector2(0, 0)
        # Geschwindigkeit in Pixel pro Frame
        self.rect_velocity: pygame.Vector2 = pygame.Vector2(60, 60)
        self.rect_size: int = 20  # Größe des Rechtecks

    def update(self):
        super().update()
        dt = self.ctx.window.dt
        self.rect_position += self.rect_velocity * dt

        max_x = self.ctx.game_settings.room_width - self.rect_size
        max_y = self.ctx.game_settings.room_height - self.rect_size

        if self.rect_position.x <= 0 or self.rect_position.x >= max_x:
            self.rect_velocity.x *= -1  # Richtung umkehren
            self.rect_position.x = max(0, min((self.rect_position.x, max_x)))  # Clamp

        if self.rect_position.y <= 0 or self.rect_position.y >= max_y:
            self.rect_velocity.y *= -1
            self.rect_position.y = max(0, min((self.rect_position.y, max_y)))

    def render(self, surf: pygame.Surface):
        super().render(surf)
        pygame.draw.rect(
            surf,
            (0, 0, 0),  # Weiß
            pygame.Rect(self.rect_position.x, self.rect_position.y, self.rect_size, self.rect_size)
        )