from dataclasses import dataclass

@dataclass
class BlockFlags:
    world: bool = True       # blocks the simulation completely
    entities: bool = True    # blocks entity updates
    camera: bool = True      # blocks camera updates
    vfx: bool = True         # blocks VFX updates
    input: bool = True       # blocks input handling