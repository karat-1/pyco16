from dataclasses import dataclass, fields, field
from pygame import Vector2, Color
from typing import Literal


@dataclass
class ParticleBaseSettings:
    """
    This is the base dataclass for particle settings. It has default values which can be overwritten, as long
    as type safety is considered. The settings object can be passed to a particlesystem's apply_config() method
    as a parameter and it will always be applied.
    """
    spawn_rate: int = 1
    spawn_delay: float = 1
    particle_chance: float = 1.0
    color_start: Color = field(default_factory=lambda: Color(255, 255, 255, 255))
    color_end: Color = field(default_factory=lambda: Color(255, 255, 255, 255))
    gravity: float = 0.981
    sin_x: bool = False
    sin_y: bool = False
    particle_velocity_x: float = 0
    random_x_dir: bool = False
    particle_velocity_y: float = 0
    random_y_dir: bool = False
    random_velocity_deviation: float = 0.0
    lifetime: float = 1.0
    start_size: int = 1
    end_size: int = 1
    particle_type: Literal["RECT", "CIRCLE", "LINE", "ANIMATION"] = "RECT"
    spawn_type: Literal["AUTO", "EVENT"] = "AUTO"
    glow_size: int = 0
    random_glow: int = 0
    start_alpha: int = 255
    end_alpha: int = 255

    def __setattr__(self, key, value):
        allowed_fields = {f.name: f.type for f in fields(self)}

        if key not in allowed_fields:
            raise AttributeError(f"Cannot add new field '{key}' in subclass of {self.__class__.__name__}")

        object.__setattr__(self, key, value)  # Allow modifying existing fields


@dataclass
class PlayerJumpParticles(ParticleBaseSettings):
    spawn_rate: int = 1
    spawn_delay: int = 1
    particle_chance: float = 1.0
    color_start: Color = field(default_factory=lambda: Color(125, 125, 125, 255))
    color_end: Color = field(default_factory=lambda: Color(255, 255, 255, 0))
    gravity: float = 0.981
    sin_x: bool = False
    sin_y: bool = False
    particle_velocity_x: float = 15
    random_x_dir: bool = True
    random_y_dir: bool = False
    particle_velocity_y: float = -1
    random_velocity_deviation: float = 5
    lifetime: float = 1.25
    start_size: int = 3
    end_size: int = 1
    particle_type: str = "RECT"
    spawn_type: str = "EVENT"


@dataclass
class BonfireParticles(ParticleBaseSettings):
    spawn_rate: int = 2
    spawn_delay: float = 0.1
    particle_chance: float = 50
    color_start: Color = field(default_factory=lambda: Color('#9F1A00'))
    color_end: Color = field(default_factory=lambda: Color('#FFF000'))
    gravity: float = 0.981
    sin_x: bool = False
    sin_y: bool = False
    particle_velocity_x: float = 1.05
    random_x_dir: bool = True
    particle_velocity_y: float = -6.55
    random_y_dir: bool = False
    random_velocity_deviation: float = 2
    lifetime: float = 2
    start_size: int = 1
    end_size: int = 1
    particle_type: Literal["RECT", "CIRCLE", "LINE", "ANIMATION"] = "RECT"
    spawn_type: Literal["AUTO", "EVENT"] = "AUTO"
    glow_size: int = 1
    random_glow: int = 0
    start_alpha: int = 255
    end_alpha: int = 0
