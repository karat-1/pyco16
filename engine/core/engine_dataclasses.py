from dataclasses import dataclass, field
from typing import List


@dataclass()
class ENTITYTYPES:
    default: bool = False
    player: bool = False

    def __post_init__(self):
        # asserts that the fields are only booleans
        for field_name, value in self.__dict__.items():
            if not isinstance(value, bool):
                raise ValueError(f"{field_name} has to be a boolean value, but {value} was used")


@dataclass(frozen=True)
class DEBUGCONFIG:
    player_show_collision_box: bool = False
    player_show_surround_tiles: bool = False
    player_show_wallcollider: bool = False

    def __post_init__(self):
        # asserts that the fields are only booleans
        for field_name, value in self.__dict__.items():
            if not isinstance(value, bool):
                raise ValueError(f"{field_name} has to be a boolean value, but {value} was used")


@dataclass(frozen=True)
class Dialogue:
    content: List = field(default_factory=lambda: ["default_text"])


@dataclass
class ColorPalette:
    colors: list = field(
        default_factory=lambda: [
            "#be4a2f",
            "#d77643",
            "#ead4aa",
            "#e4a672",
            "#b86f50",
            "#733e39",
            "#3e2731",
            "#a22633",
            "#e43b44",
            "#f77622",
            "#feae34",
            "#fee761",
            "#63c74d",
            "#3e8948",
            "#265c42",
            "#193c3e",
            "#124e89",
            "#0099db",
            "#2ce8f5",
            "#ffffff",
            "#c0cbdc",
            "#8b9bb4",
            "#5a6988",
            "#3a4466",
            "#262b44",
            "#181425",
            "#ff0044",
            "#68386c",
            "#b55088",
            "#f6757a",
            "#e8b796",
            "#c28569",
        ]
    )
    brown_tones: list = field(default_factory=lambda: ["#e4a672", "#b86f50", "#733e39", "#3e2731"])

    def __getitem__(self, key):
        return getattr(self, key, None)


@dataclass
class PlayerProgress:
    default: bool = True

    def __post_init__(self):
        # asserts that the fields are only booleans
        for field_name, value in self.__dict__.items():
            if not isinstance(value, bool):
                raise ValueError(f"{field_name} has to be a boolean value, but {value} was used")

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Key '{key}' not found.")


@dataclass
class CollectableProgress:
    default: bool = True

    def __post_init__(self):
        # asserts that the fields are only booleans
        for field_name, value in self.__dict__.items():
            if not isinstance(value, bool):
                raise ValueError(f"{field_name} has to be a boolean value, but {value} was used")

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Key '{key}' not found.")


@dataclass
class QuestProgress:
    default: bool = True

    def __post_init__(self):
        # asserts that the fields are only booleans
        for field_name, value in self.__dict__.items():
            if not isinstance(value, bool):
                raise ValueError(f"{field_name} has to be a boolean value, but {value} was used")

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Key '{key}' not found.")
