import sys
import pygame
from pygame.locals import *
from enum import StrEnum, auto
from typing import Set, Dict, Tuple, Optional

class Action(StrEnum):
    MOVE_LEFT    = auto()
    MOVE_RIGHT   = auto()
    MOVE_UP      = auto()
    MOVE_DOWN    = auto()
    JUMP         = auto()
    SHOOT        = auto()
    DASH         = auto()
    INTERACT     = auto()
    MENU         = auto()
    EDITOR_SAVE  = auto()
    EDITOR_UNDO  = auto()


class Input:
    def __init__(self, ctx):
        pygame.joystick.init()
        self.ctx = ctx
        self.joystick: Optional[pygame.joystick.Joystick] = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

        self.actions_down:     Dict[Action, bool] = {a: False for a in Action}
        self.actions_pressed:  Dict[Action, bool] = {a: False for a in Action}
        self.actions_released: Dict[Action, bool] = {a: False for a in Action}

        self.mouse_pos:    Tuple[int, int] = (0, 0)
        self.mouse_delta:  Tuple[int, int] = (0, 0)
        self.wheel:        int = 0

        self.mouse_buttons_down:    Set[int] = set()     # 1=left, 3=right, 2=middle, 4=wheel up, etc.
        self.mouse_buttons_pressed: Set[int] = set()

        self.input_method: str = "keyboard"   # "keyboard" | "gamepad" | "mouse"

        self.keyboard_bindings: Dict[Action, int] = {
            Action.MOVE_LEFT:   K_a,
            Action.MOVE_RIGHT:  K_d,
            Action.MOVE_UP:     K_w,
            Action.MOVE_DOWN:   K_s,
            Action.JUMP:        K_SPACE,
            Action.SHOOT:       K_LCTRL,
            Action.DASH:        K_LSHIFT,
            Action.INTERACT:    K_e,
            Action.MENU:        K_ESCAPE,
            Action.EDITOR_SAVE: K_F5,
            Action.EDITOR_UNDO: K_z,
        }

        self.gamepad_bindings: Dict[Action, int] = {
            Action.MOVE_LEFT:   None,
            Action.MOVE_RIGHT:  None,
            Action.MOVE_UP:     None,
            Action.MOVE_DOWN:   None,
            Action.JUMP:        0,      # A / bottom button
            Action.SHOOT:       2,      # X button
            Action.DASH:        1,      # B button
            Action.INTERACT:    3,      # Y button
            Action.MENU:        6,      # Back / Select
            Action.EDITOR_SAVE: None,
            Action.EDITOR_UNDO: None,
        }

        # D-Pad / left stick deadzone
        self.deadzone = 0.24

    def update(self):
        self.actions_pressed.clear()
        self.actions_released.clear()
        self.mouse_buttons_pressed.clear()
        self.wheel = 0

        prev_mouse = self.mouse_pos
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_delta = (self.mouse_pos[0] - prev_mouse[0],
                            self.mouse_pos[1] - prev_mouse[1])

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            # Keyboard
            if event.type == KEYDOWN:
                self.input_method = "keyboard"
                for action, key in self.keyboard_bindings.items():
                    if event.key == key:
                        if not self.actions_down[action]:
                            self.actions_pressed[action] = True
                        self.actions_down[action] = True

            elif event.type == KEYUP:
                for action, key in self.keyboard_bindings.items():
                    if event.key == key:
                        if self.actions_down[action]:
                            self.actions_released[action] = True
                        self.actions_down[action] = False

            # Mouse
            elif event.type == MOUSEBUTTONDOWN:
                self.input_method = "mouse"
                btn = event.button
                self.mouse_buttons_down.add(btn)
                self.mouse_buttons_pressed.add(btn)

            elif event.type == MOUSEBUTTONUP:
                btn = event.button
                self.mouse_buttons_down.discard(btn)

            elif event.type == MOUSEWHEEL:
                self.wheel += event.y   # +1 up, -1 down

            # Gamepad buttons
            if self.joystick and event.type == JOYBUTTONDOWN:
                self.input_method = "gamepad"
                for action, btn_idx in self.gamepad_bindings.items():
                    if btn_idx is not None and event.button == btn_idx:
                        if not self.actions_down[action]:
                            self.actions_pressed[action] = True
                        self.actions_down[action] = True

            elif self.joystick and event.type == JOYBUTTONUP:
                for action, btn_idx in self.gamepad_bindings.items():
                    if btn_idx is not None and event.button == btn_idx:
                        if self.actions_down[action]:
                            self.actions_released[action] = True
                        self.actions_down[action] = False

            # D-Pad
            if self.joystick and event.type == JOYHATMOTION:
                self.input_method = "gamepad"
                self.dpad = event.value   # (-1..1, -1..1)

        if self.joystick:
            lx = self.joystick.get_axis(0)   # left stick X
            ly = self.joystick.get_axis(1)   # left stick Y (usually inverted)

            # Simple digital movement from stick + dpad
            move_x = self.dpad[0]
            move_y = self.dpad[1]

            if abs(lx) > self.deadzone:
                move_x = 1 if lx > 0 else -1
            if abs(ly) > self.deadzone:
                move_y = 1 if ly > 0 else -1   # adjust sign if needed

            self.actions_down[Action.MOVE_LEFT]  = move_x < 0
            self.actions_down[Action.MOVE_RIGHT] = move_x > 0
            self.actions_down[Action.MOVE_UP]    = move_y < 0
            self.actions_down[Action.MOVE_DOWN]  = move_y > 0

    def down(self, action: Action) -> bool:
        return self.actions_down.get(action, False)

    def pressed(self, action: Action) -> bool:
        return self.actions_pressed.get(action, False)

    def released(self, action: Action) -> bool:
        return self.actions_released.get(action, False)

    def mouse_down(self, button: int = 1) -> bool:   # 1 = left
        return button in self.mouse_buttons_down

    def mouse_pressed(self, button: int = 1) -> bool:
        return button in self.mouse_buttons_pressed

    def get_move_direction(self) -> Tuple[float, float]:
        """For character movement, returns digital or analog."""
        if self.input_method == "gamepad" and self.joystick:
            lx = self.joystick.get_axis(0)
            ly = self.joystick.get_axis(1)
            if abs(lx) > self.deadzone or abs(ly) > self.deadzone:
                return (lx, ly)
        # Fallback to digital (WASD / arrows / dpad)
        x = (self.down(Action.MOVE_RIGHT) - self.down(Action.MOVE_LEFT))
        y = (self.down(Action.MOVE_DOWN)  - self.down(Action.MOVE_UP))
        return (x, y)