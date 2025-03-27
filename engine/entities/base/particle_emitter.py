import math
from dataclasses import dataclass, fields
from engine.core.engine_core_funcs import lerp, clamp

import pygame
from pygame import Vector2, Color
from engine.entities.base.entity import Entity
import random
from engine.entities.base.particle_presets import ParticleBaseSettings


def from_kwargs(kwargs):
    return ParticleBaseSettings(**{k: v for k, v in kwargs.items() if k in ParticleBaseSettings.__annotations__})


def interpolate_color(color1, color2, t):
    """
    Interpolates between two Pygame Color objects.

    :param color1: First Pygame Color (e.g., pygame.Color("#be4a2f"))
    :param color2: Second Pygame Color (e.g., pygame.Color("#ead4aa"))
    :param t: Interpolation factor (0.0 to 1.0)
    :return: Interpolated Pygame Color
    """
    return pygame.Color(
        int(color1.r + (color2.r - color1.r) * t),
        int(color1.g + (color2.g - color1.g) * t),
        int(color1.b + (color2.b - color1.b) * t),
        int(color1.a + (color2.a - color1.a) * t)
    )


@dataclass
class Particle:
    position: Vector2
    start_position: Vector2
    velocity: Vector2
    frequency: float
    phase: float
    direction: int
    color: Color
    time_elapsed: float
    lifetime: float
    size: int
    surf: pygame.Surface | None
    gsurf: pygame.Surface | None
    alpha: int


