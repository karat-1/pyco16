import logging

import pygame

from engine.core.tile import Tile
from pygame import Surface
import json
import csv

from engine.core.engine_core_funcs import load_img
from pathlib import Path
from typing import Optional


class EntityData:
    def __init__(self):
        self.all_entities = {}
        self.position = [0, 0]


class RoomData:
    def __init__(self, tile_size):
        self.collider_array = []
        self.tile_array = []
        self.composite_img = None
        self.position = [0, 0]
        self.width = 0
        self.height = 0
        self.__tile_size = tile_size
        self.entities = {}

    @property
    def room_bounding_box(self):
        return [self.position[0], self.position[1], self.width, self.height]

    def get_tile(self, x, y) -> Optional[Tile]:
        yi = int(y)
        xi = int(x)
        if yi < 0 or yi >= len(self.tile_array):
            return None
        row = self.tile_array[yi]
        if xi < 0 or xi >= len(row):
            return None
        return row[xi]

    def contains(self, px: int, py: int) -> bool:
        """Prüft, ob der Punkt (px,py) in diesem Room liegt (AABB)."""
        x0, y0 = self.position[0], self.position[1]
        return x0 <= px <= x0 + self.width and y0 <= py <= y0 + self.height

    def populate_tile_array(self):
        for y, row in enumerate(self.collider_array):
            row_array = []
            for x, cell in enumerate(row):
                if cell == "1":
                    # Convert room's position (pixels) to tile indices
                    room_tile_x = self.position[0] // self.__tile_size
                    room_tile_y = self.position[1] // self.__tile_size
                    # Calculate world tile indices
                    world_tile_x = room_tile_x + x
                    world_tile_y = room_tile_y + y
                    row_array.append(
                        Tile(
                            tile_size=self.__tile_size,
                            pos=pygame.Vector2(x, y),  # Local tile position (tile indices)
                            world_pos=pygame.Vector2(world_tile_x, world_tile_y),  # World tile indices
                            solid=True,
                        )
                    )
                elif cell == "0":
                    row_array.append(None)
            self.tile_array.append(row_array)

    def fix_entity_positions_to_world(self):
        """Convert entity local (x,y) to world (x,y) in-place."""
        rx, ry = self.position  # room world top-left
        for _, lst in (self.entities or {}).items():
            if not isinstance(lst, list):
                continue
            for ent in lst:
                lx = ent.get("x")
                ly = ent.get("y")
                if lx is None or ly is None:
                    continue
                ent["x"] = int(rx + lx)
                ent["y"] = int(ry + ly)  # top-left origin, Y down locally


class Tilemap:

    def __init__(self,ctx=None):
        self.ctx = ctx
        self.__tile_size: int = self.ctx.game_settings.tile_size
        self.__resource_paths = self.ctx.resource_paths.rooms
        self.__tileset_surface: Surface = None
        self.__room_data: dict[tuple[int, int], RoomData] = {}
        self.rooms_sorted_x = []
        self._rooms_x_starts = []
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def get_surround_tiles(self, world_position, radius):
        room: RoomData = self.get_room_at_point(world_position.x, world_position.y)
        # Calculate local position
        room_world_x = room.position[0]
        room_world_y = room.position[1]
        local_entity_position = (
            (int(world_position.x) - room_world_x) // self.__tile_size,
            (int(world_position.y) - room_world_y) // self.__tile_size,
        )
        rects = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                check_location = [local_entity_position[0] + dx, local_entity_position[1] + dy]
                tile = room.get_tile(check_location[0], check_location[1])
                if isinstance(tile, Tile) and tile.solid:
                    rects.append(tile)
        return rects

    def get_all_entity_data(self):
        all_entity_data = {}
        for rd in self.rooms_sorted_x:
            entity_data = EntityData()
            ents = getattr(rd, "entities", {}) or {}
            for key, lst in ents.items():
                if key not in entity_data.all_entities:
                    entity_data.all_entities[key] = []
                entity_data.all_entities[key].append(lst)
            room_key = (rd.position[0], rd.position[1], rd.width, rd.height)
            all_entity_data[room_key] = entity_data
        return all_entity_data

    def get_tile_cell(self, x: int, y: int, room_position: tuple[int, int]):
        tile = self.__room_data[room_position].get_tile(x, y)
        if tile:
            return tile

    def get_tile_cell_pixel(self, x: int, y: int) -> Tile:
        room: RoomData = self.get_room_at_point(x, y)

        # Calculate local position
        room_world_x = room.position[0]
        room_world_y = room.position[1]
        local_entity_position = ((int(x) - room_world_x) // self.__tile_size,
                                 (int(y) - room_world_y) // self.__tile_size)
        tile = room.get_tile(local_entity_position[0], local_entity_position[1])
        if tile:
            return tile

    def __reset_room(self):
        self.__tileset_surface = None
        self.__room_data = None

    def load_room_ldtk(self):
        self.__reset_room()
        self.__read_room_data_ldtk_gridvania()
        self.create_ldtk_tilemap_surface()

    def create_ldtk_tilemap_surface(self):
        self.__tileset_surface = pygame.Surface(
            (self.ctx.game_settings.world_width, self.ctx.game_settings.world_height),
            flags=pygame.SRCALPHA,
        )
        self.__tileset_surface.fill((0, 0, 0, 0))
        for rd in self.__room_data.values():
            self.__tileset_surface.blit(rd.composite_img, rd.position)

    def __read_room_data_ldtk_gridvania(self):
        base = Path(self.ctx.resource_paths.rooms)
        rooms: dict[tuple[int, int], RoomData] = {}
        room_width = self.ctx.game_settings.room_width
        room_height = self.ctx.game_settings.room_height

        # Deterministic order (level0, level1, ...)
        for folder in sorted((d for d in base.iterdir() if d.is_dir()), key=lambda p: p.name):
            room = RoomData(self.__tile_size)

            # Collision layer
            with (folder / "Collision_Layer.csv").open("r", newline="", encoding="utf-8") as f:
                self.logger.info("Level Name: %s ", folder)
                room.collider_array = list(csv.reader(f))

            # Level metadata
            with (folder / "data.json").open("r", encoding="utf-8") as f:
                level_data = json.load(f)
            room.position[0] = level_data["x"]
            room.position[1] = level_data["y"]
            room.width = level_data["width"]
            room.height = level_data["height"]
            room.entities = level_data["entities"]
            # soon more

            # Composite image
            room.composite_img = load_img(str(folder / "_composite.png"), colorkey=(24, 20, 37))

            # init the room data
            room.populate_tile_array()
            room.fix_entity_positions_to_world()

            # Calculate grid position
            grid_x = room.position[0] // room_width
            grid_y = room.position[1] // room_height
            rooms[(grid_x, grid_y)] = room

        self.__room_data = rooms
        # 2) eine Liste aller Rooms, nach x (linke Kante) sortiert
        self.rooms_sorted_x = sorted(rooms.values(), key=lambda r: r.position[0])
        # 2a) parallel eine Liste mit den x-starts (nur für bisect)
        self._rooms_x_starts = [r.position[0] for r in self.rooms_sorted_x]

    def get_room_at_point(self, px: int, py: int):
        for r in self.rooms_sorted_x:
            if r.contains(px, py):
                return r
        return None

    def render_single_surface_subsurface(self, surf: Surface, offset, room_size_px):
        try:
            surf.blit(
                self.__tileset_surface.subsurface(pygame.Rect(offset[0], offset[1], room_size_px.x, room_size_px.y)),
                (0, 0),
            )
        except ValueError as e:
            self.logger.error("Failed to render subsurface to buffer %r", e)
