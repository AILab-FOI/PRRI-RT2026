import pygame as pg
import time
import math
import json
import random
import sys
from Assets.settings import *
from Assets.scripts.Util.font_manager import load_custom_font, resource_path
from Assets.scripts.UI.menu import MetallicUIRenderer


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
        self.waiting_for_input = False
        self.custom_message = None
        self.use_level1_custom_image = False
        self.loading_complete = False
        self.on_complete_callback = None

        self.tips = []
        self.lore = []
        self.current_tip = ""
        self.load_tips_and_lore()

        bg_image_path = resource_path('resources/teksture/pocetna.png')
        self.bg_image = pg.image.load(bg_image_path).convert()
        self.bg_image = pg.transform.scale(self.bg_image, RES)

        self.level1_custom_image = None
        for candidate in (
            'resources/teksture/level1_loading.png',
            'resources/teksture/level1_loading.jpg',
            'resources/teksture/level1_loading.jpeg',
            'resources/teksture/level1_custom_loading.png',
        ):
            try:
                img = pg.image.load(resource_path(candidate)).convert()
                self.level1_custom_image = pg.transform.scale(img, RES)
                break
            except Exception:
                continue

        self.level1_ready_size = (1024, 512)
        self.level1_ready_image = None
        for candidate in (
            'resources/teksture/keybinds.png',
        ):
            try:
                img = pg.image.load(resource_path(candidate)).convert_alpha()
                self.level1_ready_image = pg.transform.scale(img, self.level1_ready_size)
                break
            except Exception:
                continue

        self.level1_ready_panel_padding = 24

        self.title_font = load_custom_font(60)
        self.info_font = load_custom_font(30)
        self.tip_font = load_custom_font(20)
        self.prompt_font = load_custom_font(24)

        self.text_color = (235, 235, 245)
        self.muted_text = (190, 205, 220)
        self.orange_color = (255, 140, 0)
        self.white = (235, 235, 245)

        self.circle_radius = 40
        self.circle_width = 5
        self.circle_y = HALF_HEIGHT + 105
        self.num_segments = 8

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

    def start(self, level_number=None, auto_continue=True, use_custom_level1_image=False, message=None, on_complete_callback=None):
        self.active = True
        self.start_time = time.time()
        self.level_number = level_number
        self.auto_continue = auto_continue
        self.waiting_for_input = False
        self.custom_message = message
        self.use_level1_custom_image = use_custom_level1_image and level_number == 1
        self.loading_complete = False
        self.on_complete_callback = on_complete_callback

        pg.mouse.set_visible(False)

        if random.random() < 0.5 and self.tips:
            self.current_tip = random.choice(self.tips)
        elif self.lore:
            self.current_tip = random.choice(self.lore)
        elif self.tips:
            self.current_tip = random.choice(self.tips)
        else:
            self.current_tip = ""

    def mark_loading_complete(self, message=None):
        self.loading_complete = True
        self.waiting_for_input = self.level_number == 1
        if message is not None:
            self.custom_message = message

    def update(self):
        if not self.active:
            return

        if self.waiting_for_input:
            return

        if not self.auto_continue:
            return

        if not self.loading_complete:
            return

        elapsed = time.time() - self.start_time
        if elapsed >= self.duration:
            self.active = False

    def _draw_centered_text(self, text, font, center, color):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=center)
        self.screen.blit(surf, rect)

    def _draw_bottom_right_text(self, text, font, color, margin=28):
        surf = font.render(text, True, color)
        rect = surf.get_rect(bottomright=(WIDTH - margin, HEIGHT - margin))
        panel = rect.inflate(26, 18)
        self.ui_renderer.draw_panel(panel, 10)
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
            pg.draw.arc(spinner_surface, color, arc_rect, start_angle, end_angle, self.circle_width)

        self.screen.blit(
            spinner_surface,
            (circle_center[0] - size[0] // 2, circle_center[1] - size[1] // 2)
        )

    def _draw_level1_ready_panel(self):
        if self.level1_ready_image is None:
            return

        panel_width = self.level1_ready_size[0] + self.level1_ready_panel_padding * 2
        panel_height = self.level1_ready_size[1] + self.level1_ready_panel_padding * 2
        panel_rect = pg.Rect(0, 0, panel_width, panel_height)
        panel_rect.center = (HALF_WIDTH, HALF_HEIGHT + 40)

        self.ui_renderer.draw_panel(panel_rect, 12)

        image_rect = self.level1_ready_image.get_rect(center=panel_rect.center)
        self.screen.blit(self.level1_ready_image, image_rect)

    def set_custom_message(self, message):
        self.custom_message = message

    def handle_continue_key(self, event):
        if not self.active or not self.loading_complete or not self.waiting_for_input:
            return False

        if event.type == pg.KEYDOWN and event.key == pg.K_x:
            self.active = False
            self.waiting_for_input = False
            if self.on_complete_callback:
                callback = self.on_complete_callback
                self.on_complete_callback = None
                callback()
            return True
        return False

    def draw(self):
        if not self.active:
            return

        self.update_screen_reference()

        if self.use_level1_custom_image and self.level1_custom_image is not None:
            self.screen.blit(self.level1_custom_image, (0, 0))
        else:
            self.screen.blit(self.bg_image, (0, 0))

        show_level1_ready_image = (
            self.level_number == 1 and
            self.loading_complete and
            self.level1_ready_image is not None
        )

        if not show_level1_ready_image:
            title_text = "LOADING"
            title_panel = pg.Rect(HALF_WIDTH - 240, HALF_HEIGHT - 160, 480, 72)
            self.ui_renderer.draw_panel(title_panel, 10)
            self._draw_centered_text(title_text, self.title_font, title_panel.center, self.white)

        if self.level_number is not None and not self.waiting_for_input and not show_level1_ready_image:
            level_panel = pg.Rect(HALF_WIDTH - 120, HALF_HEIGHT - 28, 240, 56)
            self.ui_renderer.draw_panel(level_panel, 8)
            self._draw_centered_text(
                f"LEVEL {self.level_number}",
                self.info_font,
                level_panel.center,
                self.text_color
            )

        if self.current_tip and not self.use_level1_custom_image and not self.waiting_for_input and not show_level1_ready_image:
            tip_rect = pg.Rect(HALF_WIDTH - 320, HALF_HEIGHT + 155, 640, 92)
            self.ui_renderer.draw_panel(tip_rect, 10)
            inner_tip_rect = tip_rect.inflate(-28, -20)
            self._draw_wrapped_text(self.current_tip, self.tip_font, self.text_color, inner_tip_rect)

        if self.custom_message and not self.waiting_for_input and not show_level1_ready_image:
            msg_panel = pg.Rect(HALF_WIDTH - 290, HEIGHT - 180, 580, 60)
            self.ui_renderer.draw_panel(msg_panel, 10)
            self._draw_centered_text(self.custom_message, self.info_font, msg_panel.center, self.white)

        if show_level1_ready_image:
            self._draw_level1_ready_panel()
            self._draw_bottom_right_text("Press X to continue", self.prompt_font, self.orange_color)
        elif self.waiting_for_input and self.loading_complete:
            self._draw_bottom_right_text("Press X to continue", self.prompt_font, self.orange_color)
        else:
            self._draw_spinner()