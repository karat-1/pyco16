import random

import pygame

from engine.core.engine_core_funcs import lerp
from engine.entities.entitymanager import Manager
from engine.entities.hitbox_manager import HitboxManager
from engine.content.spritesheets import SpritesheetManager
from engine.content.background import BackgroundManager, Background
from engine.core.tilemap import Tilemap
from engine.textsystem.textbubble import TextbubbleHandler
import json
from engine.core.engineconstants import RESOURCEPATHS
from engine.rendersystem.camera import Camera


class SimpleWorld:
    """
    A class which holds the whole Update loop and all variables, objects etc.
    """

    def __init__(self, game) -> None:
        self.master_clock: float = 0.0
        self.__tile_size = 4
        self.__resource_paths = RESOURCEPATHS['rooms']
        self.entities: Manager = None
        self.content: game.content_manager = None
        self.sh_manager: SpritesheetManager = None
        self.font_manager = None
        self.textbubble_handler = None
        self.background: Background = None
        self.background_manager: BackgroundManager = None
        self.tilemap: Tilemap = None
        self.game = game
        self.active_room = None
        self.camera = None
        self.room_size_px = pygame.Vector2(64, 64)

    def init_world(self):
        self.content = self.game.content_manager
        self.camera = Camera(self.game)
        self.sh_manager = self.content.get_sprite_sheet_manager()
        self.background_manager = self.content.get_background_manager()
        self.font_manager = self.content.get_font_manager()
        self.entities = Manager(self.game)
        self.textbubble_handler = TextbubbleHandler(self.game, self.font_manager)
        self.tilemap = Tilemap(smanager=self.sh_manager)
        self.load_world(True)
        self.camera.init_camera(self.entities.player, self.room_size_px)

    def load_world(self, generate_room: bool = False, room_name: str = 'worldmap'):
        self.active_room = room_name
        # self.background_manager.set_background(),
        self.tilemap.load_room_ldtk(room_name)
        self.entities.instantiate_entities(room_name)
        self.restrict_rect = pygame.Rect(0, 0, 1024, 512)


    def update(self) -> None:
        """
        This is the game loop. If we have new mechanics, objects or systems that need to be updated
        then this has to be done here.
        :return: Nothing
        """
        dt = self.game.window.dt
        self.background_manager.update(dt)

        self.camera.update(dt)
        self.entities.spatial_update()
        self.textbubble_handler.update(dt)
        self.master_clock += self.game.window.dt

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            self.load_world(room_name=self.active_room)

    def render(self, surf: pygame.Surface) -> None:
        """
        The world renderings function only important purpose is to render every project or object
        that is part of a level to a surface. E.g. NPCs, players, enemies, items, particles etc.
        This is the main render function which gets called from the renderer. As of right now
        the Background (e.g. everything that uses parallax is not directly part of the world and is rendered
        before the world gets blitted to the surface)
        :param surf: The surface which everything should be blit too
        :return: None
        """
        # self.background_manager.render(surf, self.render_scroll)
        self.tilemap.render_single_surface_subsurface(surf, self.camera.render_scroll, self.room_size_px)
        self.entities.spatial_render(surf, self.camera.render_scroll)

    def render_ui(self, surf: pygame.Surface) -> None:
        # self.textbubble_handler.render(surf, self.camera.render_scroll)
        pass

    def get_entity_manager(self):
        return self.entities

    def read_room_data(self, room_name):
        path = self.__resource_paths + '/' + room_name + '.json'
        f = open(path, 'r')
        room_data = json.loads(f.read())
        f.close()
        return room_data
