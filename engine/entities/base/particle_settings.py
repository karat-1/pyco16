import pygame
from pygame import Vector2, Color
from typing import Optional

from dataclasses import dataclass, field
from typing import Literal, List, Tuple


@dataclass(frozen=True)
class SineSettings:
    """Configuration for sinusoidal movement"""
    enabled: bool = False
    amplitude: float = 8.0  # base pixel amplitude
    frequency_range: Tuple[float, float] = (0.3, 0.7)
    phase_range: Tuple[float, float] = (0.0, 6.283185)  # 0..2π
    axes: Literal["x", "y", "both"] = "both"
    independent_timing: bool = True  # use particle.time_elapsed instead of global time


@dataclass(frozen=True)
class MovementSettings:
    """How particles move - extensible for future modes"""
    mode: Literal["linear", "sine", "cubic"] = "linear"
    sine: SineSettings = field(default_factory=SineSettings)
    # Future possibilities:
    # acceleration: Optional[Vector2] = None
    # drag: float = 1.0
    # orbit_center: Optional[Vector2] = None


@dataclass
class ParticleBaseSettings:
    """
    Base configuration for all particle emitters.
    Subclass this for specific effects (fire, smoke, jump dust, background waves...)
    """
    # Spawning
    spawn_rate: int = 1
    spawn_delay: float = 1.0
    particle_chance: float = 1.0  # 0.0–1.0

    # Appearance
    color_start: Color = field(default_factory=lambda: Color(255, 255, 255, 255))
    color_end: Color = field(default_factory=lambda: Color(255, 255, 255, 255))
    start_alpha: int = 255
    end_alpha: int = 255
    start_size: int = 2
    end_size: int = 2

    # Physics / Movement
    movement: MovementSettings = field(default_factory=MovementSettings)
    velocity: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    min_velocity: float = 0
    max_velocity: float = 0
    random_x_direction: bool = False
    random_y_direction: bool = False
    velocity_deviation: float = 0.0
    gravity: float = 0.0  # positive = down

    # Lifetime & Behavior
    lifetime: float = 1.0
    particle_type: Literal["RECT", "CIRCLE", "LINE", "POINT", "POLYGON", "ANIMATION"] = "RECT"
    spawn_type: Literal["AUTO", "EVENT"] = "AUTO"

    # Effects
    glow_size: int = 0
    glow_random_variation: int = 0  # renamed for clarity

    # Future extensions (placeholders)
    texture: Optional[pygame.Surface] = None
    polygon_points: Optional[List[Vector2]] = None  # relative to particle center
