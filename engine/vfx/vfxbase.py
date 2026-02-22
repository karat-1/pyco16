import math
from dataclasses import dataclass

import pygame

from engine.core.engine_core_funcs import approach


class VFXAnimation:
    def __init__(self, frames, position, end_alpha):
        self.frames: list[pygame.Surface] = frames
        self.current_frame = 0
        self.position: pygame.Vector2 = position
        self.end_alpha = end_alpha
        self.__alpha = 255

    @property
    def active_img(self) -> pygame.Surface:
        return self.frames[int(self.current_frame)]

    def update(self, dt):
        self.current_frame += dt

    def render(self, surf: pygame.Surface, offset):
        surf.blit(self.active_img,
                  (self.position.x - self.active_img.width // 2 - offset[0],
                   self.position.y + self.active_img.height // 2 - offset[1]))


class VFXEffect:
    def __init__(self, position, color, end_color=None, animation_speed=100, width=1):
        self.position = position
        self.color = color
        self.end_color = end_color
        if self.end_color is None:
            self.end_color = color
        self.animation_speed = animation_speed
        self.current_color = color
        self.width = width
        self.alive = True

    def update(self, dt):
        pass

    def render(self, surf: pygame.Surface, offset):
        pass


class VFXCircleEffect(VFXEffect):
    def __init__(self, position, color, start_radius, end_radius, animation_speed=100):
        super().__init__(position, color, animation_speed)
        self.start_radius = start_radius
        self.end_radius = end_radius
        self.current_radius = start_radius

    def update(self, dt):
        self.current_radius = approach(self.current_radius, self.end_radius, self.animation_speed * dt)
        if self.current_radius == self.end_radius:
            self.alive = False

    def render(self, surf: pygame.Surface, offset):
        super().render(surf, offset)
        pygame.draw.circle(surf, self.current_color, self.position - offset, self.current_radius, self.width)


class VFXLineEffect(VFXEffect):
    def __init__(self, position, color, magnitude: int, angle_deg: int, end_color=None, animation_speed=100):
        super().__init__(position, color, end_color, animation_speed)
        self.angle = angle_deg
        self.angle_rad = math.radians(angle_deg)
        self.magnitude = magnitude
        self.position_positive = pygame.Vector2([0, 0])
        self.position_negative = pygame.Vector2([0, 0])
        self.__calculate_length()

    def update(self, dt):
        self.magnitude = approach(self.magnitude, 0, self.animation_speed * dt)
        if self.magnitude <= 0:
            self.magnitude = 0
            self.alive = False

        self.__calculate_length()

    def __calculate_length(self):
        dx = math.cos(self.angle_rad) * self.magnitude
        dy = math.sin(self.angle_rad) * self.magnitude

        self.position_positive = self.position - pygame.Vector2(dx, dy)
        self.position_negative = self.position + pygame.Vector2(dx, dy)

    def render(self, surf: pygame.Surface, offset):
        super().render(surf, offset)
        pygame.draw.aaline(surf, self.current_color, self.position - offset, self.position_positive - offset)
        pygame.draw.aaline(surf, self.current_color, self.position - offset, self.position_negative - offset)


class VFXBase:
    def __init__(self):
        self.circle_surfaces = self._generate_circle_surfaces()
        self.active_texture_animations: list[VFXAnimation] = []
        self.active_effect_animations: list[VFXEffect] = []
        self.__active_effect_queue: list[VFXEffect] = []
        self.__active_texture_queue: list[VFXAnimation] = []

    def add_vfx_effect(self, effect):
        self.__active_effect_queue.append(effect)

    def update(self, dt):
        # Entities and other stuff spawns effects, add them now then update
        for added_anim in self.__active_effect_queue:
            self.active_effect_animations.append(added_anim)
        self.__active_effect_queue.clear()
        for added_anim in self.__active_texture_queue:
            self.active_texture_animations.append(added_anim)
        self.__active_texture_queue.clear()

        for active_anim in self.active_texture_animations[:]:
            active_anim.update(dt)
        for i, active_anim in enumerate(self.active_effect_animations[:]):
            active_anim.update(dt)
            if not active_anim.alive:
                self.active_effect_animations.remove(active_anim)

    def _generate_circle_surfaces(self):
        surfaces = []
        size = 32
        center = (size // 2, size // 2)
        color = (255, 255, 255, 255)  # White with full alpha
        max_radius = size // 2  # 16 for 32x32

        for radius in range(1, max_radius + 1):
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, center, radius, width=1)
            surfaces.append(surf)
        return surfaces

    def __get_expanding_circle(self, frame):
        """
        Get the surface for the expanding circle animation.
        frame: int from 0 to len(self.circle_surfaces)-1 (smallest to largest)
        """
        if 0 <= frame < len(self.circle_surfaces):
            return self.circle_surfaces[frame]
        else:
            raise IndexError("Frame out of range for expanding circle")

    def __get_decreasing_circle(self, frame):
        """
        Get the surface for the decreasing circle animation.
        frame: int from 0 to len(self.circle_surfaces)-1 (largest to smallest)
        """
        if 0 <= frame < len(self.circle_surfaces):
            return self.circle_surfaces[-1 - frame]
        else:
            raise IndexError("Frame out of range for decreasing circle")

    def render(self, surf, offset):
        for active_anim in self.active_texture_animations:
            active_anim.render(surf, offset)
        for active_anim in self.active_effect_animations:
            active_anim.render(surf, offset)
