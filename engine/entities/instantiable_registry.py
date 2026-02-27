from typing import Type, Dict
from engine.entities.base.entity import Entity

INSTANTIABLE_ENTITIES: Dict[str, Type[Entity]] = {}

def Instantiable(cls: Type[Entity]) -> Type[Entity]:
    if not issubclass(cls, Entity):
        raise TypeError(f"{cls.__name__} must inherit from Entity")
    INSTANTIABLE_ENTITIES[cls.__name__] = cls
    return cls