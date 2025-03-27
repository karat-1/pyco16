import pygame

from engine.core.tile import Tile
from engine.core.engineconstants import RESOURCEPATHS
from pygame import Surface
import json
from pygame import Vector2 as Vec2
import os
import csv
from engine.core.engine_core_funcs import load_img

SURROUND_POS = [
    [0, 0],  # SAME
    [1, 0],  # RIGHT
    [0, 1],  # BELOW
    [1, 1],  # DOWN RIGHT
    [-1, 0],  # LEFT
    [1, -1],  # ABOVE RIGHT
    [-1, 1],  # DOWN LEFT
    [0, -1],  # ABOVE
    [-1, -1]]  # ABOVE LEFT

DOUBLE_SURROUND = [[0, 2],
                   [2, 1],
                   [-2, 0],
                   [-2, 1],
                   [-2, 2],
                   [1, -2],
                   [0, -2],
                   [-1, -2],
                   [-1, 2],
                   [2, 0],
                   [1, 2]]


class Tilemap:

    def __init__(self, *args, **kwargs):
        self.__width = 0
        self.__height = 0
        self.__tile_size: int = 4
        self.__spritesheetmanager = kwargs.get('smanager')
        self.__tile_data = {
            'layer': [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}],
            'decals': [],
            'tile_size': self.__tile_size,
            'width': 128,
            'height': 128

        }
        self.__tileset: list[Surface] = kwargs.get('tileset')
        self.__render_chunks = []
        self.__chunk_size = 8
        self.__resource_paths = RESOURCEPATHS['rooms']
        self.__default_layer = 4
        self.__tileset_surface: Surface = None

    def get_surround_tiles(self, position: Vec2):
        tile_position = (int(position.x // self.__tile_size), int(position.y // self.__tile_size))
        rects = []
        for p in SURROUND_POS + DOUBLE_SURROUND:
            check_location = [tile_position[0] + p[0], tile_position[1] + p[1]]
            tile = (self.get_tile_cell(check_location[0], check_location[1]))
            if isinstance(tile, Tile):
                if tile.solid:
                    rects.append(self.get_tile_cell(check_location[0], check_location[1]))
        return rects

    def get_surround_tiles_new(self, position, radius):
        _position = position // self.__tile_size
        rects = []
        for y in range(-radius, radius + 1):
            for x in range(-radius, radius + 1):
                check_location = [_position.x + x, _position.y + y]
                tile = self.get_tile_cell(check_location[0], check_location[1])
                if isinstance(tile, Tile):
                    if tile.solid:
                        rects.append(tile)
        return rects

    def get_tile_cell(self, x: int, y: int, layer: int = 0):
        if (x, y) in self.__tile_data['layer'][layer]:
            tile = self.__tile_data['layer'][layer][(x, y)]
            if tile:
                return tile

    def get_tile_cell_pixel(self, x: int, y: int, layer: int = 0):
        _x = x // self.__tile_size
        _y = y // self.__tile_size
        if (_x, _y) in self.__tile_data['layer'][layer]:
            tile = self.__tile_data['layer'][layer][(_x, _y)]
            if tile:
                return tile

    def add_tile_cell(self, x: int, y: int, layer: int = 4, tile: Tile = None):
        pass

    def add_tile(self, tile: Tile):
        self.__tile_data['layer'][tile.layer][(int(tile.position.x), int(tile.position.y))] = tile

    def __reset_room(self):
        self.__tile_data = {
            'layer': [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}],
            'decals': [],
            'tile_size': self.__tile_size,
            'width': 128,
            'height': 128

        }
        self.__render_chunks = []

    def autotile(self):
        for i, layer in enumerate(self.__tile_data["layer"]):
            for tile in list(layer.values()):
                if tile:
                    tile.simple_autotile(layer=i)

    def load_room_ogmo(self, room_name: str):
        self.__reset_room()
        room_data = self.read_room_data(room_name)
        self.__height = room_data['height'] // self.__tile_size
        self.__width = room_data['width'] // self.__tile_size
        for layer in room_data['layers']:
            if 'Layer' in layer['name']:
                data2d = layer["data2D"]
                for y, row in enumerate(data2d):
                    for x, column in enumerate(row):
                        tile_index = data2d[y][x]
                        if tile_index == -1:
                            continue
                        tilesheet = self.__spritesheetmanager.get_spritesheet(layer['tileset'])
                        temp_tile = Tile(tile_size=layer['gridCellWidth'],
                                         pos=pygame.Vector2(x, y),
                                         solid=True,
                                         destructable=False,
                                         tileset_name=layer['tileset'],
                                         tile_list=tilesheet,
                                         tile_index=tile_index,
                                         tilemap=self,
                                         scalar=pygame.Vector2(4, 4),
                                         layer=int(layer['name'][-2:]))
                        self.__tile_data['layer'][temp_tile.layer][
                            (temp_tile.position.x, temp_tile.position.y)] = temp_tile
        # self.autotile()
        self.create_tilemap_surface()

    def load_room_ldtk(self, room_name: str):
        self.__reset_room()
        room_data = self.read_room_data_ldtk(room_name)
        self.__height = 512 // self.__tile_size
        self.__width = 1024 // self.__tile_size
        layers = room_data['layers']
        img = room_data['composite_img']
        int_layer = 0
        for layer_name, layer in layers.items():
            if layer_name != "Tile_Layer_04":
                continue
            for y, row in enumerate(layer):
                for x, column in enumerate(row):
                    tile_index = layer[y][x]
                    if tile_index == "0":
                        continue
                    temp_tile = Tile(tile_size=self.__tile_size,
                                     pos=pygame.Vector2(x, y),
                                     solid=True,
                                     destructable=False,
                                     tileset_name="default",
                                     tilemap=self,
                                     scalar=pygame.Vector2(4, 4),
                                     layer=layer_name)
                    self.__tile_data['layer'][int_layer][
                        (int(temp_tile.position.x), int(temp_tile.position.y))] = temp_tile
            int_layer += 1
        self.create_ldtk_tilemap_surface(img, room_data['surf_layers'])

    def create_ldtk_tilemap_surface(self, composite_img: pygame.Surface, surf_layers: list[pygame.Surface]):
        self.__tileset_surface = pygame.Surface(
            (self.__width * self.__tile_size, (self.__height + 1) * self.__tile_size), flags=pygame.SRCALPHA)
        self.__tileset_surface.fill((0, 0, 0, 0))
        for surf_layer in surf_layers:
            surf_layer.set_colorkey((0, 0, 0))
            self.__tileset_surface.blit(surf_layer, (0, 0))

    def read_room_data(self, room_name):
        path = self.__resource_paths + '/' + room_name + '.json'
        f = open(path, 'r')
        room_data = json.loads(f.read())
        f.close()
        return room_data

    def read_room_data_ldtk(self, room_name):
        # TODO: hardcoded value
        path = "resources/ldtkdata/example_world/simplified/World"
        ldtk_dict = {"layers": {}, "composite_img": None, "surf_layers": []}
        for file_name in os.listdir(path):
            file_path = os.path.join(path, file_name)
            if file_name.endswith(".csv"):
                try:
                    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                        reader = csv.reader(csvfile)
                        # Convert the reader object to a list of rows
                        csv_data = list(reader)
                        # Append the resources to the list
                        ldtk_dict['layers'][file_name[:-4]] = csv_data
                        print(f"Collision Layer: {file_name}")
                except Exception as e:
                    print(f"Error reading {file_name}: {e}")
            if file_name.endswith(".png"):
                if file_name == "_composite.png":
                    img = load_img(file_path)
                    ldtk_dict['composite_img'] = img
                elif not file_name[:-4].endswith("int") and file_name[:-4] != "_bg" and not file_name[
                                                                                            :-4] == "Tile_Layer_04":
                    print(file_name[:-4])
                    ldtk_dict["surf_layers"].append(load_img(file_path))

        return ldtk_dict

    def create_tilemap_surface(self):
        self.__tileset_surface = pygame.Surface(
            (self.__width * self.__tile_size, (self.__height + 1) * self.__tile_size), flags=pygame.SRCALPHA)
        self.__tileset_surface.fill((0, 0, 0, 0))
        for index, layer in enumerate(self.__tile_data['layer']):
            if index in [3, 4]:
                continue
            for tile in list(layer.values()):
                t = tile.image
                t.set_colorkey((0, 0, 0))
                self.__tileset_surface.blit(t, tile.pixel_position)

    def render_tiles_blit(self, surf, offset=pygame.Vector2(0, 0)):
        for index, layer in enumerate(self.__tile_data['layer']):
            if index in [3, 4]:
                continue
            for tile in list(layer.values()):
                tile.set_tile_index(15)
                surf.blit(tile.image, tile.pixel_position - offset)

    def render_single_surface(self, surf: Surface, offset):
        surf.blit(self.__tileset_surface, (0, 0))

    def render_single_surface_subsurface(self, surf: Surface, offset, room_size_px):
        surf.blit(self.__tileset_surface.subsurface(pygame.Rect(offset[0], offset[1], room_size_px.x, room_size_px.y)),
                  (0, 0))
