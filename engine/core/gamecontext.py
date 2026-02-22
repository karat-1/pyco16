class GameContext:
    def __init__(self):
        # initialize in __init__
        self._frozen = False

        # Core engine services
        self._window = None
        self._input = None
        self._sound = None
        self._content = None
        self._renderer = None
        self._savegame = None
        self._scene_manager = None
        self._global_events = None

        # Config dataclasses
        self._window_settings = None
        self._game_settings = None
        self._resource_paths = None

    def __setattr__(self, name, value):
        if getattr(self, "_frozen", False) and hasattr(self, name):
            raise AttributeError(f"Cannot modify '{name}' after context initialization")
        super().__setattr__(name, value)

    # -------------------- Services --------------------
    @property
    def window(self):
        return self._window

    def set_window(self, window):
        self._window = window

    @property
    def input(self):
        return self._input

    def set_input(self, input_):
        self._input = input_

    @property
    def content(self):
        return self._content

    def set_content(self, content):
        self._content = content

    @property
    def renderer(self):
        return self._renderer

    def set_renderer(self, renderer):
        self._renderer = renderer

    @property
    def savegame(self):
        return self._savegame

    def set_savegame(self, sg):
        self._savegame = sg

    @property
    def sound(self):
        return self._sound

    def set_sound(self, sg):
        self._sound = sg

    @property
    def scene_manager(self):
        return self._scene_manager

    def set_scene_manager(self, sm):
        self._scene_manager = sm

    @property
    def global_events(self):
        return self._global_events

    def set_global_eventmanager(self, ge):
        self._global_events = ge

    # -------------------- Configs --------------------
    @property
    def window_settings(self):
        return self._window_settings

    def set_window_settings(self, ws):
        self._window_settings = ws

    @property
    def game_settings(self):
        return self._game_settings

    def set_game_settings(self, gs):
        self._game_settings = gs

    @property
    def resource_paths(self):
        return self._resource_paths

    def set_resource_paths(self, rp):
        self._resource_paths = rp

    # -------------------- Freeze --------------------
    def freeze(self):
        self._frozen = True