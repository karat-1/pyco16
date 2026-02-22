import pygame
from pygame import Vector2, Rect
import random

from project.events.player_change_room import PlayerChangeRoom
from project.projectsettings import WindowSettings


class Camera:
    def __init__(self, ctx, wctx):
        self.screen_shake = 0
        self.ctx = ctx
        self.wctx = wctx
        self.screen_shake_strength = Vector2(0, 0)
        self.screen_shake_duration = 0
        self.scroll = [0, 0]
        self.render_scroll = [0, 0]
        self.target = None
        self.restrict_rect_coordinates: list[int] = [0, 0, 0, 0]  # x, y, w, h
        self.wctx.eventbus.subscribe(PlayerChangeRoom, self.on_player_change_room)
        self.screen_shake_speed = 50

    @property
    def restrict_rect(self):
        return Rect(
            self.restrict_rect_coordinates[0], self.restrict_rect_coordinates[1], self.restrict_rect_coordinates[2],
            self.restrict_rect_coordinates[3]
        )

    @property
    def viewport_rect(self) -> Rect:
        return Rect(
            self.scroll[0],
            self.scroll[1],
            WindowSettings.game_resolution_width,
            WindowSettings.game_resolution_height,
        )

    def on_player_change_room(self, event: PlayerChangeRoom):
        self.restrict_rect_coordinates = event.room_data.room_bounding_box
        print(self.restrict_rect_coordinates)

    def set_restrict_rect(self, coordinates: list[int]):
        self.restrict_rect_coordinates = coordinates

    def init_camera(self, obj_to_follow):
        self.set_target(obj_to_follow)

    def set_target(self, obj_to_follow):
        self.target = obj_to_follow

    def update(self, dt: float):
        if self.screen_shake_duration > 0:
            self.screen_shake = Vector2(
                random.uniform(-self.screen_shake_strength.x, self.screen_shake_strength.x),
                random.uniform(-self.screen_shake_strength.y, self.screen_shake_strength.y),
            )
            self.screen_shake_duration -= self.screen_shake_speed * dt
        else:
            self.screen_shake = Vector2(0, 0)

        new_scroll = [
            (self.target.position.x - (WindowSettings.game_resolution_width / 2) + self.screen_shake.x),
            self.target.position.y - (WindowSettings.game_resolution_height / 2) + self.screen_shake.y,
        ]

        self.scroll[0] = new_scroll[0]
        self.scroll[1] = new_scroll[1]

        if self.restrict_rect:
            display_w = self.ctx.window.display.get_width()
            display_h = self.ctx.window.display.get_height()

            if self.scroll[0] + display_w > self.restrict_rect.right:
                self.scroll[0] = self.restrict_rect.right - display_w

            if self.scroll[0] < self.restrict_rect.left:
                self.scroll[0] = self.restrict_rect.left

            if self.scroll[1] + display_h > self.restrict_rect.bottom:
                self.scroll[1] = self.restrict_rect.bottom - display_h

            if self.scroll[1] < self.restrict_rect.top:
                self.scroll[1] = self.restrict_rect.top

        self.render_scroll = [int(self.scroll[0]), int(self.scroll[1])]

    def invoke_screenshake(self, duration: float, strength: int):
        _strength = pygame.Vector2(strength, strength)
        self.screen_shake_duration = duration
        self.screen_shake_strength = _strength
