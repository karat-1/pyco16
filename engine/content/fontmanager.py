import pygame

from engine.core.engine_core_funcs import load_img
import os


class FontManager:
    def __init__(self, path):
        self.__path = path
        self.__fonts = {}
        self.__font_order = [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Y",
            "Z",
            "!",
            "?",
            ".",
        ]
        self.char_width = 5
        self.char_height = 5

    def load_images(self):
        for img in os.listdir(self.__path):
            if img.split(".")[-1] == "png":
                name = img.split(".", 1)[0]
                self.__fonts[name] = {}
                _font_img = load_img(self.__path + "/" + img, (0, 0, 0))
                for i in range(len(self.__font_order)):
                    subsurf = _font_img.subsurface(
                        pygame.Rect(i * self.char_width, 0, self.char_width, self.char_height)
                    )
                    self.__fonts[name][self.__font_order[i]] = subsurf

    def get_surface(self, char):
        return self.__fonts["base"][char]

    def get_font(self):
        return self.__fonts["base"]
