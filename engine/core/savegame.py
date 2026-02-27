import json
from engine.core.engine_dataclasses import (
    PlayerProgress,
    CollectableProgress,
    QuestProgress,
)
from dataclasses import asdict


class SaveGame:
    def __init__(self, ctx):
        self.ctx = ctx
        self.__path = self.ctx.resource_paths.savegames
        self.__config = None

        # progress objects
        self.__player_progress = None
        self.__collectable_progress = None
        self.__quest_progress = None

        self.load_save()

    def load_save(self):
        try:
            f = open(self.__path + "/sav.json", "r")
            self.__config = json.loads(f.read())

        except FileNotFoundError:
            self.__config = {
                "player_progress": asdict(PlayerProgress()),
                "collectable_progress": asdict(CollectableProgress()),
                "quest_progress": asdict(QuestProgress()),
            }
            f = open(self.__path + "/sav.json", "w")
            f.write(json.dumps(self.__config))
            f.close()


    def save_progress(self):
        pass
