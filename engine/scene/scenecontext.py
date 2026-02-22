class FrozenWorldContextError(AttributeError):
    pass


class WorldContext:
    """
    Holds all world-level state and systems that are *project/game specific*.
    Works like GameContext: setters + freeze + read-only properties.
    """

    __slots__ = (
        "_frozen",
        "_entities",
        "_content",
        "_spritesheets",
        "_backgrounds",
        "_fonts",
        "_tilemap",
        "_camera",
        "_game_manager",
        "_textbubbles",
        "_active_room",
        "_player",
        "_gradient",
        "_eventbus",
        "_vfx_manager"
    )

    def __init__(self):
        self._frozen = False

        # world systems
        self._entities = None
        self._content = None
        self._spritesheets = None
        self._backgrounds = None
        self._fonts = None
        self._tilemap = None
        self._camera = None
        self._game_manager = None
        self._textbubbles = None
        self._eventbus = None
        self._vfx_manager = None

        # world state
        self._active_room = None
        self._player = None
        self._gradient = None

    # ----------------------------------------------------------------------
    # Internal safety
    # ----------------------------------------------------------------------

    def _assign(self, attr, value):
        if self._frozen and getattr(self, attr) is not None:
            raise FrozenWorldContextError(f"Cannot modify '{attr}' after world context is frozen")
        object.__setattr__(self, attr, value)

    # ----------------------------------------------------------------------
    # Properties + setters
    # ----------------------------------------------------------------------

    @property
    def entities(self): return self._entities

    def set_entities(self, m): self._assign("_entities", m)

    @property
    def content(self): return self._content

    def set_content(self, c): self._assign("_content", c)

    @property
    def spritesheets(self): return self._spritesheets

    def set_spritesheets(self, s): self._assign("_spritesheets", s)

    @property
    def backgrounds(self): return self._backgrounds

    def set_backgrounds(self, b): self._assign("_backgrounds", b)

    @property
    def fonts(self): return self._fonts

    def set_fonts(self, f): self._assign("_fonts", f)

    @property
    def tilemap(self): return self._tilemap

    def set_tilemap(self, t): self._assign("_tilemap", t)

    @property
    def camera(self): return self._camera

    def set_camera(self, cam): self._assign("_camera", cam)

    @property
    def game_manager(self): return self._game_manager

    def set_game_manager(self, gm): self._assign("_game_manager", gm)

    @property
    def textbubbles(self): return self._textbubbles

    def set_textbubbles(self, tb): self._assign("_textbubbles", tb)

    @property
    def eventbus(self): return self._eventbus

    def set_eventbus(self, eb): self._assign("_eventbus", eb)

    @property
    def vfx_manager(self): return self._vfx_manager

    def set_vfx_manager(self, vfxm): self._assign("_vfx_manager", vfxm)

    # ----------------------------------------------------------------------
    # World state
    # ----------------------------------------------------------------------

    @property
    def active_room(self): return self._active_room

    def set_active_room(self, room): self._assign("_active_room", room)

    @property
    def player(self): return self._player

    def set_player(self, player): self._assign("_player", player)

    @property
    def gradient(self): return self._gradient

    def set_gradient(self, g): self._assign("_gradient", g)

    # ----------------------------------------------------------------------

    def freeze(self):
        self._frozen = True
