import pygame
from engine.core.engine_dataclasses import Dialogue


class TextbubbleHandler:
    def __init__(self, game, font_manager):
        self.game = game
        self.font_manager = font_manager
        self.textbubbles: list[Textbubble] = []

    def update(self, dt):
        for bubble in self.textbubbles:
            bubble.update(dt)

        self.textbubbles = [bubble for bubble in self.textbubbles if bubble.alive]

    def create_textbubble(self, position, dialogue, size):
        _tmp = Textbubble(self.game, position, dialogue, size)
        self.textbubbles.append(_tmp)
        return self.textbubbles[-1]

    def render(self, surf, offset):
        for bubble in self.textbubbles:
            bubble.render(surf, offset, self.font_manager.get_font())


class Textbubble:
    def __init__(self, game, position, dialogue: Dialogue, size):
        self.game = game

        self.position = position
        self.size = size
        self.word_gap = 3

        # bubble and text logic
        self.dialogue = dialogue.content
        self.diaologue_index = 0
        self.hidden = True
        self.alive = True
        self.typing_cooldown = 50
        self.typing_timer = 0
        self.typing_progress = 0
        self.typing_finished = False
        self.text_to_display = ""

    def show_bubble(self):
        self.hidden = False

    def close_bubble(self):
        self.alive = False

    def progress_dialogue(self):
        self.diaologue_index += 1
        self.text_to_display = ""
        self.typing_finished = False
        self.typing_progress = 0

    def dialogue_finished(self):
        return self.diaologue_index == len(self.dialogue)

    def is_active_line_finished(self) -> bool:
        return len(self.text_to_display) == len(self.dialogue[self.diaologue_index])

    def skip_typing(self):
        self.text_to_display = self.dialogue[self.diaologue_index]
        self.typing_finished = True
        self.typing_progress = len(self.dialogue[self.diaologue_index]) - 1

    def update(self, dt):
        if self.typing_timer < self.typing_cooldown:
            self.typing_timer += dt
        elif self.typing_timer > self.typing_cooldown:
            self.typing_timer = 0
            if self.typing_finished:
                return
            elif self.typing_progress > len(self.dialogue[self.diaologue_index]) - 1:
                self.typing_finished = True
            else:
                self.text_to_display += self.dialogue[self.diaologue_index][self.typing_progress]
                self.typing_progress += 1

    def render(self, surf: pygame.Surface, offset, font: dict):
        x_offset = 5 * 3
        y_offset = 5 * 3
        textbox_surf = pygame.Surface(
            (
                self.game.window.window_resolution[0] // 2,
                self.game.window.window_resolution[1] // 3,
            )
        )
        for char in self.text_to_display:
            if char != " ":
                textbox_surf.blit(
                    pygame.transform.scale_by(font[char], (3, 3)),
                    (0 + x_offset, 0 + y_offset),
                )
                x_offset += 4 * 3
            else:
                x_offset += self.word_gap * 3
        x_pos = (self.position.x - offset[0]) * 8
        y_pos = (self.position.y - offset[1]) * 8
        surf.blit(textbox_surf, (x_pos, y_pos))
