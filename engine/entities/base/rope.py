import math
import pygame
from engine.entities.base.entity import Entity
from engine.core.engine_dataclasses import DEBUGCONFIG

Vector2 = pygame.Vector2


class Particle:
    def __init__(self, x, y, mass, fixed):
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y
        self.init_pos_x = x
        self.init_pos_y = y
        self.mass = mass
        self.fixed = fixed

    def set_init_pos(self):
        self.x = self.init_pos_x
        self.y = self.init_pos_y


class Stick:
    def __init__(self, p1, p2, length):
        self.p1 = p1
        self.p2 = p2
        self.length = length

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.p1.x, self.p1.y, 3, self.length)


class ParticleRope(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.particles: list[Particle] = []
        self.sticks: list[Stick] = []
        self.gravity = kwargs.get('gravity')
        self.length = kwargs.get('length')
        self.mass = kwargs.get('mass')
        self.color = pygame.Color(kwargs.get('color'))
        self.amount_of_particles = kwargs.get('amount_of_particles')
        self.drag = kwargs.get('drag')
        self.end_x = kwargs.get('end_x')
        self.end_y = kwargs.get('end_y')
        self.elasticity = 4
        self.attached_entity = None
        self.flags.rope = 1
        self.flags.interactable = kwargs.get('interactable')
        for i in range(self.amount_of_particles):
            self.particles.append(
                Particle(self.position.x, self.position.y + self.length * i, self.mass, True if i == 0 else False))
        if self.end_x >= 0 and self.end_y >= 0:
            self.particles.append(Particle(self.end_x, self.end_y, self.mass, True))
        for i, particle in enumerate(self.particles):
            if i > 0:
                self.sticks.append(Stick(self.particles[i - 1], self.particles[i], self.length))

    def __get_difference(self, p1: Vector2, p2: Vector2):
        return Vector2(p1.x - p2.x, p1.y - p2.y)

    def __get_length(self, p: Vector2):
        return math.sqrt(p.x * p.x + p.y * p.y)

    def set_impact(self, entity):
        if not self.flags.interactable:
            return
        if entity.velocity.x != 0:
            for particle in self.particles:
                if entity.rect.collidepoint((particle.x, particle.y)) and not particle.fixed:
                    particle.x += entity.velocity.x + (entity.face[0] * 0.5)
                    # project.position = pygame.Vector2(particle.x, particle.y)

    def __get_distance(self, p1: Particle, p2: Particle):
        dx = p1.x - p2.x
        dy = p1.y - p2.y
        return math.sqrt(dx * dx + dy * dy)

    def move_head(self, position):
        self.particles[0].x += position.x
        self.particles[0].y += position.y
        self.particles[0].init_pos_x += position.x
        self.particles[0].init_pos_y += position.y

    def update(self, dt):
        for particle in self.particles:
            if particle.fixed:
                particle.set_init_pos()
                continue
            force = Vector2(0, self.gravity)
            acceleration = Vector2(force.x / particle.mass, force.y / particle.mass)
            prev_pos = Vector2(particle.x, particle.y)

            particle.x = 2 * particle.x - particle.prev_x + acceleration.x * (dt * dt)
            particle.y = 2 * particle.y - particle.prev_y + acceleration.y * (dt * dt)

            particle.prev_x = prev_pos.x
            particle.prev_y = prev_pos.y

        for stick in self.sticks:
            diff = self.__get_difference(stick.p1, stick.p2)
            dist = math.sqrt(diff.x * diff.x + diff.y * diff.y)
            diff_factor = (stick.length - dist) / dist
            offset = Vector2(diff.x * diff_factor * 0.5, diff.y * diff_factor * 0.5)

            stick.p1.x += offset.x
            stick.p1.y += offset.y
            stick.p2.x -= offset.x
            stick.p2.y -= offset.y

        return True

    def check_for_rect_collision(self, rect: pygame.Rect):
        for i, stick in enumerate(self.sticks):
            if rect.colliderect(stick.rect):
                try:
                    self.sticks.pop(i)
                    return True
                except IndexError:
                    print("End of rope has been hit")

    def render(self, surf, offset=(0, 0)):
        super().render(surf)

        if DEBUGCONFIG.rope_show_points:
            for particle in self.sticks:
                pygame.draw.rect(surf, (255, 255, 255),
                                 pygame.Rect(particle.rect.x - offset[0], particle.rect.y - offset[1], 3,
                                             particle.length))
        else:
            for stick in self.sticks:
                pygame.draw.line(surf, self.color, Vector2(stick.p1.x - offset[0], stick.p1.y - offset[1]),
                                 Vector2(stick.p2.x - offset[0], stick.p2.y - offset[1]), 1)
