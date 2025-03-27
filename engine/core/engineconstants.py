# all entities that are to be instantiated need to be imported here
from engine.entities.base.wave import Wave
from engine.entities.base.rope import ParticleRope
from engine.entities.base.particle_emitter import ParticleEmitter

from project.player_entities.player import Player
from engine.entities.base.oneway_collider import OnewayCollider

# defines where resources are located inside the project
RESOURCEPATHS = {
    "animations": 'resources/sprites/animations',
    "thumbnails": 'resources/sprites/thumbnails',
    "sprites": 'resources/sprites',
    "rooms": "",
    "backgrounds": 'resources/sprites/backgrounds',
    "images": 'resources/sprites/images',
    "savegames": 'resources/save',
    "fonts": 'resources/fonts'
}

# defines which dataformats are supported for loading images
SUPPORTED_IMAGE_FORMATS = [
    'png',
    'jpg',
    'jpeg'
]

# defines the framerate at which the game is allowed to run at
GLOBAL_FRAMERATE = 60

INSTANTIABLE_OBJECTS = {"Player": Player,
                        "Wave": Wave,
                        "ParticleRope": ParticleRope,
                        "OnewayCollider": OnewayCollider,
}
