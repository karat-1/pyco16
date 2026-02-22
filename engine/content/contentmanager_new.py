from engine.content.animations import AnimationManager
from engine.content.spritesheets import SpritesheetManager
from engine.content.imagemanager import ImageManager
from engine.content.background import BackgroundManager
from engine.content.fontmanager import FontManager


class ContentManager:

    def __init__(self, ctx):
        self.ctx = ctx
        self.__animations = AnimationManager(self.ctx.resource_paths.animations)
        self.__sprite_sheet_manager = SpritesheetManager(self.ctx.resource_paths.animations)
        self.__image_manager = ImageManager(self.ctx.resource_paths.animations)
        self.__background_manager = BackgroundManager(self.ctx.resource_paths.animations)
        self.__font_manager = FontManager(self.ctx.resource_paths.animations)
        self.load_assets()

    def load_assets(self):
        self.__animations.load_animations()
        self.__sprite_sheet_manager.load_spritesheets()
        self.__image_manager.load_images()
        self.__font_manager.load_images()
        self.__background_manager.load_backgrounds()

    def get_sprite_sheet_manager(self):
        return self.__sprite_sheet_manager

    def get_animation_manager(self):
        return self.__animations

    def get_background_manager(self):
        return self.__background_manager

    def get_image_manager(self):
        return self.__image_manager

    def get_image(self, name: str):
        return self.__image_manager.get_image(name)

    def get_animation(self, character_id, animation_id):
        return self.__animations.get_animation(character_id, animation_id)

    def get_animation_array(self, character_id, animation_id):
        return self.__animations.get_animation_array(character_id, animation_id)

    def get_font_manager(self):
        return self.__font_manager
