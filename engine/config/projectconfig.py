from dataclasses import dataclass
from typing import Type

from pygame import Color
from engine.core.engine_core_funcs import resource_path
from engine.entities.base.entity import Entity


@dataclass(frozen=True)
class WindowSettings:
    resoloution_scale: int = 6
    game_resolution_width: int = 208
    game_resolution_height: int = 88
    window_width: int = game_resolution_width * resoloution_scale
    window_height: int = game_resolution_height * resoloution_scale
    window_bg_color: Color = (255, 255, 255)


@dataclass(frozen=True)
class GameSettings:
    tile_size: int = 8
    room_width: int = 208
    room_height: int = 88
    rooms_x: int = 50
    rooms_y: int = 50
    world_width: int = room_width * rooms_x
    world_height: int = room_height * rooms_y


@dataclass(frozen=True)
class RenderSettings:
    pass


@dataclass(frozen=True)
class ResourcePaths:
    animations: str = resource_path("resources/sprites/animations")
    thumbnails: str = resource_path("resources/sprites/thumbnails")
    sprites: str = resource_path("resources/sprites")
    rooms: str = resource_path("resources/ldtkdata/example-project/simplified/")
    data: str = resource_path("resources/ldtkdata/example-project/simplified/World/data.json")
    backgrounds: str = resource_path("resources/sprites/backgrounds")
    images: str = resource_path("resources/sprites/images")
    savegames: str = resource_path("resources/save")
    fonts: str = resource_path("resources/fonts")
    sounds: str = resource_path("resources/sounds")

@dataclass(frozen=True)
class InstantiableEntities:
    default: Type[Entity] = Entity