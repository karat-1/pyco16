import pygame
from pygame import Surface as Surface
from pygame import Vector2 as Vec2
from pygame import Rect as Rect
import random


class Tile:
    """
    The Tile Object holding all necessary information regarding the tiles in this game

    """

    def __init__(
            self,
            tile_size: int = 4,
            pos: Vec2 = (0, 0),
            solid: bool = True,
            destructable: bool = False,
            world_pos: Vec2 = Vec2(0, 0)
    ):
        """
        :param tile_size: the pixel size of a tile
        :param pos: the tuple position of a tile
        :param solid: wether a tile is collideable or not
        :param destructable: wether a tile is destructable or not
        :param layer: a reference to the layer the tile should be on
        :param tileset_name: a name for the tileset so the correct tileset can be accessed during rendering
        :param tile_index: the tileset index so the correct sprite from the tileset can be accessed during rendering
        :param tile_type: a type definition of a tile as string
        :param color: a color for debugging purposes. grey by tilesetDefault
        """
        self.tile_size: int = tile_size
        self.size = pygame.Vector2(self.tile_size, self.tile_size)
        self.position: Vec2 = pos
        self.pixel_position: Vec2 = Vec2(pos.x * tile_size, pos.y * tile_size)
        self.world_position = world_pos
        self.world_pixel_position = Vec2(world_pos.x * tile_size, world_pos.y * tile_size)
        self.solid: bool = solid
        self.destructable: bool = destructable
        self.neighbours: list[Tile] = []

    @property
    def rect(self) -> Rect:
        """
        :return: the tiles rectangle
        """
        return Rect(
            self.world_position.x * self.tile_size,
            self.world_position.y * self.tile_size,
            self.tile_size,
            self.tile_size,
        )

    def add_neighbour(self, neighbour) -> None:
        """
        Takes in a tile object and appends the neighbour list of this tile object
        :param neighbour: a tile object
        :return: Nothing
        """
        self.neighbours.append(neighbour)

    def clear_neighbours(self) -> None:
        """
        Clears the neighbours list
        :return:
        """
        self.neighbours.clear()

    def render(self, surf, offset: Vec2):
        rect = Rect(
            self.pixel_position.x - offset.x,
            self.pixel_position.y - offset.y,
            self.tile_size,
            self.tile_size,
        )
        pygame.draw.rect(surf, (255, 0, 0), rect, 1)
