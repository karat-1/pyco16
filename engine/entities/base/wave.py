import pygame
import numpy
import random
from engine.entities.base.entity import Entity
from scipy.interpolate import interp1d
import numpy as np
from scipy.ndimage import gaussian_filter, uniform_filter

Point = pygame.Vector2


def gaussian_blur(surface, sigma=4):
    array = pygame.surfarray.pixels3d(surface).astype(np.float32)
    blurred_array = gaussian_filter(array, sigma=(sigma, sigma, 0))
    pygame.surfarray.blit_array(surface, blurred_array.astype(np.uint8))
    return surface


def fast_box_blur(surface, blur_radius=2):
    """Blurs a surface using a fast box blur with NumPy and SciPy."""
    array = pygame.surfarray.array3d(surface).astype(np.float32)  # Get RGB pixel array
    blurred_array = uniform_filter(array, size=(blur_radius, blur_radius, 1))  # Fast convolution
    pygame.surfarray.blit_array(surface, blurred_array.astype(np.uint8))  # Convert back
    return surface


def create_gradient_surface(size, color1, color2, position):
    gradient = pygame.Surface((64, 64), pygame.SRCALPHA)
    width, height = size
    for y in range(int(height)):
        t = y / height
        r = int(color1[0] + (color2[0] - color1[0]) * t)
        g = int(color1[1] + (color2[1] - color1[1]) * t)
        b = int(color1[2] + (color2[2] - color1[2]) * t)
        pygame.draw.line(gradient, (r, g, b, 255), (position.x, position.y - y + 8), (position.x + width, position.y - y + 8))
    return gradient


class Spring:
    def __init__(self, position):
        self.position = pygame.Vector2(position.x, position.y)
        self.target_y = position.y
        self.dampening = 0.10
        self.tension = 0.05
        self.velocity = pygame.Vector2(0, 0)

    def update(self, dt):
        dh = self.target_y - self.position.y
        if abs(dh) < 0.01:
            self.position.y = self.target_y
        self.velocity.y += self.tension * dh - self.velocity.y * self.dampening
        self.position.y += self.velocity.y * 60 * dt

    @property
    def rect(self):
        return pygame.Rect(self.position.x, self.position.y, 1, 1)

    def render(self, surface: pygame.Surface, type: str = 'circle'):
        if type == 'rect':
            pygame.draw.rect(surface, (255, 255, 255), self.rect)
        elif type == 'circle':
            pygame.draw.circle(surface, (255, 255, 255), self.position, 1)


class Wave(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.springs: list[Spring] = []
        self.points: list[Point] = []
        self.polysurf: pygame.Surface = pygame.Surface((64, 64), pygame.SRCALPHA)
        self.polysurf.set_colorkey((0, 0, 0))
        self.alpha = (kwargs.get("alpha"))
        self.top_color = pygame.Color(kwargs.get('top_color'))
        self.bottom_color = pygame.Color(kwargs.get('bottom_color'))
        self.glow: bool = kwargs.get('glow')
        self.type: str = kwargs.get('type')
        self.wave_type: str = kwargs.get('wave_type')
        self.natural_variance = 1
        self.natural_variance_counter = 0
        self.lava_gradient = None
        self.top_line_color = kwargs.get('top_line_color')

        point_iterations = int(self.size.x // 4)

        for i in range(point_iterations + 1):
            self.springs.append(Spring(pygame.Vector2(self.position.x + (i * 4), self.position.y)))

        # this has to be done once otherwise it crashes upon entering a new room
        self.points = [Point(spring.position.x, spring.position.y) for spring in self.springs]

        # water needs to be moved once
        variance = random.randint(-self.natural_variance, self.natural_variance)
        self.springs[random.randint(1, len(self.springs) - 2)].position.y += variance
        self.natural_variance_counter = 0

    def update(self, dt):
        for spring in self.springs:
            spring.update(dt)
        self.spread_wave(dt)
        self.points = [Point(spring.position.x, spring.position.y) for spring in self.springs]
        # self.points = self.get_curve()
        self.points.extend([Point(self.position.x + self.size.x, self.position.y + self.size.y),
                            Point(self.position.x, self.position.y + self.size.y)])

        self.natural_variance_counter += dt
        if self.natural_variance_counter > 60:
            variance = random.randint(-self.natural_variance, self.natural_variance)
            self.springs[random.randint(1, len(self.springs) - 2)].position.y += variance
            self.natural_variance_counter = 0

        return True

    def get_curve(self):
        x_new = numpy.arange(self.points[0].x, self.points[-1].x, 1)
        x = numpy.array([i.x for i in self.points[:-1]])
        y = numpy.array([i.y for i in self.points[:-1]])
        f = interp1d(x, y, kind='cubic', fill_value='extrapolate')
        y_new = f(x_new)
        x1 = list(x_new)
        y1 = list(y_new)
        points = [Point(x1[i], y1[i]) for i in range(len(x1))]
        return points

    def spread_wave(self, dt):
        spread = 0.01
        for i, spring in enumerate(self.springs[:-1]):
            if i > 0:
                self.springs[i - 1].velocity.y += (spread * (
                        self.springs[i].position.y - self.springs[i - 1].position.y)) * dt
            try:
                self.springs[i + 1].velocity.y += (spread * (
                        self.springs[i].position.y - self.springs[i + 1].position.y)) * dt
            except IndexError:
                pass
        self.springs[0].position.y = self.springs[0].target_y
        self.springs[-1].position.y = self.springs[-3].target_y

    def set_impact(self, entity):
        if entity.velocity.y != 0:
            for spring in self.springs:
                if entity.rect.collidepoint(spring.position):
                    spring.position.y = entity.rect.bottom

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset)
        for point in self.points:
            point.x -= offset[0]
            point.y -= offset[1]
        self.points[-3].x -= 1
        self.points[-2].x -= 1

        # while this works it has way too many hardcoded numbers, I need to rework this at some point
        self.polysurf.fill((0, 0, 0, 0))
        self.lava_gradient = create_gradient_surface((self.size.x, self.size.y + 8), self.bottom_color,
                                                     self.top_color, self.position - offset)
        pygame.draw.polygon(self.polysurf, (255, 255, 255, self.alpha), self.points)
        self.lava_gradient.blit(self.polysurf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(self.lava_gradient, (0, 0))

        if self.glow:
            for i in range(3):
                glow = gaussian_blur(self.lava_gradient.copy(), 2 + i)
                glow.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                surf.blit(glow, (0, 0 - i), special_flags=pygame.BLEND_RGBA_ADD)

        surf.blit(self.lava_gradient, (0, 0))

        # rendering the line
        pygame.draw.lines(surf, self.top_line_color, False, self.points[:-2], 1)

        # debugging renderering
        # for spring in self.springs:
        #    spring.render(surf, 'rect')
