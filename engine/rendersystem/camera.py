from pygame import Vector2, Rect
import random
from engine.core.engine_core_funcs import lerp
class Camera:
    def __init__(self, game, world_size: Vector2 = Vector2(1024, 512)):
        self.screen_shake = 0
        self.game = game
        self.screen_shake_strength = Vector2(0, 0)
        self.screen_shake_duration = 0
        self.current_cam_pos = Vector2(0, 0)
        self.previous_cam_pos = Vector2(0, 0)
        self.scroll = [0, 0]
        self.render_scroll = [0, 0]
        self.world_size = world_size
        self.target = None
        self.room_dimension = None

    @property
    def restrict_rect(self):
        return Rect(0, 0, self.world_size.x, self.world_size.y)

    def init_camera(self, obj_to_follow, room_dimension=Vector2(64,64)):
        self.set_target(obj_to_follow)
        self.room_dimension = room_dimension

    def set_target(self, obj_to_follow):
        self.target = obj_to_follow

    def update(self, dt: float):
        # Camera code, maybe needs to end up in its own object once its figured out
        if self.screen_shake_duration > 0:
            self.screen_shake = Vector2(
                random.uniform(-self.screen_shake_strength.x, self.screen_shake_strength.x),
                random.uniform(-self.screen_shake_strength.y, self.screen_shake_strength.y))
            self.screen_shake_duration -= dt
        else:
            self.screen_shake = Vector2(0, 0)

        # static room camera
        prev_scroll = self.scroll.copy()

        new_scroll = [(self.target.rect.centerx //
                       self.room_dimension.x) * self.room_dimension.x + self.screen_shake.x,
                      (self.target.rect.centery //
                       self.room_dimension.y) * self.room_dimension.y + self.screen_shake.y
                      ]

        if prev_scroll != new_scroll:
            self.scroll[0] = lerp(self.scroll[0], new_scroll[0], 10 * dt)
            self.scroll[1] = lerp(self.scroll[1], new_scroll[1], 10 * dt)

        if self.restrict_rect:

            if self.scroll[0] + self.game.window.display.get_width() > self.restrict_rect.right:
                self.scroll[0] = self.restrict_rect.right - self.game.window.display.get_width()

            if self.scroll[0] < self.restrict_rect.left:
                self.scroll[0] = self.restrict_rect.left

            if self.scroll[1] < self.restrict_rect.top:
                self.scroll[1] = self.restrict_rect.top

            if self.scroll[1] + self.game.window.display.get_height() > self.restrict_rect.bottom:
                self.scroll[1] = self.restrict_rect.bottom - self.game.window.display.get_height()

        self.render_scroll = [int(self.scroll[0]), int(self.scroll[1])]

    def invoke_screenshake(self, duration: float, strength: Vector2):
        self.screen_shake_duration = duration
        self.screen_shake_strength = strength