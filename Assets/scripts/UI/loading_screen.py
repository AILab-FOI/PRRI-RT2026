import pygame as pg
import time
import math
import json
import random
import sys
from Assets.settings import *
from Assets.scripts.Util.font_manager import load_custom_font, resource_path
from Assets.scripts.UI.menu import MetallicUIRenderer, Button


class LoadingScreen:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.ui_renderer = MetallicUIRenderer(self.screen)

        self.active = False
        self.start_time = 0
        self.duration = 3.0
        self.auto_continue = True
        self.level_number = None

        self.tips = []
        self.lore = []
        self.current_tip = ""
        self.load_tips_and_lore()

        bg_image_path = resource_path('resources/teksture/pocetna.png')
        self.bg_image = pg.image.load(bg_image_path).convert()
        self.bg_image = pg.transform.scale(self.bg_image, RES)

        self.title_font = load_custom_font(60)
        self.info_font = load_custom_font(30)
        self.tip_font = load_custom_font(20)
        self.button_font = load_custom_font(36)

        self.text_color = (235, 235, 245)
        self.muted_text = (190, 205, 220)
        self.blue_color = (0, 180, 255)
        self.orange_color = (255, 140, 0)
        self.white = (235, 235, 245)

        self.circle_radius = 40
        self.circle_width = 5
        self.circle_y = HALF_HEIGHT + 105
        self.num_segments = 8

        button_height = 60
        button_width = 300
        center_x = HALF_WIDTH - button_width // 2

        self.buttons = [
            Button(center_x, HEIGHT - 150, button_width, button_height, "Continue", font_size=36),
            Button(center_x, HEIGHT - 80, button_width, button_height, "Exit", font_size=36)
        ]

    def update_screen_reference(self):
        self.screen = self.game.screen
        self.ui_renderer.screen = self.screen

    def load_tips_and_lore(self):
        try:
            tips_path = resource_path('resources/loading_tips.json')
            with open(tips_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tips = data.get('tips', [])
                self.lore = data.get('lore', [])
        except Exception:
            self.tips = ["Press E to interact with objects."]
            self.lore = ["The ship was attacked by Vogons."]

    def start(self, level_number=None, auto_continue=True):
        self.active = True
        self.start_time = time.time()
        self.level_number = level_number
        self.auto_continue = auto_continue

        pg.mouse.set_visible(not auto_continue)

        if random.random() < 0.5 and self.tips:
            self.current_tip = random.choice(self.tips)
        elif self.lore:
            self.current_tip = random.choice(self.lore)
        elif self.tips:
            self.current_tip = random.choice(self.tips)
        else:
            self.current_tip = ""

    def handle_events(self):
        if not self.active or self.auto_continue:
            return False

        mouse_pos = pg.mouse.get_pos()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            for i, button in enumerate(self.buttons):
                button.update(mouse_pos, self.game)
                if button.is_clicked(event, self.game):
                    if i == 0:
                        self.active = False
                        return True
                    elif i == 1:
                        pg.quit()
                        sys.exit()

        return False

    def update(self):
        if not self.active:
            return

        elapsed = time.time() - self.start_time
        if elapsed >= self.duration and self.auto_continue:
            self.active = False

    def _draw_centered_text(self, text, font, center, color):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=center)
        self.screen.blit(surf, rect)

    def _wrap_text_lines(self, text, font, max_width):
        words = text.split()
        lines = []
        current = ""

        for word in words:
            test = word if not current else f"{current} {word}"
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word

        if current:
            lines.append(current)

        return lines

    def _draw_wrapped_text(self, text, font, color, rect, line_spacing=4):
        lines = self._wrap_text_lines(text, font, rect.width)
        font_h = font.get_height()
        total_h = len(lines) * font_h + max(0, len(lines) - 1) * line_spacing
        y = rect.centery - total_h // 2

        for line in lines:
            surf = font.render(line, True, color)
            line_rect = surf.get_rect(centerx=rect.centerx, y=y)
            self.screen.blit(surf, line_rect)
            y += font_h + line_spacing

    def _draw_spinner(self):
        circle_center = (HALF_WIDTH, self.circle_y)
        size = (self.circle_radius * 2 + 20, self.circle_radius * 2 + 20)
        spinner_surface = pg.Surface(size, pg.SRCALPHA)
        local_center = (size[0] // 2, size[1] // 2)
        arc_rect = pg.Rect(
            local_center[0] - self.circle_radius,
            local_center[1] - self.circle_radius,
            self.circle_radius * 2,
            self.circle_radius * 2
        )

        pg.draw.circle(
            spinner_surface,
            (40, 40, 45, 120),
            local_center,
            self.circle_radius,
            self.circle_width
        )

        rotation_speed = 220
        base_angle = (time.time() * rotation_speed) % 360
        segment_span = 360 / self.num_segments

        for i in range(self.num_segments):
            angle = base_angle - (i * segment_span)
            opacity = 255 - int(190 * (i / self.num_segments) ** 1.4)
            color = (*self.orange_color, opacity)

            start_angle = math.radians(angle)
            end_angle = math.radians(angle + segment_span * 0.72)

            pg.draw.arc(
                spinner_surface,
                color,
                arc_rect,
                start_angle,
                end_angle,
                self.circle_width
            )

        self.screen.blit(
            spinner_surface,
            (circle_center[0] - size[0] // 2, circle_center[1] - size[1] // 2)
        )

    def set_custom_message(self, message, position=None, color=None):
        if color is None:
            color = self.text_color
        if position is None:
            position = (HALF_WIDTH, HALF_HEIGHT + 300)

        message_text = self.info_font.render(message, True, color)
        message_rect = message_text.get_rect(center=position)
        self.screen.blit(message_text, message_rect)

    def draw(self):
        if not self.active:
            return

        self.update_screen_reference()
        self.screen.blit(self.bg_image, (0, 0))

        title_text = "LOADING"
        if not self.auto_continue and self.level_number is not None:
            title_text = f"LEVEL {self.level_number}"

        title_panel = pg.Rect(HALF_WIDTH - 240, HALF_HEIGHT - 160, 480, 72)
        self.ui_renderer.draw_panel(title_panel, 10)
        self._draw_centered_text(title_text, self.title_font, title_panel.center, self.white)

        if self.level_number is not None and self.auto_continue:
            level_panel = pg.Rect(HALF_WIDTH - 120, HALF_HEIGHT - 28, 240, 56)
            self.ui_renderer.draw_panel(level_panel, 8)
            self._draw_centered_text(
                f"LEVEL {self.level_number}",
                self.info_font,
                level_panel.center,
                self.text_color
            )

        if self.current_tip:
            tip_rect = pg.Rect(HALF_WIDTH - 320, HALF_HEIGHT + 155, 640, 92)
            self.ui_renderer.draw_panel(tip_rect, 10)
            inner_tip_rect = tip_rect.inflate(-28, -20)
            self._draw_wrapped_text(self.current_tip, self.tip_font, self.text_color, inner_tip_rect)

        if self.auto_continue:
            self._draw_spinner()
        else:
            buttons_bg = pg.Rect(HALF_WIDTH - 185, HEIGHT - 172, 370, 170)
            self.ui_renderer.draw_panel(buttons_bg, 10)

            mouse_pos = pg.mouse.get_pos()
            for button in self.buttons:
                button.update(mouse_pos, self.game)
                button.draw(self.screen)

        pg.display.flip()