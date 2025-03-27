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


class SimpleWorld:
    """
    A class which holds the whole Update loop and all variables, objects etc.
    """

    def __init__(self, game) -> None:
        self.screen_shake = 0
        self.screen_shake_strength = pygame.Vector2(0, 0)
        self.screen_shake_duration = 0
        self.current_cam_pos = pygame.Vector2(0, 0)
        self.previous_cam_pos = pygame.Vector2(0, 0)
        self.master_clock: float = 0.0
        self.__tile_size = 4
        self.__resource_paths = RESOURCEPATHS['rooms']
        self.entities: Manager = None
        self.content: game.content_manager = None
        self.sh_manager: SpritesheetManager = None
        self.hitbox_manager: HitboxManager = None
        self.font_manager = None
        self.textbubble_handler = None
        self.background: Background = None
        self.background_manager: BackgroundManager = None
        self.tilemap: Tilemap = None
        self.game = game
        self.scroll = [0, 0]
        self.render_scroll = [0, 0]
        self.restrict_rect = None
        self.active_room = None
        self.room_size_px = pygame.Vector2(64, 64)

    def init_world(self):
        self.content = self.game.content_manager
        self.sh_manager = self.content.get_sprite_sheet_manager()
        self.background_manager = self.content.get_background_manager()
        self.font_manager = self.content.get_font_manager()
        self.hitbox_manager = HitboxManager(self.game)
        self.entities = Manager(self.game)
        self.textbubble_handler = TextbubbleHandler(self.game, self.font_manager)
        self.tilemap = Tilemap(smanager=self.sh_manager)
        self.load_world(True)

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

        self.update_camera(dt)
        self.entities.spatial_update()
        self.hitbox_manager.update(dt)
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
        self.tilemap.render_single_surface_subsurface(surf, self.render_scroll, self.room_size_px)
        self.entities.spatial_render(surf)

    def render_ui(self, surf: pygame.Surface) -> None:
        # self.textbubble_handler.render(surf, self.render_scroll)
        pass
    def get_entity_manager(self):
        return self.entities

    def invoke_screenshake(self, duration: int, strength: pygame.Vector2):
        self.screen_shake_duration = duration
        self.screen_shake_strength = strength

    def update_camera(self, dt):
        # Camera code, maybe needs to end up in its own object once its figured out
        if self.screen_shake_duration > 0:
            self.screen_shake = pygame.Vector2(
                random.uniform(-self.screen_shake_strength.x, self.screen_shake_strength.x),
                random.uniform(-self.screen_shake_strength.y, self.screen_shake_strength.y))
            self.screen_shake_duration -= dt
        else:
            self.screen_shake = pygame.Vector2(0, 0)

        # static room camera
        prev_scroll = self.scroll.copy()

        new_scroll = [(self.entities.player.rect.centerx //
                       self.room_size_px.x) * self.room_size_px.x + self.screen_shake.x,
                      (self.entities.player.rect.centery //
                       self.room_size_px.y) * self.room_size_px.y + self.screen_shake.y
                      ]

        if prev_scroll != new_scroll:
            self.scroll[0] = lerp(self.scroll[0], new_scroll[0], 10 * dt)
            self.scroll[1] = lerp(self.scroll[1], new_scroll[1], 10 * dt)

        if self.restrict_rect:

            if self.scroll[0] + self.game.window.display.get_width() > self.restrict_rect.right:
                self.scroll[0] = self.restrict_rect.right - self.game.window.display.get_width()

            if self.scroll[0] < self.restrict_rect.left:
                self.scroll[0] = self.restrict_rect.left

            if self.scroll[1] < self.restrict_rect.top:
                self.scroll[1] = self.restrict_rect.top

            if self.scroll[1] + self.game.window.display.get_height() > self.restrict_rect.bottom:
                self.scroll[1] = self.restrict_rect.bottom - self.game.window.display.get_height()

        self.render_scroll = [int(self.scroll[0]), int(self.scroll[1])]

    def read_room_data(self, room_name):
        path = self.__resource_paths + '/' + room_name + '.json'
        f = open(path, 'r')
        room_data = json.loads(f.read())
        f.close()
        return room_data
