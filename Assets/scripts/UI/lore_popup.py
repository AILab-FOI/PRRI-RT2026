import pygame as pg
from Assets.settings import *
from Assets.scripts.Util.font_manager import load_custom_font


class LorePopup:
    def __init__(self, game):
        self.game = game
        self.active = False
        self.message = ""
        self.message_queue = []
        self.font = load_custom_font(20)
        self.start_time = 0
        self.show_duration = 99999999

        self.box_width = int(WIDTH * 0.6)
        self.box_height = 150
        self.box_x = (WIDTH - self.box_width) // 2
        self.box_y = HEIGHT - self.box_height - 80
        self.padding = 20
        self.line_spacing = 30

    def show_message(self, message):
        self.message_queue.append(message)
        if not self.active:
            self._display_next()

    def _display_next(self):
        if not self.message_queue:
            return
        self.message = self.message_queue.pop(0)
        self.active = True
        self.start_time = pg.time.get_ticks()
        self.game.player.dialogue_mode = True

    def dismiss(self):
        self.active = False
        self.message = ""
        self.game.player.dialogue_mode = False
        if self.message_queue:
            self._display_next()

    def update(self):
        if not self.active:
            return
        

    def draw(self):
        if not self.active:
            return

        screen = self.game.screen

        msg_surface = pg.Surface((self.box_width, self.box_height), pg.SRCALPHA)
        msg_surface.fill((0, 0, 0, 200))
        screen.blit(msg_surface, (self.box_x, self.box_y))

        pg.draw.rect(screen, (255, 255, 255), (self.box_x, self.box_y, self.box_width, self.box_height), 2)

        text_start_x = self.box_x + self.padding
        max_width = self.box_width - 2 * self.padding

        words = self.message.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if self.font.size(test_line)[0] > max_width:
                lines.append(current_line)
                current_line = word + " "
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)

        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, (200, 200, 200))
            y_pos = self.box_y + self.padding + 20 + i * self.line_spacing
            screen.blit(text_surface, (text_start_x, y_pos))

        hint = self.font.render("Press E to dismiss", True, (100, 100, 100))
        hint_x = self.box_x + self.box_width - hint.get_width() - self.padding
        hint_y = self.box_y + self.box_height - hint.get_height() - self.padding
        screen.blit(hint, (hint_x, hint_y))
