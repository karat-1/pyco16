import math
from dataclasses import dataclass, fields
from engine.core.engine_core_funcs import lerp, clamp

import pygame
from pygame import Vector2, Color
from engine.entities.base.entity import Entity
import random
from project.vfx.shapes.particle_presets import ParticleBaseSettings


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
        int(color1.a + (color2.a - color1.a) * t),
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
        self.flags.particle_system = True
        self.time_elapsed: float = 0
        self.parent = kwargs.get("parent", False)
        self.blit_list = []
        self.glow_blit_list = []
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
        This function is for scripting use only. It will overwrite the existing settings with a new settings
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

    def spawn_particle_group(self, amount, position=None):
        spawn_position = self.position
        if position is not None:
            spawn_position = position
        for i in range(amount):
            self.__spawn_particle(spawn_position)

    def __spawn_particle_rate(self, spawn_rate, position=None):
        spawn_position = self.position
        if position is not None:
            spawn_position = position
        for i in range(spawn_rate):
            self.__spawn_particle(spawn_position)

    def set_state(self, state: bool):
        self.is_active = state

    def __spawn_particle(self, position):
        # Spawn position (inside the emitter rect)
        rnd_x = random.randint(0, int(self.size.x))
        rnd_y = random.randint(0, int(self.size.y))
        pos = Vector2(position.x + rnd_x, position.y + rnd_y)

        # Velocity setup
        base_vel = self.p_base.velocity.copy()  # Vector2(x, y)

        # Apply random direction flipping (independent for x/y)
        if self.p_base.random_x_direction and self.p_base.random_y_direction:
            angle = random.uniform(0, 2 * math.pi)
            magnitude = random.uniform(self.p_base.min_velocity, self.p_base.max_velocity)
            base_vel = Vector2(magnitude * math.cos(angle), magnitude * math.sin(angle))
        elif self.p_base.random_x_direction:
            base_vel.x *= random.choice([-1, 1])
        elif self.p_base.random_y_direction:
            base_vel.y *= random.choice([-1, 1])

        # Apply random deviation (symmetric around base velocity)
        deviation = random.uniform(-self.p_base.velocity_deviation, self.p_base.velocity_deviation)
        vel = base_vel + Vector2(deviation, deviation)

        # Optional: small lifetime variation
        lifetime = self.p_base.lifetime
        lifetime += random.uniform(-0.2, 0.2)

        # Sine frequency & phase (still needed even in linear mode)
        frequency = random.uniform(*self.p_base.movement.sine.frequency_range)
        phase = random.uniform(*self.p_base.movement.sine.phase_range)

        # Initial surface (only for RECT/CIRCLE for now)
        psurf = None
        match self.p_base.particle_type:
            case "RECT":
                psurf = self._get_rect_surface(self.p_base.start_size)
                psurf.fill(self.p_base.color_start)
            case "CIRCLE":
                psurf = self._get_circle_surface(self.p_base.start_size)
                psurf.fill(self.p_base.color_start)
            case "LINE" | "POINT" | "POLYGON" | "ANIMATION":
                pass  # handled in render/update later

        # Create particle
        particle = Particle(
            position=pos,
            start_position=pos.copy(),
            velocity=vel,
            frequency=frequency,
            phase=phase,
            direction=1,
            color=self.p_base.color_start,
            time_elapsed=0,
            lifetime=lifetime,
            size=self.p_base.start_size,
            surf=psurf,
            alpha=self.p_base.start_alpha,
            gsurf=None,
        )

        self.particles.append(particle)
        self.particle_count += 1

    def update(self, dt):
        # first timers are updated
        self.time_elapsed += dt
        self.spawn_timer += dt
        self.blit_list.clear()
        self.glow_blit_list.clear()
        # checks wether particles are automatically added or by an eventsystem driven function or others
        if self.is_active:
            match self.p_base.spawn_type:
                case "AUTO":
                    self.__spawn_auto()
                case "EVENT":
                    self.__spawn_event()

        # particles that are instanced need to be updated based on the config that is given
        self.__update_particles(dt)
        return super().update(dt)

    def update_position(self, position: Vector2):
        """
        If an emitter is attached to an entity its position has to be updated. This function
        should be called if for any reason the position of the emitter needs to be changed
        :param position:
        :return: None
        """
        self.position = position

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

    def __spawn_auto(self):
        if self.spawn_timer >= self.p_base.spawn_delay:
            rnd = random.randint(0, 100)
            if rnd < self.p_base.particle_chance:
                self.__spawn_particle_rate(self.p_base.spawn_rate)
                self.spawn_timer = 0

    def __spawn_event(self):
        pass

    def __update_particles(self, dt: float) -> None:
        """
        Update all active particles according to current configuration.
        """

        for particle in self.particles[:]:  # [:] → safe to remove during iteration
            # Time update
            # We clamp dt to prevent extreme simulation steps
            MIN_DT = 1 / 240
            _dt = max(dt, MIN_DT)
            particle.time_elapsed += _dt

            # Early out if lifetime exceeded
            if particle.time_elapsed >= particle.lifetime:
                self.particles.remove(particle)
                continue

            # Position / Movement update
            movement = self.p_base.movement

            if movement.mode == "sine" and movement.sine.enabled:
                # Sine movement mode
                cfg = movement.sine
                # Choose time base (global or per-particle independent)
                t = particle.time_elapsed if cfg.independent_timing else self.time_elapsed
                sine_value = math.sin(t * particle.frequency + particle.phase)
                if cfg.axes in ("x", "both"):
                    particle.position.x += sine_value * cfg.amplitude
                if cfg.axes in ("y", "both"):
                    particle.position.y += sine_value * cfg.amplitude
            elif movement.mode == "cubic":
                t_progress = min(particle.time_elapsed / particle.lifetime, 1.0)
                ease_factor = (1.0 - t_progress) ** 1.5  # power curve, very popular
                particle.position += particle.velocity * _dt * ease_factor
                if self.p_base.gravity != 0:
                    particle.velocity.y += self.p_base.gravity * _dt
            else:
                # Default: linear movement + gravity
                particle.position += particle.velocity * _dt

                # Apply gravity (if any)
                if self.p_base.gravity != 0:
                    particle.velocity.y += self.p_base.gravity * _dt

            # Interpolation (color, size, alpha)
            t = (particle.time_elapsed / particle.lifetime) ** 2  # quadratic ease-out

            particle.color = interpolate_color(
                particle.color, self.p_base.color_end, t
            )
            particle.size = lerp(particle.size, self.p_base.end_size, t)
            particle.alpha = lerp(particle.alpha, self.p_base.end_alpha, t)

            # Surface / Glow preparation
            psurf = None
            gsurf = None

            current_size = clamp(int(particle.size), 1, 10)

            match self.p_base.particle_type:
                case "RECT":
                    psurf = self._get_rect_surface(current_size).copy()
                    psurf.fill(particle.color)
                    psurf.set_alpha(particle.alpha)

                    if self.p_base.glow_size > 0:
                        glow_size = clamp(
                            int(particle.size + self.p_base.glow_size +
                                random.choice([-self.p_base.glow_random_variation,
                                               self.p_base.glow_random_variation])),
                            1, 10
                        )
                        gsurf = self._get_rect_surface(glow_size).copy()
                        gsurf.fill((
                            int(particle.color.r * (particle.alpha / 255)),
                            int(particle.color.g * (particle.alpha / 255)),
                            int(particle.color.b * (particle.alpha / 255)),
                        ))

                case "CIRCLE":
                    psurf = self._get_circle_surface(current_size).copy()
                    psurf.fill(particle.color)
                    psurf.set_alpha(particle.alpha)

                    if self.p_base.glow_size > 0:
                        glow_size = clamp(
                            int(particle.size + self.p_base.glow_size +
                                random.choice([-self.p_base.glow_random_variation,
                                               self.p_base.glow_random_variation])),
                            1, 10
                        )
                        gsurf = self._get_circle_surface(glow_size).copy()
                        gsurf.fill((
                            int(particle.color.r * (particle.alpha / 255)),
                            int(particle.color.g * (particle.alpha / 255)),
                            int(particle.color.b * (particle.alpha / 255)),
                        ))

                case "LINE" | "POINT" | "POLYGON" | "ANIMATION":
                    # For now we skip surface creation for these types
                    # (LINE is drawn directly in render, others are future work)
                    pass

            particle.surf = psurf
            particle.gsurf = gsurf

            # Prepare for fast rendering (camera relative)
            if psurf is not None:
                self.blit_list.append((psurf, particle.position - self.wctx.camera.render_scroll))

    def render(self, surf: pygame.Surface, offset=(0, 0)) -> None:
        super().render(surf, offset)
        # rendering lines has unfortunately be done iteratively as they are calculated
        # at runtime based on their direction
        if self.p_base.particle_type == "LINE":
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
