from engine.core.engineconstants import RESOURCEPATHS
import json
from engine.core.engine_dataclasses import PlayerProgress, CollectableProgress, QuestProgress
from dataclasses import asdict


class SaveGame:
    def __init__(self, game):
        self.game = game
        self.__path = RESOURCEPATHS['savegames']
        self.__config = None

        # progress objects
        self.__player_progress = None
        self.__collectable_progress = None
        self.__quest_progress = None

        self.load_save()

    def load_save(self):
        try:
            f = open(self.__path + '/sav.json', 'r')
            self.__config = json.loads(f.read())
            self.__player_progress = PlayerProgress(**self.__config['player_progress'])
            self.__collectable_progress = CollectableProgress(**self.__config['collectable_progress'])
            self.__quest_progress = QuestProgress(**self.__config['quest_progress'])
        except FileNotFoundError:
            self.__config = {
                'player_progress': asdict(PlayerProgress()),
                'collectable_progress': asdict(CollectableProgress()),
                'quest_progress': asdict(QuestProgress())
            }
            f = open(self.__path + '/sav.json', 'w')
            f.write(json.dumps(self.__config))
            f.close()
            self.__player_progress = PlayerProgress(**self.__config['player_progress'])
            self.__collectable_progress = CollectableProgress(**self.__config['collectable_progress'])
            self.__quest_progress = QuestProgress(**self.__config['quest_progress'])

    def save_progress(self):
        pass

    def get_player_progress(self):
        return self.__player_progress

    def get_collectable_progress(self):
        return self.__collectable_progress

    def get_quest_progress(self):
        return self.__quest_progress
