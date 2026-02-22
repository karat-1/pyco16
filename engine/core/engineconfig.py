# all entities that are to be instantiated need to be imported here
from engine.core.engine_core_funcs import resource_path

# defines where resources are located inside the project
RESOURCEPATHS = {
    "animations": resource_path("resources/sprites/animations"),
    "thumbnails": resource_path("resources/sprites/thumbnails"),
    "sprites": resource_path("resources/sprites"),
    "rooms": resource_path(""),
    "backgrounds": resource_path("resources/sprites/backgrounds"),
    "images": resource_path("resources/sprites/images"),
    "savegames": resource_path("resources/save"),
    "fonts": resource_path("resources/fonts"),
    "spritesheets": resource_path("resources/sprites/spritesheets"),
    "sound": resource_path("resources/sounds")
}

# defines which dataformats are supported for loading images
SUPPORTED_IMAGE_FORMATS = ["png", "jpg", "jpeg"]

# defines the framerate at which the game is allowed to run at
GLOBAL_FRAMERATE = 60

INSTANTIABLE_OBJECTS = {}
