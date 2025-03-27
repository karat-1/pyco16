from typing import Union

import pygame
from pygame import Vector2
from engine.entities.base.entity import Entity
from engine.core.tile import Tile


class Actor(Entity):
    def __init__(self, game, position: Vector2, controllable: bool = False, *args, **kwargs):
        super().__init__(game, position, controllable, *args, **kwargs)
        self.hurt: int = 0
        self.max_health: int = 1
        self.health: int = self.max_health
        self.tile_data = kwargs.get('tile_data')
        self.tiles: list[Tile] = []
        self.on_ground: bool = False
        self.on_oneway: bool = False
        self.debug = True
        self.requests = {}
        self.flags.actor = 1
        self.on_wall_right = False
        self.on_wall_left = False

    @property
    def ground_check(self) -> pygame.Rect:
        return pygame.Rect(self.position.x, self.position.y, self.img.get_width(), self.img.get_height() + 1)

    def destroy(self):
        if self.health <= 0:
            self.alive = 0

    def damage(self, amount=1, **kwargs):
        self.health -= amount
        if self.flags.destroys_itself:
            self.destroy()

    def add_request(self):
        pass

    def move(self, dt: float) -> dict:
        """
        This function moves the project object and returns a dictionary containing the info of which side collided with a collider object
        :param dt: deltaTime as float
        :return: A dictionary of collision types as specified 2 lines below
        """
        collision_types = {'top': False, 'bottom': False, 'left': False, 'right': False, 'oneway': False}
        self.tiles.clear()
        self.tiles = self.tile_data.get_surround_tiles_new(self.center, 2)
        entity_colliders = self.em.get_spatial_entities(self.get_chunk_location())
        oneway_colliders = [entity for entity in entity_colliders if entity.flags.oneway_collider]
        collideable_entities = [entity for entity in entity_colliders if entity.flags.collideable]
        self.tiles.extend(collideable_entities)

        if self.velocity.y < self.velocity.x:
            self.vertical_collision_check(collision_types, dt)
            self.horizontal_collision_check(collision_types, dt)
        else:
            self.horizontal_collision_check(collision_types, dt)
            self.vertical_collision_check(collision_types, dt)

        if len(self.tiles) > 0:
            for tile in self.tiles:
                new_rect = pygame.Rect(self.position.x, self.position.y + 1, self.size.x, self.size.y)
                if tile.rect.colliderect(new_rect):
                    self.on_ground = True
                    break
                else:
                    self.on_ground = False
            for tile in self.tiles:
                wall_rect_left = pygame.Rect(self.position.x - 1, self.position.y, 2, self.size.y)
                wall_rect_right = pygame.Rect(self.rect.right - 1, self.position.y, 2, self.size.y)
                if tile.rect.colliderect(wall_rect_left):
                    self.on_wall_left = True
                    break
                elif tile.rect.colliderect(wall_rect_right):
                    self.on_wall_right = True
                    break
                else:
                    self.on_wall_right = False
                    self.on_wall_left = False
        else:
            self.on_ground = False
            self.on_oneway = False

        if self.flags.player:
            if self.velocity[1] >= 0:
                self.on_oneway = False
                for tile in oneway_colliders:
                    new_rect = pygame.Rect(self.position.x, self.position.y, self.size.x, self.size.y + 1)
                    if tile.rect.colliderect(new_rect):
                        if self.rect.bottom - tile.rect.top < 2:
                            self.position.y = tile.rect.top - self.rect.height
                            self.velocity.y = 0
                            collision_types['oneway'] = True
                            self.on_ground = True
                            self.on_oneway = True
                            break

        return collision_types

    def vertical_collision_check(self, collision_types, dt):
        self.position.y += self.velocity.y * dt
        for tile in self.tiles:
            if self.velocity.y > 0:
                if tile.rect.colliderect(pygame.Rect(self.position.x, self.position.y + 1, self.size.x, self.size.y)):
                    self.position.y = tile.rect.top - self.rect.height
                    self.velocity.y = 0
                    collision_types['bottom'] = True
                    break
            elif self.velocity.y < 0:
                if tile.rect.colliderect(self.rect):
                    self.position.y += tile.rect.bottom - self.rect.top
                    self.velocity.y = 0
                    collision_types['top'] = True
                    break

    def horizontal_collision_check(self, collision_types, dt):
        self.position.x += self.velocity.x * dt
        if self.velocity.x != 0:
            for tile in self.tiles:
                if self.velocity.x > 0:
                    if tile.rect.colliderect(self.rect):
                        self.position.x = tile.rect.left - self.rect.width
                        self.velocity.x = 0
                        collision_types['right'] = True
                        break
                elif self.velocity.x < 0:
                    if tile.rect.colliderect(self.rect):
                        self.position.x = tile.rect.right
                        self.velocity.x = 0
                        collision_types['left'] = True
                        break

    def update(self, dt) -> Union[bool, None]:
        r = super().update(dt)
        if self.hurt:
            self.hurt = max(0, self.hurt - dt * 3)
        if self.alive:
            return True

    def check_water_collisions(self):
        water_objs = self.em.get_entities_by_type('Wave')
        for wave in water_objs:
            wave.set_impact(self)

    def check_rope_collisions(self):
        rope_objs = self.em.get_spatial_entities(self.get_chunk_location())
        rope_objs = [rope for rope in rope_objs if rope.flags.rope]
        for rope in rope_objs:
            rope.set_impact(self)


    def render(self, surf: pygame.Surface, offset=(0, -8)) -> None:
        super().render(surf, offset)
