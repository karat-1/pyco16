import logging
import json
from copy import copy, deepcopy
from engine.core.engine_core_funcs import *
from engine.core.engineconfig import SUPPORTED_IMAGE_FORMATS, GLOBAL_FRAMERATE


class AnimationManager:
    def __init__(self, path):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._animations = {}
        self.animation_path = path

    def load_animations(self):
        try:
            for character in os.listdir(self.animation_path):
                if ".py" in character:
                    continue
                self._animations[character] = AnimationData(self.animation_path + "/" + character)
        except FileNotFoundError:
            self.logger.warning("No animations in %s", self.animation_path)
        else:
            self.logger.info("Animations loaded")
    def get_animation(self, character_id, action_id):
        a: AnimationData = self._animations[character_id]
        b: Animation = a.get_animation(action_id)
        b.rewind()
        return b

    def get_animation_array(self, character_id, action_id):
        a: AnimationData = self._animations[character_id]
        b: Animation = a.get_animation(action_id)
        return b


class Animation:
    """
    A class actually holding an animation (including its data)
    """

    def __init__(self, animation_frames, animation_config):
        self.__animation_frames = animation_frames
        self.__animation_config = deepcopy(animation_config)
        self.__paused = False
        self.__current_frame = None
        self.__should_loop = self.__animation_config["loop"]
        self.__frame = 0
        self.__flip = [False, False]
        self.__calc_img()
        self.__rotation = 0
        self.__just_looped = False
        self.__done = False
        self.center_x = False
        self.center_y = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def __calc_img(self):
        img = self.__animation_frames[int(self.__frame)]
        if sum(self.__flip) != 0:
            img = pygame.transform.flip(img, *self.__flip)
        self.__current_frame = img

    def get_frames(self):
        return self.__animation_frames

    def play(self, dt):
        if not self.__paused:
            self.__frame += dt * self.__animation_config["speed"]
        if self.__frame > self.__animation_config["frames"] - 1 and self.__should_loop:
            self.__frame = 0
            self.__just_looped = True
        if self.__frame > self.__animation_config["frames"] - 1 and not self.__should_loop:
            self.__done = True
            return
        if self.__just_looped and self.__animation_config["loop"] or not self.__just_looped:
            self.__calc_img()

    def rewind(self):
        self.__just_looped = False
        self.__frame = 0

    def set_loop(self, loop: bool):
        self.__should_loop = loop

    def set_speed(self, speed):
        self.__animation_config["speed"] = speed

    def pause(self):
        self.__paused = True

    def get_center(self):
        return self.__animation_config["center"]

    def is_done(self):
        return self.__done

    def unpause(self):
        self.__paused = False

    def get_current_frame_index(self):
        return self.__frame

    def get_current_animation_frame(self):
        return self.__current_frame

    def get_offset(self):
        return self.__animation_config["offset"]


class AnimationData:
    def __init__(self, path: str, colorkey=(0, 0, 0)):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.id = path.split("/")[-1]
        self.__path = path
        self.__animations = {}
        self.__sprite_atlas = None
        self.__config = None
        self.__colorkey = colorkey
        self.__init_animation()

    def __init_animation(self):
        """
        Sets up an animation which is in the resources/animations/{CHARACTERNAME} folder.
        Each of these folders contains a single sprite atlas and a config that is either
        created by hand or by the script. Each stripe of the atlas is a single entry in the
        config as seen below. Each stripe in an atlas gets a name. the default name is default_animation
        and needs to get changed later on. Frames and Columns are identical, but for accessibility both are
        possible to adress
        :return:
        """
        for img_name in os.listdir(self.__path):
            if img_name.split(".")[-1] in SUPPORTED_IMAGE_FORMATS:
                self.__sprite_atlas = load_img(resource_path(self.__path + "/" + img_name), None, True)
        try:
            f = open(resource_path(self.__path + "/config.json"), "r")
            self.__config = json.loads(f.read())
        except FileNotFoundError:
            self.__config = {
                "default_animation": {
                    "frames": 8,
                    "columns": 8,
                    "loop": True,
                    "speed": 1.0,
                    "centered": False,
                    "offset": [0, 0],
                    "width": 16,
                    "height": 16,
                    "center": [0, 0],
                }
            }
            f = open(resource_path(self.__path + "/config.json"), "w")
            f.write(json.dumps(self.__config))
            f.close()

        y_offset = 0
        for row_coord, animatio_name in enumerate(self.__config.keys()):
            animation_frames = []

            height = self.__config[animatio_name]["height"]
            width = self.__config[animatio_name]["width"]
            frame_count = self.__config[animatio_name]["frames"]

            for column_coord in range(frame_count):
                x = width * column_coord
                y = y_offset
                rectangle = pygame.Rect(x, y, width, height)
                try:
                    img = self.__sprite_atlas.subsurface(rectangle)
                    animation_frames.append(img)
                except ValueError:
                    self.logger.warning("Image could not be found, exception handling has not been implemented")
            self.__animations[animatio_name] = Animation(animation_frames, self.__config[animatio_name])
            y_offset += height  # Add height of current animation row to offset

    def get_animation(self, animation_name):
        return copy(self.__animations[animation_name])
