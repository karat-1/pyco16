import pygame
from pygame import Vector2 as vec2
import os
from engine.core.engineconstants import RESOURCEPATHS
from engine.core.engine_core_funcs import load_img

PARALLAXCLASS = [0, 0.1, 0.20, 0.4, 0.5, 0.7]


class BackgroundManager:
    def __init__(self):
        self.__backgrounds = {}
        self.path = RESOURCEPATHS['backgrounds']
        self.active_background = None

    def load_backgrounds(self):
        for background in os.listdir(self.path):
            if ".py" in background:
                continue
            _bg_img = load_img(self.path + '/' + background, (0, 0, 0))
            _bg = Background(_bg_img)
            _bg_name = background[:-4]
            self.__backgrounds[_bg_name] = _bg

    def update(self, dt):
        if not self.active_background:
            self.set_background()

    def set_background(self, bg_name="default"):
        self.active_background = self.__backgrounds[bg_name]

    def render(self, surf, offset):
        self.active_background.render(surf, offset)

    def get_backgrounds(self, room_name):
        return self.__backgrounds[room_name]


class Background:
    def __init__(self, bg_img):
        self.width = 192
        self.height = 128
        self.layer_surfaces = []
        self.background_data = {}
        self.offset = (0, 0)
        self.__load_background(bg_img)

    def __load_background(self, layer_sheet: pygame.Surface, offset=(0, 0)):
        self.layer_surfaces = self.__sheet_to_layers(layer_sheet)
        for i, background in enumerate(self.layer_surfaces):
            # for now this position is okay, but if i like the system this location has to be passed in from outside,
            # idk how yet though. it should most likely be the center of a zone
            position = vec2(540, 120)
            parallax_mult = PARALLAXCLASS[i]
            self.background_data[i] = [position, parallax_mult]
        self.offset = offset


    def __sheet_to_layers(self, layer_sheet):
        amount_of_layers = layer_sheet.get_height() // self.height
        layers = []
        for i in range(amount_of_layers):
            subsurface = layer_sheet.subsurface(pygame.Rect(0, i * self.height, self.width, self.height))
            layers.append(subsurface)
        return layers

    def update(self, dt, camera):
        pass

    def render(self, surf, offset):
        for i, layer in enumerate(self.layer_surfaces):
            layer_pos = self.background_data[i][0]  # Position des Layers
            parallax_factor = self.background_data[i][1]

            # Berechne den versetzten Offset für diesen Layer
            parallax_x = (layer_pos.x - offset[0]) * parallax_factor + self.offset[0]
            parallax_y = (layer_pos.y - offset[1]) * parallax_factor + self.offset[1]  # Y bleibt fix

            # Breite des Layers für das Looping
            layer_width = layer.get_width()

            # Modulo-Looping für nahtlosen Übergang auf der X-Achse
            loop_x = parallax_x % layer_width

            # Render-Hintergrund in einem 3x1 Grid für nahtlose X-Wiederholung
            for x in range(-1, 2):  # -1, 0, 1 → 3 Tiles nebeneinander
                surf.blit(layer, (loop_x + x * layer_width, parallax_y))