class ParticleEmitter(Entity):
    _SURFACES_RECT = [pygame.Surface((i, i), pygame.SRCALPHA) for i in range(1, 11)]
    _SURFACES_CIRCLE = [pygame.Surface((i * 2, i * 2), pygame.SRCALPHA) for i in range(1, 11)]

    # Fill rectangle surfaces with white
    for surf in _SURFACES_RECT:
        surf.fill((255, 255, 255, 255))

    # Pre-draw circles onto surfaces
    for i, surf in enumerate(_SURFACES_CIRCLE, start=1):
        pygame.draw.circle(surf, (255, 255, 255, 255), (i, i), i)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # counter variables that are not passed in as kwargs
        self.particles: list[Particle] = []
        self.spawn_timer: float = 0
        self.master_clock: float = 0
        self.flags.particle_system = 1
        self.time_elapsed: float = 0
        self.parent = kwargs.get('parent', False)
        self.blit_list = []
        self.glow_blit_list = []
        self.room_rect = pygame.Rect(self.position.x // 64 * 64, self.position.y // 64 * 64, 64, 64)
        self.particle_count = 0
        self.is_active = True

        # set the base object in case no kwargs with settings are passed in
        self.p_base = ParticleBaseSettings()

        # if no kwargs are given nothing happens, if kwargs are given the base settings are overwritten
        # kwargs should only be supplied by editor instantiaton. for in engine use instantiate the emitter first
        # and then apply the config
        self.apply_config(from_kwargs(kwargs))

    def apply_config(self, config: ParticleBaseSettings) -> None:
        """
        This function is for in engine use only. It will overwrite the existing settings with a new settings
        object.
        :param config:
        :return:
        """
        for f in fields(self.p_base):
            if hasattr(config, f.name):  # Ensure the field exists in the provided config
                setattr(self.p_base, f.name, getattr(config, f.name))
        if isinstance(self.p_base.color_start, str):
            self.p_base.color_start = Color(self.p_base.color_start)
        if isinstance(self.p_base.color_end, str):
            self.p_base.color_end = Color(self.p_base.color_end)

    def spawn_particle_group(self, amount):
        for i in range(amount):
            self.__spawn_particle()

    def __spawn_particle_rate(self, spawn_rate):
        for i in range(spawn_rate):
            self.__spawn_particle()

    def set_state(self, state: bool):
        self.is_active = state

    def __spawn_particle(self):
        # particles are spawned in a rect. this calculates an offset from the rect origin
        rnd_x = random.randint(0, self.size.x)
        rnd_y = random.randint(0, self.size.y)

        # that offset is applied here
        pos_x = self.position.x + rnd_x
        pos_y = self.position.y + rnd_y

        # this is the frequence and phase of the sine wave and lifetime.
        # each particle needs its own freq and phase so they dont move in sync
        frequency = random.uniform(0.3, 0.6)
        phase = random.uniform(0.6, 2 * math.pi)
        random_lifetime_deviation = 0

        rnd_x_dir = random.choice([-1, 1]) if self.p_base.random_x_dir else 1
        rnd_y_dir = random.choice([-1, 1]) if self.p_base.random_y_dir else 1

        rnd_x_deviation = random.uniform(0, self.p_base.random_velocity_deviation)

        v = Vector2(self.p_base.particle_velocity_x * rnd_x_dir + rnd_x_deviation,
                    self.p_base.particle_velocity_y * rnd_y_dir)

        # create surf placeholder, get the proper surf and color it accordingly
        psurf = None
        match self.p_base.particle_type:
            case "RECT":
                psurf = self._get_rect_surface(self.p_base.start_size)
                psurf.fill(self.p_base.color_start)
            case "CIRCLE":
                psurf = self._get_circle_surface(self.p_base.start_size)
                psurf.fill(self.p_base.color_start)
            case "ANIMATION":
                pass

        particle = Particle(position=Vector2(pos_x, pos_y),
                            start_position=Vector2(pos_x, pos_y),
                            velocity=v,
                            frequency=frequency,
                            phase=phase,
                            direction=1,
                            color=self.p_base.color_start,
                            time_elapsed=0,
                            lifetime=self.p_base.lifetime - random_lifetime_deviation,
                            size=self.p_base.start_size,
                            surf=psurf,
                            alpha=self.p_base.start_alpha,
                            gsurf=None)
        self.particles.append(particle)
        self.particle_count += 1

    def update(self, dt):
        # first timers are updated
        self.time_elapsed += dt
        self.spawn_timer += dt
        self.blit_list.clear()
        self.glow_blit_list.clear()
        # checks wether particles are automatically added or by an event driven function or others
        if self.is_active:
            match self.p_base.spawn_type:
                case "AUTO":
                    self.__update_auto()
                case "EVENT":
                    self.__update_spawn()

        # particles that are instanced need to be updated based on the config that is given
        self.__update_particles(dt)
        return super().update(dt)

    def update_position(self, position: Vector2):
        """
        If an emitter is attached to an project its position has to be updated. This function
        should be called if for any reason the position of the emitter needs to be changed
        :param position:
        :return: None
        """
        self.position = position
        self.room_rect = pygame.Rect(self.position.x // 64 * 64, self.position.y // 64 * 64, 64, 64)

    def _get_rect_surface(self, size: int) -> pygame.Surface:
        """
        Internal method to fetch a rectangle surface of a given size.
        :param size:
        :return: pygame.Surface
        """
        if 0 <= size <= 10:
            return self._SURFACES_RECT[size - 1].copy()
        raise ValueError("Size must be between 1 and 10")

    def _get_circle_surface(self, radius: int) -> pygame.Surface:
        """
        Internal method to fetch a circle surface of a given radius.
        :param radius:
        :return: pygame.Surface
        """
        if 1 <= radius <= 10:
            return self._SURFACES_CIRCLE[radius - 1].copy()
        raise ValueError("Radius must be between 1 and 10")

    def __update_auto(self):
        if self.spawn_timer >= self.p_base.spawn_delay:
            rnd = random.randint(0, 100)
            if rnd < self.p_base.particle_chance:
                self.__spawn_particle_rate(self.p_base.spawn_rate)
                self.spawn_timer = 0

    def __update_spawn(self):
        pass

    def __update_particles(self, dt):
        # remove particles that are not inside the room
        self.particles = [p for p in self.particles if self.room_rect.collidepoint(p.position)]

        # update the remaining particles
        for particle in self.particles:
            # positional update
            if self.p_base.sin_x:
                particle.position.x += particle.direction * (
                        (math.sin(self.time_elapsed * particle.frequency + particle.phase) * 1) / 8)
            else:
                particle.position.x += particle.velocity.x * dt

            if self.p_base.sin_y:
                particle.position.y += particle.direction * (
                        (math.sin(self.time_elapsed * particle.frequency + particle.phase) * 1) / 8)
            else:
                particle.position.y += particle.velocity.y * dt

            # time update
            MIN_DT = 1 / 240
            _dt = max(dt, MIN_DT)
            particle.time_elapsed += _dt
            try:
                if particle.time_elapsed >= particle.lifetime:
                    self.particles.remove(particle)
            except ValueError as e:
                print(f"{e}: Particle already removed")

            # color size interpolation
            t = (particle.time_elapsed / particle.lifetime) ** 2
            particle.color = interpolate_color(particle.color, self.p_base.color_end, t)
            particle.size = lerp(particle.size, self.p_base.end_size, t)
            particle.alpha = lerp(particle.alpha, self.p_base.end_alpha, t)

            # after data is set, get correct surf, and mutate it accordingly to updated data
            psurf = None
            gsurf = None
            match self.p_base.particle_type:
                case "RECT":
                    psurf = self._get_rect_surface(clamp(int(particle.size), 1, 10))
                    psurf.fill(particle.color)
                    psurf.set_alpha(particle.alpha)
                    if self.p_base.glow_size > 0:
                        gsurf = self._get_rect_surface(clamp(int(particle.size + self.p_base.glow_size + random.choice(
                            [self.p_base.random_glow, -self.p_base.random_glow])), 1, 10))
                        gsurf.fill((int(particle.color.r * (particle.alpha / 255)),
                                    int(particle.color.g * (particle.alpha / 255)),
                                    int(particle.color.b * (particle.alpha / 255))))
                case "CIRCLE":
                    psurf = self._get_circle_surface(clamp(int(particle.size), 1, 10))
                    psurf.fill(particle.color)
                    psurf.set_alpha(particle.alpha)
                    if self.p_base.glow_size > 0:
                        gsurf = self._get_circle_surface(
                            clamp(int(particle.size + self.p_base.glow_size + random.choice(
                                [self.p_base.random_glow, -self.p_base.random_glow])), 1, 10))
                        gsurf.fill((int(particle.color.r * (particle.alpha / 255)),
                                    int(particle.color.g * (particle.alpha / 255)),
                                    int(particle.color.b * (particle.alpha / 255))))
                case "ANIMATION":
                    pass
            particle.surf = psurf
            particle.gsurf = gsurf
            self.blit_list.append((psurf, particle.position - self.game.world.camera.render_scroll))

    def render(self, surf: pygame.Surface, offset=(0, 0)) -> None:
        super().render(surf, offset)
        # rendering lines has unfortunately be done iteratively as they are calculated
        # at runtime based on their direction
        if self.p_base.particle_type == 'LINE':
            for p in self.particles:
                velocity_length = math.sqrt(p.velocity.x ** 2 + p.velocity.y ** 2)
                direction_x = p.velocity.x / velocity_length
                direction_y = p.velocity.y / velocity_length
                end_x = p.position.x + direction_x * p.size
                end_y = p.position.y + direction_y * p.size
                end_p = Vector2(end_x, end_y)
                pygame.draw.aaline(surf, p.color, p.position - offset, end_p - offset, 1)
        else:
            # rendering for animations, circles, rects
            surf.fblits(self.blit_list)

        # rendering glow has to be done after everything has been rendered already
        for p in self.particles:
            if p.gsurf:
                surf.blit(p.gsurf, p.position - offset, special_flags=pygame.BLEND_RGBA_ADD)
