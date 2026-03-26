import pygame as pg
import time
import math
import json
import random
import sys
from settings import *
from scripts.Util.font_manager import load_custom_font, resource_path
from scripts.UI.menu import MetallicUIRenderer, Button

class LoadingScreen:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.active = False
        self.start_time = 0
        self.duration = 3.0
        self.auto_continue = True

        self.tips = []
        self.lore = []
        self.current_tip = ""
        self.load_tips_and_lore()

        bg_image_path = resource_path('resources/teksture/pocetna.png')
        self.bg_image = pg.image.load(bg_image_path)
        self.bg_image = pg.transform.scale(self.bg_image, RES)

        self.title_font = load_custom_font(60)
        self.info_font = load_custom_font(30)
        self.tip_font = load_custom_font(20)

        self.circle_radius = 40
        self.circle_width = 4
        self.circle_y = HALF_HEIGHT + 100
        self.num_segments = 8

        self.text_color = (220, 220, 255)
        self.circle_color = (255, 140, 0)
        self.circle_bg_color = (40, 40, 45, 80)

        self.ui_renderer = MetallicUIRenderer(self.screen)

        button_height = 60
        button_width = 300
        center_x = HALF_WIDTH - button_width // 2

        self.buttons = [
            Button(center_x, HEIGHT - 150, button_width, button_height, "Continue", font_size=36),
            Button(center_x, HEIGHT - 80, button_width, button_height, "Exit", font_size=36)
        ]

    def load_tips_and_lore(self):
        try:
            tips_path = resource_path('resources/loading_tips.json')
            with open(tips_path, 'r') as f:
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

        if not auto_continue:
            pg.mouse.set_visible(True)

        if random.random() < 0.5 and self.tips:
            self.current_tip = random.choice(self.tips)
        elif self.lore:
            self.current_tip = random.choice(self.lore)

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

    def set_custom_message(self, message, position=None, color=None):
        if not color:
            color = self.text_color

        if not position:
            position = (HALF_WIDTH, HALF_HEIGHT + 300)

        message_text = self.info_font.render(message, True, color)
        message_rect = message_text.get_rect(center=position)
        self.game.screen.blit(message_text, message_rect)

    def draw(self):
        if not self.active:
            return

        self.screen.blit(self.bg_image, (0, 0))

        title_text = "LOADING"
        if not self.auto_continue and self.level_number is not None:
            title_text = f"LEVEL {self.level_number}"

        self.ui_renderer.draw_metallic_text(
            title_text,
            self.title_font,
            (HALF_WIDTH, HALF_HEIGHT - 100),
            bg_alpha=128
        )

        if self.level_number is not None and self.auto_continue:
            level_text = self.info_font.render(f"LEVEL {self.level_number}", True, self.text_color)
            level_rect = level_text.get_rect(center=(HALF_WIDTH, HALF_HEIGHT))
            self.screen.blit(level_text, level_rect)

        if self.current_tip:
            tip_rect = pg.Rect(0, 0, WIDTH - 200, 70)
            tip_rect.center = (HALF_WIDTH, HALF_HEIGHT + 200)

            self.ui_renderer.draw_metallic_panel(
                tip_rect,
                chamfer_size=8,
                bg_alpha=180
            )

            tip_text = self.tip_font.render(self.current_tip, True, self.text_color)
            tip_text_rect = tip_text.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 200))
            self.screen.blit(tip_text, tip_text_rect)

        if self.auto_continue:
            circle_center = (HALF_WIDTH, self.circle_y)

            pg.draw.circle(self.screen, self.circle_bg_color, circle_center,
                          self.circle_radius, self.circle_width)

            rotation_speed = 0.3
            base_angle = time.time() * rotation_speed * 360

            for i in range(self.num_segments):
                angle = base_angle - (i * (360 / self.num_segments))
                opacity = 255 - int(180 * (i / self.num_segments) ** 1.5)
                segment_color = (*self.circle_color[:3], opacity)

                start_angle = math.radians(angle)
                end_angle = math.radians(angle + (360 / self.num_segments) * 0.8)

                pg.draw.arc(self.screen, segment_color,
                           (circle_center[0] - self.circle_radius,
                            circle_center[1] - self.circle_radius,
                            self.circle_radius * 2,
                            self.circle_radius * 2),
                           start_angle, end_angle, self.circle_width)

        if not self.auto_continue:
            for button in self.buttons:
                button.draw(self.screen)

        pg.display.flip()
