import logging

import pygame
from pygame import Vector2 as vec2
import os
from engine.core.engine_core_funcs import load_img

PARALLAXCLASS = [0, 0.05, 0.07, 0.06, 0.85, 0.095]


class BackgroundManager:
    def __init__(self, path):
        self.__backgrounds = {}
        # this has already resource_path executed upon
        self.path = path
        self.active_background = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def load_backgrounds(self):
        try:
            for background in os.listdir(self.path):
                if ".py" in background:
                    continue
                _bg_img = load_img(self.path + "/" + background, (0, 0, 0))
                _bg = Background(_bg_img)
                _bg_name = background[:-4]
                self.__backgrounds[_bg_name] = _bg
        except FileNotFoundError:
            self.logger.warning("No backgrounds found at %s", self.path)
        else:
            self.logger.info("Backgrounds loaded")

    def update(self, dt):
        if not self.active_background:
            self.set_background()
        self.active_background.update(dt)

    def set_background(self, bg_name="default"):
        self.active_background = self.__backgrounds[bg_name]

    def render(self, surf, offset):
        self.active_background.render(surf, offset)

    def get_backgrounds(self, room_name):
        return self.__backgrounds[room_name]


class Background:
    def __init__(self, bg_img):
        self.width = 108
        self.height = 288
        self.layer_surfaces = []
        self.background_data = {}
        self.offset = (0, 0)
        self.__load_background(bg_img)

    def __load_background(self, layer_sheet: pygame.Surface):
        self.layer_surfaces = self.__sheet_to_layers(layer_sheet)
        for i, background in enumerate(self.layer_surfaces):
            # for now this position is okay, but if i like the system this location has to be passed in from outside,
            # idk how yet though. it should most likely be the center of a zone
            position = vec2(0, 15199)
            parallax_mult = PARALLAXCLASS[i]
            self.background_data[i] = [position, parallax_mult]

    def __sheet_to_layers(self, layer_sheet):
        amount_of_layers = layer_sheet.get_height() // self.height
        layers = []
        for i in range(amount_of_layers):
            subsurface = layer_sheet.subsurface(pygame.Rect(0, i * self.height, self.width, self.height))
            layers.append(subsurface)
        return layers

    def update(self, dt):
        pass

    def render(self, surf, offset):
        for i, layer in enumerate(self.layer_surfaces):
            layer_pos = self.background_data[i][0]  # Position des Layers
            parallax_factor = self.background_data[i][1]

            # Berechne den versetzten Offset für diesen Layer
            parallax_x = (layer_pos.x - offset[0]) * parallax_factor
            parallax_y = (layer_pos.y - offset[1]) * parallax_factor

            # Render-Hintergrund in einem 3x1 Grid für nahtlose X-Wiederholung
            surf.blit(layer, (parallax_x, parallax_y))
