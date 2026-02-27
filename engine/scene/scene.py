import pygame

from engine.eventsystem.eventbus import EventBus
from engine.scene.scenecontext import WorldContext


class Scene:
    def __init__(self, ctx):
        self.ctx = ctx
        self.__resource_paths = self.ctx.resource_paths.rooms
        self.wctx = WorldContext()
        self.name = "default"

    def init_scene(self):
        """
        Every scenes subsystems are decided by the scene itself except for the content and an inherent event system
        They are set by default as they're key components of every scene
        """
        self.wctx.set_eventbus(EventBus())
        self.wctx.set_content(self.ctx.content)

    def load_scene(self):
        pass

    def reset_scene(self):
        pass

    def update(self):
        pass

    def enter_scene(self):
        pass

    def exit_scene(self):
        pass

    def render(self, surf: pygame.Surface):
        pass
