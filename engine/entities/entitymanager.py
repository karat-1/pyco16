import json
import logging

import pygame

from engine.entities.base.entity import Entity
from engine.entities.instantiable_registry import INSTANTIABLE_ENTITIES


class EntityRoomData:
    def __init__(self):
        self.room_key: tuple[int, int, int, int] = (0, 0, 0, 0)
        self.room_entities = []


class Manager:
    def __init__(self, ctx, wctx):
        self.ctx = ctx
        self.wctx = wctx
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.__focus_entity = None
        self.__resource_paths = self.ctx.resource_paths.rooms

        # is the actual list of all objects, ordered by inserition time
        self.__all_entities = []
        # global entities persist between spatial changes and are always updated
        self.__global_entities = []
        # holds a dict of all entities by type
        self.list_of_objects = {}
        # a hashmap which will map entities to their region
        self.spatial_hashmap = {}

        self.list_of_instantiable_objects = INSTANTIABLE_ENTITIES
        # entities that are added at runtime, this list will be added to the entity lists after update() finished
        self.runtime_added_entities = []
        # deprecated
        self.callbacks_post_update = []

    def set_focus_entity(self, entity: Entity):
        self.__focus_entity = entity

    def __create_object(self, object_class_name: str, parameter: dict):
        parameter["ctx"] = self.ctx
        parameter["wctx"] = self.wctx
        parameter["creator"] = "Manager"
        parameter["position"] = pygame.Vector2(parameter["x"], parameter["y"])
        parameter["tile_data"] = self.wctx.tilemap
        parameter = {**parameter, **parameter["customFields"]}
        instantiable_object = self.list_of_instantiable_objects[object_class_name]
        temp_obj = instantiable_object(**parameter)
        if temp_obj.__class__.__name__ in self.list_of_instantiable_objects.keys():
            self.__add_entity(temp_obj)
            return temp_obj
        else:
            return None

    def instantiate_entities(self, entities: dict):
        self.list_of_objects = {}
        self.__all_entities = []
        entities_to_init = entities
        for room_key, room_entities in entities_to_init.items():
            edr = EntityRoomData()
            edr.room_key = room_key
            self.spatial_hashmap[room_key] = edr
            for entity, entity_data in room_entities.all_entities.items():
                for ed in entity_data:
                    for e in ed:
                        self.__create_object(entity, e)

        for entity in self.__all_entities:
            entity.init_entity()

    def reset_entities(self):
        for entity in self.__all_entities:
            entity.reset_entity()

    def _find_room_key_for_point(self, x, y):
        for room_key in self.spatial_hashmap.keys():
            rx, ry, rw, rh = room_key
            if rx <= x < rx + rw and ry <= y < ry + rh:
                return room_key
        return None

    def __add_entity(self, entity):
        if entity.is_global:
            self.__global_entities.append(entity)
            self.__all_entities.append(entity)
            return

        # Find the correct room via bounding-box match
        cx = entity.rect.centerx
        cy = entity.rect.centery
        room_key = self._find_room_key_for_point(cx, cy)

        if room_key is None:
            raise ValueError(f"Entity at ({cx},{cy}) is not inside any room!")

        if entity.__class__.__name__ in self.list_of_objects.keys():
            self.list_of_objects[entity.__class__.__name__].append(entity)
            self.spatial_hashmap[room_key].room_entities.append(entity)
        else:
            self.list_of_objects[entity.__class__.__name__] = [entity]
            self.spatial_hashmap[room_key].room_entities.append(entity)

        self.__all_entities.append(entity)
        entity.init_entity()

    def read_room_data(self, room_name):
        path = self.__resource_paths + "/" + room_name + ".json"
        f = open(path, "r")
        room_data = json.loads(f.read())
        f.close()
        return room_data

    def read_ldtk_room_data(self, room_name):
        # TODO: hard coded value
        path = self.ctx.resource_paths.data
        f = open(path, "r")
        room_data = json.loads(f.read())
        f.close()
        return room_data

    @property
    def focus_entity(self):
        return self.__focus_entity

    def update(self):
        for entity_type in self.list_of_objects:
            for i, entity in enumerate(self.list_of_objects[entity_type]):
                entity.update(self.ctx.window.dt)
                if not entity.alive:
                    # TODO: I need a function that does this for the other datastructures as well
                    self.list_of_objects[entity_type].pop(i)

        self.__add_runtime_added_entities()
        self.__execute_entity_callbacks()

    def __execute_entity_callbacks(self):
        for callback in self.callbacks_post_update:
            callback()
        self.callbacks_post_update.clear()

    def __add_runtime_added_entities(self):
        for entity in self.runtime_added_entities:
            entity.init_entity()
            self.__add_entity(entity)
        self.runtime_added_entities.clear()

    def spatial_update(self, dt):
        chunk_location = self._find_room_key_for_point(self.__focus_entity.position.x, self.__focus_entity.position.y)
        entity_list = self.get_spatial_entities(self.__focus_entity.position)

        # Update with sideffect hack
        # noinspection PyStatementEffect
        entities_to_remove = [e for e in entity_list if not (e.update(dt), e.alive)[1]]

        # noinspection PyStatementEffect
        [e for e in self.__global_entities if (e.update(dt), e.alive)[1]]

        for e in entities_to_remove:
            try:
                self.spatial_hashmap[chunk_location].room_entities.remove(e)
                self.__all_entities.remove(e)
            except ValueError:
                self.logger.error(ValueError)

        new_chunk = self._find_room_key_for_point(self.__focus_entity.position.x, self.__focus_entity.position.y)
        if new_chunk != chunk_location:
            # TODO: event needs to be fired in on_leave_chunk()
            self.spatial_hashmap[chunk_location].room_entities.remove(self.__focus_entity)
            self.spatial_hashmap[new_chunk].room_entities.append(self.__focus_entity)
            chunk_location = new_chunk

        if self.__focus_entity not in self.spatial_hashmap[chunk_location].room_entities:
            self.spatial_hashmap[chunk_location].room_entities.append(self.__focus_entity)

        self.__add_runtime_added_entities()
        self.__execute_entity_callbacks()

    def __remove_entity(self, entity):
        pass

    def add_entity(self, entity):
        self.runtime_added_entities.append(entity)
        return entity

    def add_callback(self, callback):
        self.callbacks_post_update.append(callback)

    def get_all_entities(self):
        all_entities = []
        for list_of_entities in self.list_of_objects.values():
            all_entities.extend(list_of_entities)
        return all_entities

    def get_entities_by_type(self, entity_type: str):
        try:
            return self.list_of_objects[entity_type]
        except KeyError:
            return []

    def render(self, surf):
        front = []
        for entity_type in self.list_of_objects:
            for entity in self.list_of_objects[entity_type]:
                if entity.render_priority:
                    front.append(entity)
                    continue
                entity.render(surf, self.wctx.camera.render_scroll)
        for entity in front:
            entity.render(surf, self.wctx.camera.render_scroll)

    def spatial_render(self, surf, camera_offset=(0, 0)):
        front = []
        entities_to_render = self.spatial_hashmap[
            self._find_room_key_for_point(self.__focus_entity.rect.centerx, self.__focus_entity.rect.centery)
        ].room_entities.copy()
        entities_to_render.extend(self.__global_entities)
        for entity in entities_to_render:
            if entity.render_priority:
                front.append(entity)
                continue
            entity.render(surf, camera_offset)
        for entity in front:
            entity.render(surf, camera_offset)

    def get_spatial_entities(self, position) -> list:
        room_location = self._find_room_key_for_point(position[0], position[1])
        return self.spatial_hashmap[room_location].room_entities
