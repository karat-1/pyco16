import logging
import os

from engine.core.engine_core_funcs import load_img


class ImageManager:
    def __init__(self, path):
        self.images = {}
        self.resource_path = path
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def load_images(self):
        try:
            for img in os.listdir(self.resource_path):
                if img.split(".")[-1] == "png":
                    name = img.split(".", 1)[0]
                    _img = load_img(self.resource_path + "/" + img, (0, 0, 0))
                    self.images[name] = _img
        except FileNotFoundError:
            self.logger.warning("No images found at %s", self.resource_path)
        else:
            self.logger.info("Images loaded")

    def get_image(self, name):
        return self.images[name]
