import uuid
import json
import pygame

from engine.core.engineconstants import RESOURCEPATHS
from engine.core.engineconstants import INSTANTIABLE_OBJECTS
from project.player_entities.player import Player


class Manager:
    def __init__(self, game):
        self.game = game
        self.player = None
        self.__resource_paths = RESOURCEPATHS['rooms']
        self.__all_entities = []
        self.list_of_objects = {}
        self.spatial_hashmap = {}
        self.list_of_instantiable_objects = INSTANTIABLE_OBJECTS
        self.hb_manager = self.game.world.hitbox_manager
        self.runtime_added_entities = []
        self.callbacks_post_update = []

        self.init_spatialhash()

    def init_spatialhash(self):
        self.spatial_hashmap = {}
        for x in range(0, 16):  # TODO: hardcoded value muss replaced werden
            for y in range(0, 8):  # TODO: hardcoded value muss replaced werden
                chunk_location = (x, y)
                self.spatial_hashmap[chunk_location] = []

    def __create_object(self, object_class_name: str, parameter: dict, return_object=False):
        parameter['game'] = self.game
        parameter['creator'] = "Manager"
        parameter['position'] = pygame.Vector2(parameter['x'], parameter['y'])
        parameter['tile_data'] = self.game.world.tilemap
        parameter = {**parameter, **parameter['customFields']}
        instantiable_object = self.list_of_instantiable_objects[object_class_name]
        temp_obj = instantiable_object(**parameter)
        # TODO: check can be simplified
        if temp_obj.__class__.__name__ in self.list_of_instantiable_objects.keys():
            self.__add_entity(temp_obj)
            if object_class_name == "Player":
                self.player = temp_obj
        if return_object:
            return temp_obj

    def instantiate_entities(self, room_name: str):
        self.list_of_objects = {}
        self.init_spatialhash()
        self.__all_entities = []
        self.list_of_instantiable_objects = INSTANTIABLE_OBJECTS
        room_data = self.read_ldtk_room_data(room_name)
        entities_to_init = room_data['entities']  # list of entities where each project is a dict

        for entity, entity_data in entities_to_init.items():
            for ed in entity_data:
                self.__create_object(entity, ed)

        for entity in self.__all_entities:
            entity.init_entity()

    def read_room_data(self, room_name):
        path = self.__resource_paths + '/' + room_name + '.json'
        f = open(path, 'r')
        room_data = json.loads(f.read())
        f.close()
        return room_data

    def read_ldtk_room_data(self, room_name):
        # TODO: hard coded value
        path = "resources/ldtkdata/example_world/simplified/World/data.json"
        f = open(path, 'r')
        room_data = json.loads(f.read())
        f.close()
        return room_data

    def gen_player(self) -> None:
        pass

    def set_player(self, player, pos: pygame.Vector2):
        pass

    def get_player(self):
        return self.player

    def init_player(self, position: pygame.Vector2):
        self.player = Player(game=self.game,
                             position=position,
                             controllable=True,
                             size=pygame.Vector2(16, 16),
                             creator="Manager",
                             id=str(uuid.uuid4()))
        self.__add_entity(self.player)

    def update(self):
        for entity_type in self.list_of_objects:
            for i, entity in enumerate(self.list_of_objects[entity_type]):
                alive = entity.update(self.game.window.dt)
                if not alive:
                    self.list_of_objects[entity_type].pop(i)

        self.__add_runtime_added_entities()
        self.__execute_entity_callbacks()

    def __execute_entity_callbacks(self):
        for callback in self.callbacks_post_update:
            callback()
        self.callbacks_post_update.clear()

    def __add_runtime_added_entities(self):
        for entity in self.runtime_added_entities:
            self.__add_entity(entity)
        self.runtime_added_entities.clear()

    def spatial_update(self):
        # TODO: hardcoded values here
        chunk_location = self.player.get_chunk_location()
        entity_list = self.get_spatial_entities(chunk_location)
        entity_list = [entity for entity in entity_list if entity.update(self.game.window.dt)]
        for entity in entity_list[:]:
            if chunk_location != entity.get_chunk_location():
                is_leaving = entity.on_leave_chunk()
                if not is_leaving:
                    continue
                self.spatial_hashmap[entity.get_chunk_location()].append(entity)
                entity_list.remove(entity)
        self.spatial_hashmap[chunk_location] = entity_list
        self.__add_runtime_added_entities()
        self.__execute_entity_callbacks()

    def get_player(self):
        return self.player

    def get_drone(self):
        return next((entity for entity in self.__all_entities if entity.flags.is_drone), None)

    def __add_entity(self, entity):
        chunk_position = ((int(entity.rect.centerx // 64)), int((entity.rect.centery // 64)))
        self.__all_entities.append(entity)
        if entity.__class__.__name__ in self.list_of_objects.keys():
            self.list_of_objects[entity.__class__.__name__].append(entity)
            self.spatial_hashmap[chunk_position].append(entity)
        else:
            self.list_of_objects[entity.__class__.__name__] = [entity]
            self.spatial_hashmap[chunk_position].append(entity)

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

    def render(self, surf, front=False, spatial: bool = False):
        front = []
        for entity_type in self.list_of_objects:
            for entity in self.list_of_objects[entity_type]:
                if entity.render_priority:
                    front.append(entity)
                    continue
                entity.render(surf, self.game.world.render_scroll)
        for entity in front:
            entity.render(surf, self.game.world.render_scroll)

    def spatial_render(self, surf, front=False):
        front = []
        for entity in self.spatial_hashmap[self.player.get_chunk_location()]:
            if entity.render_priority:
                front.append(entity)
                continue
            entity.render(surf, self.game.world.render_scroll)
        for entity in front:
            entity.render(surf, self.game.world.render_scroll)

    def get_spatial_entities(self, chunk_location):
        return self.spatial_hashmap[chunk_location]

    def remove_all_minerblocks(self):
        for entity_list in self.spatial_hashmap.values():
            for value in entity_list:
                if value.flags.miner_rock:
                    value.destroy()
                    value.flags.collideable = False
