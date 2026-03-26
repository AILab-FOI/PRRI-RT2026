import pygame as pg
import os
from Assets.settings import *
from Assets.scripts.Util.font_manager import load_custom_font, resource_path
from Assets.scripts.UI.menu import MetallicUIRenderer


class GameUI:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.metallic_renderer = MetallicUIRenderer(self.screen)

        self.green_color = (0, 180, 80)
        self.orange_color = (255, 100, 0)
        self.blue_color = (0, 180, 255)
        self.dark_gray = (50, 50, 50)

        self.dash_font = load_custom_font(18)
        self.enemy_counter_font = load_custom_font(20)
        self.invulnerability_title_font = load_custom_font(24)
        self.invulnerability_timer_font = load_custom_font(40)

        self.margin_x = int(WIDTH * UI_MARGIN_PERCENT_X)
        self.margin_y = int(HEIGHT * UI_MARGIN_PERCENT_Y)

        self.dash_indicator_width = 180
        self.dash_indicator_height = 24
        self.dash_chamfer_size = 6

        self.digit_size = 90
        self.current_level = 1
        self.digit_images = self.load_digit_images()

        self.powerup_icon = self.load_texture('resources/teksture/level1/powerup.png', (100, 100))

        self.crosshair_size = 48
        self.crosshair = self.load_texture('resources/teksture/Blue-crosshair.png', (self.crosshair_size, self.crosshair_size))
        self.crosshair_y_offset = 40
        self.crosshair_pos = (
            HALF_WIDTH - self.crosshair_size // 2,
            HALF_HEIGHT - self.crosshair_size // 2 + self.crosshair_y_offset
        )

    def load_texture(self, path, res):
        texture_path = resource_path(path)
        texture = pg.image.load(texture_path).convert_alpha()
        return pg.transform.scale(texture, res)

    def load_digit_images(self):
        """Load digit images for the current level with fallback to level1 digits"""
        digits = {}
        level_digit_path = f'resources/teksture/level{self.current_level}/brojevi'
        fallback_digit_path = 'resources/teksture/level1/brojevi'
        level_digit_path_abs = resource_path(level_digit_path)

        if os.path.exists(level_digit_path_abs) and os.path.isdir(level_digit_path_abs):
            for i in range(11):
                digit_file = f'{level_digit_path}/{i}.png'
                digit_file_abs = resource_path(digit_file)

                if os.path.exists(digit_file_abs) and os.path.isfile(digit_file_abs):
                    img = self.load_texture(digit_file, [self.digit_size] * 2)
                    digits[str(i)] = img
                else:
                    fallback_digit = f'{fallback_digit_path}/{i}.png'
                    img = self.load_texture(fallback_digit, [self.digit_size] * 2)
                    digits[str(i)] = img
        else:
            for i in range(11):
                img = self.load_texture(f'{fallback_digit_path}/{i}.png', [self.digit_size] * 2)
                digits[str(i)] = img

        return digits

    def draw(self):
        self.draw_player_health()
        self.draw_dash_indicator()
        self.draw_enemy_counter()
        self.draw_invulnerability_indicator()
        self.draw_crosshair()

    def draw_crosshair(self):
        """Draw the crosshair in the center of the screen"""
        if not hasattr(self.game, 'interaction') or not self.game.interaction.is_showing_indicator:
            self.screen.blit(self.crosshair, self.crosshair_pos)

    def draw_dash_indicator(self):
        current_time = pg.time.get_ticks()
        dash_cooldown_remaining = 0
        is_dashing = self.game.player.is_dashing

        if not is_dashing:
            time_since_last_dash = current_time - self.game.player.last_dash_time
            if time_since_last_dash < PLAYER_DASH_COOLDOWN:
                dash_cooldown_remaining = 1 - (time_since_last_dash / PLAYER_DASH_COOLDOWN)

        indicator_x = WIDTH - self.dash_indicator_width - self.margin_x
        indicator_y = self.margin_y + 30
        indicator_rect = pg.Rect(indicator_x, indicator_y, self.dash_indicator_width, self.dash_indicator_height)

        if is_dashing or dash_cooldown_remaining == 0:
            dash_color = self.green_color
            dash_text = "DASH READY"
            self.metallic_renderer.draw_chamfered_rect(dash_color, indicator_rect, self.dash_chamfer_size)
        else:
            dash_color = self.orange_color
            self.metallic_renderer.draw_chamfered_rect(self.dark_gray, indicator_rect, self.dash_chamfer_size)

            fill_width = int(self.dash_indicator_width * (1 - dash_cooldown_remaining))
            if fill_width > 0:
                fill_rect = pg.Rect(indicator_x, indicator_y, fill_width, self.dash_indicator_height)
                self.metallic_renderer.draw_chamfered_rect(dash_color, fill_rect, self.dash_chamfer_size)

            cooldown_sec = max(0.1, round(dash_cooldown_remaining * (PLAYER_DASH_COOLDOWN / 1000), 1))
            dash_text = f"DASH ({cooldown_sec}s)"

        text_surface = self.dash_font.render(dash_text, True, dash_color)
        text_rect = text_surface.get_rect(center=(indicator_x + self.dash_indicator_width // 2, indicator_y - 15))
        self.screen.blit(text_surface, text_rect)

    def draw_player_health(self):
        health = str(self.game.player.health)

        for i, char in enumerate(health):
            self.screen.blit(self.digit_images[char], (self.margin_x + i * self.digit_size, self.margin_y))

        self.screen.blit(self.digit_images['10'], (self.margin_x + len(health) * self.digit_size, self.margin_y))

    def draw_invulnerability_indicator(self):
        if not self.game.player.is_invulnerable:
            return

        seconds_left = max(1, int(self.game.player.invulnerability_time_left / 1000) + 1)
        indicator_x = HALF_WIDTH - 100
        indicator_y = self.margin_y
        center_x = indicator_x + 100

        title_surface = self.invulnerability_title_font.render("INVINCIBILITY", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(center_x, indicator_y + 20))
        self.screen.blit(title_surface, title_rect)

        icon_rect = self.powerup_icon.get_rect(center=(center_x, indicator_y + 80))
        self.screen.blit(self.powerup_icon, icon_rect)

        timer_surface = self.invulnerability_timer_font.render(f"{seconds_left}s", True, self.blue_color)
        timer_rect = timer_surface.get_rect(center=(center_x, indicator_y + 140))
        self.screen.blit(timer_surface, timer_rect)

    def draw_enemy_counter(self):
        npc_list = self.game.object_handler.npc_list
        total_enemies = 0
        alive_enemies = 0

        for npc in npc_list:
            if not getattr(npc, 'is_friendly', False):
                total_enemies += 1
                if npc.alive:
                    alive_enemies += 1

        if total_enemies == 0:
            counter_color = (150, 150, 150)
        elif alive_enemies == 0:
            counter_color = self.green_color
        elif alive_enemies <= total_enemies * 0.25:
            counter_color = (180, 180, 0)
        elif alive_enemies <= total_enemies * 0.5:
            counter_color = (220, 180, 0)
        else:
            counter_color = self.orange_color

        counter_text = f"ENEMIES: {alive_enemies}/{total_enemies}"
        text_surface = self.enemy_counter_font.render(counter_text, True, counter_color)
        text_rect = text_surface.get_rect(bottomright=(WIDTH - self.margin_x, HEIGHT - self.margin_y))
        self.screen.blit(text_surface, text_rect)

    def update_level(self, level_number):
        """Update UI elements when the level changes"""
        if self.current_level != level_number:
            self.current_level = level_number
            self.digit_images = self.load_digit_images()
