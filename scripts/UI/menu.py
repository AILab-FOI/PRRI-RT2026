import pygame as pg
import sys
from settings import *
from scripts.Util.font_manager import load_custom_font, resource_path

class MetallicUIRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.accent_color = (255, 140, 0)
        self.bg_color = (40, 40, 45)
        self.hover_color = (60, 60, 65)
        self.border_color = (80, 80, 85)
        self.bevel_size = 3
        self.bevel_light = (70, 70, 75)
        self.bevel_dark = (30, 30, 35)

    def _get_chamfer_points(self, rect, chamfer_size):
        return [
            (rect.left + chamfer_size, rect.top),
            (rect.right - chamfer_size, rect.top),
            (rect.right, rect.top + chamfer_size),
            (rect.right, rect.bottom - chamfer_size),
            (rect.right - chamfer_size, rect.bottom),
            (rect.left + chamfer_size, rect.bottom),
            (rect.left, rect.bottom - chamfer_size),
            (rect.left, rect.top + chamfer_size)
        ]

    def draw_chamfered_rect(self, color, rect, chamfer_size, border_width=0):
        points = self._get_chamfer_points(rect, chamfer_size)

        if border_width == 0:
            pg.draw.polygon(self.screen, color, points)
        else:
            pg.draw.polygon(self.screen, color, points, border_width)

        return points

    def draw_bevel_effect(self, rect, chamfer_size):
        bevel_top_left = [
            (rect.left + chamfer_size, rect.top),
            (rect.left, rect.top + chamfer_size),
            (rect.left, rect.bottom - chamfer_size),
            (rect.left + chamfer_size, rect.bottom),
            (rect.left + self.bevel_size + chamfer_size, rect.bottom - self.bevel_size),
            (rect.left + self.bevel_size, rect.bottom - chamfer_size - self.bevel_size),
            (rect.left + self.bevel_size, rect.top + chamfer_size + self.bevel_size),
            (rect.left + self.bevel_size + chamfer_size, rect.top + self.bevel_size)
        ]
        pg.draw.polygon(self.screen, self.bevel_dark, bevel_top_left)

        bevel_bottom_right = [
            (rect.right - chamfer_size, rect.top),
            (rect.right, rect.top + chamfer_size),
            (rect.right, rect.bottom - chamfer_size),
            (rect.right - chamfer_size, rect.bottom),
            (rect.right - self.bevel_size - chamfer_size, rect.bottom - self.bevel_size),
            (rect.right - self.bevel_size, rect.bottom - chamfer_size - self.bevel_size),
            (rect.right - self.bevel_size, rect.top + chamfer_size + self.bevel_size),
            (rect.right - self.bevel_size - chamfer_size, rect.top + self.bevel_size)
        ]
        pg.draw.polygon(self.screen, self.bevel_light, bevel_bottom_right)

    def draw_chamfered_rect_alpha(self, color, rect, chamfer_size, border_width=0, alpha=255):
        points = self._get_chamfer_points(rect, chamfer_size)

        temp_surface = pg.Surface((rect.width + 8, rect.height + 8), pg.SRCALPHA)

        if border_width == 0:
            pg.draw.polygon(temp_surface, (*color, alpha), [(p[0] - rect.left + 4, p[1] - rect.top + 4) for p in points])
        else:
            pg.draw.polygon(temp_surface, (*color, alpha), [(p[0] - rect.left + 4, p[1] - rect.top + 4) for p in points], border_width)
        self.screen.blit(temp_surface, (rect.left - 4, rect.top - 4))

        return points

    def draw_metallic_panel(self, rect, chamfer_size, color=None, border_color=None, with_bevel=True, border_alpha=255, bg_alpha=255):
        color = color or self.bg_color
        border_color = border_color or self.border_color

        if bg_alpha < 255:
            self.draw_chamfered_rect_alpha(color, rect, chamfer_size, 0, bg_alpha)
        else:
            self.draw_chamfered_rect(color, rect, chamfer_size)

        if with_bevel:
            self.draw_bevel_effect(rect, chamfer_size)

        border_rect = rect.inflate(4, 4)
        if border_alpha < 255:
            self.draw_chamfered_rect_alpha(border_color, border_rect, chamfer_size, 2, border_alpha)
        else:
            self.draw_chamfered_rect(border_color, border_rect, chamfer_size, 2)

    def draw_metallic_text(self, text, font, pos, padding=(20, 15), chamfer_size=10, border_color=None, border_alpha=255, bg_alpha=255):
        text_surface = font.render(text, True, (220, 220, 255))
        text_rect = text_surface.get_rect(center=pos)

        bg_rect = text_rect.inflate(padding[0] * 2, padding[1] * 2)

        border_color = border_color if border_color is not None else self.accent_color
        self.draw_metallic_panel(bg_rect, chamfer_size, border_color=border_color, border_alpha=border_alpha, bg_alpha=bg_alpha)
        self.screen.blit(text_surface, text_rect)

        return bg_rect

    def draw_glow_effect(self, rect, chamfer_size, color=None, alpha=100):
        color = color or self.accent_color
        glow_rect = rect.inflate(16, 16)
        glow_color = (*color, alpha)
        glow_surf = pg.Surface((glow_rect.width, glow_rect.height), pg.SRCALPHA)
        pg.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=chamfer_size)
        self.screen.blit(glow_surf, glow_rect.topleft)

class Button:
    def __init__(self, x, y, width, height, text, font_size=36, text_color=(220, 220, 255),
                 bg_color=(40, 40, 45), hover_color=(60, 60, 65)):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.text_color = text_color
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.hovered = False
        self.was_hovered = False
        self.glow_size = 0
        self.chamfer_size = 8
        self.font = load_custom_font(self.font_size)
        self.update_text(text)
        self.renderer = None

    def update_text(self, new_text):
        self.text = new_text
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def update(self, mouse_pos, game=None):
        self.was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)

        if game and self.hovered and not self.was_hovered:
            game.sound.menu_hover.play()

        if self.hovered:
            self.glow_size = min(self.glow_size + 0.5, 8)
        else:
            self.glow_size = max(self.glow_size - 0.5, 0)

    def draw(self, screen):
        renderer = getattr(self, 'renderer', None) or MetallicUIRenderer(screen)
        self.renderer = renderer

        color = self.hover_color if self.hovered else self.bg_color
        border_color = self.renderer.accent_color if self.hovered else self.renderer.border_color

        self.renderer.draw_metallic_panel(self.rect, self.chamfer_size, color, border_color)

        screen.blit(self.text_surface, self.text_rect)
        if self.hovered:
            self.renderer.draw_glow_effect(self.rect, self.chamfer_size)

    def is_clicked(self, event, game=None):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.hovered:
            if game:
                game.sound.menu_click.play()
            return True
        return False

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, text, font_size=24):
        self.rect = pg.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.text = text
        self.font_size = font_size
        self.dragging = False
        self.font = load_custom_font(self.font_size)
        self.update_text()
        self.chamfer_size = 4
        self.handle_rect = pg.Rect(0, 0, 16, height + 14)
        self.update_handle_position()
        self.renderer = None

    def update_text(self):
        self.text_surface = self.font.render(f"{self.text}: {int(self.value * 100)}%", True, (220, 220, 255))
        self.text_rect = self.text_surface.get_rect(center=(self.rect.centerx, self.rect.y - 15))

    def update_handle_position(self):
        normalized_value = (self.value - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + (self.rect.width - self.handle_rect.width) * normalized_value
        self.handle_rect.x = handle_x
        self.handle_rect.y = self.rect.y - 7

    def update(self, mouse_pos, mouse_pressed):
        if mouse_pressed[0]:
            if self.handle_rect.collidepoint(mouse_pos):
                self.dragging = True
            elif self.dragging:
                normalized_pos = (mouse_pos[0] - self.rect.x) / self.rect.width
                normalized_pos = max(0, min(1, normalized_pos))
                self.value = self.min_val + normalized_pos * (self.max_val - self.min_val)
                self.update_handle_position()
                self.update_text()
        else:
            self.dragging = False

    def draw(self, screen):
        renderer = getattr(self, 'renderer', None) or MetallicUIRenderer(screen)
        self.renderer = renderer

        self.renderer.draw_chamfered_rect((30, 30, 35), self.rect, self.chamfer_size)

        fill_width = int((self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        if fill_width > 0:
            fill_rect = pg.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            self.renderer.draw_chamfered_rect(self.renderer.accent_color, fill_rect, self.chamfer_size)

        border_rect = self.rect.inflate(2, 2)
        self.renderer.draw_chamfered_rect(self.renderer.border_color, border_rect, self.chamfer_size, 1)

        handle_color = (80, 80, 85) if self.dragging else (60, 60, 65)
        pg.draw.rect(screen, handle_color, self.handle_rect, border_radius=4)

        pg.draw.line(screen, (100, 100, 105),
                    (self.handle_rect.left + 1, self.handle_rect.top + 1),
                    (self.handle_rect.right - 1, self.handle_rect.top + 1), 1)
        pg.draw.line(screen, (100, 100, 105),
                    (self.handle_rect.left + 1, self.handle_rect.top + 1),
                    (self.handle_rect.left + 1, self.handle_rect.bottom - 1), 1)

        pg.draw.line(screen, (40, 40, 45),
                    (self.handle_rect.left + 1, self.handle_rect.bottom - 1),
                    (self.handle_rect.right - 1, self.handle_rect.bottom - 1), 1)
        pg.draw.line(screen, (40, 40, 45),
                    (self.handle_rect.right - 1, self.handle_rect.top + 1),
                    (self.handle_rect.right - 1, self.handle_rect.bottom - 1), 1)

        pg.draw.rect(screen, (100, 100, 105), self.handle_rect, 1, border_radius=4)
        screen.blit(self.text_surface, self.text_rect)

class Menu:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.state = 'main'
        button_height = 60

        self.main_menu_texts = ["Start Game", "Settings", "Exit"]
        self.pause_menu_texts = ["Continue Game", "Reset Level", "Settings", "Exit"]
        button_widths = []
        all_texts = set(self.main_menu_texts + self.pause_menu_texts)
        for text in all_texts:
            font = load_custom_font(36)
            text_width = font.size(text)[0]
            button_width = max(300, text_width + 100)
            button_widths.append(button_width)

        max_button_width = max(button_widths)
        center_x = HALF_WIDTH - max_button_width // 2
        self.max_button_width = max_button_width
        self.button_height = button_height
        self.center_x = center_x

        self.main_buttons = []

        self.settings_buttons = [
            Button(center_x, HALF_HEIGHT + 200, max_button_width, button_height, "Back")
        ]

        slider_width = max_button_width
        slider_center_x = HALF_WIDTH - slider_width // 2
        self.sliders = [
            Slider(slider_center_x, HALF_HEIGHT - 100, slider_width, 10, 0, 1,
                   self.game.sound.music_volume, "Music Volume"),
            Slider(slider_center_x, HALF_HEIGHT, slider_width, 10, 0, 1,
                   self.game.sound.sfx_volume, "SFX Volume")
        ]

        bg_image_path = resource_path('resources/teksture/pocetna.png')
        self.bg_image = pg.image.load(bg_image_path)
        self.bg_image = pg.transform.scale(self.bg_image, RES)

        self.title_font = load_custom_font(72)
        self.version = "v1.0"
        self.credits = "2025 PRRI-RT Team"
        self.small_font = load_custom_font(16)
        self.version_text = self.small_font.render(self.version, True, (180, 180, 220))
        self.version_rect = self.version_text.get_rect(topright=(WIDTH - 40, 20))
        self.credits_text = self.small_font.render(self.credits, True, (180, 180, 220))
        self.credits_rect = self.credits_text.get_rect(topleft=(40, 20))

    def create_menu_buttons(self):
        self.main_buttons = []
        is_game_running = hasattr(self.game, 'game_initialized') and self.game.game_initialized
        button_texts = self.pause_menu_texts if is_game_running else self.main_menu_texts

        y_positions = []
        num_buttons = len(button_texts)
        start_y = HALF_HEIGHT - (num_buttons * self.button_height + (num_buttons - 1) * 20) // 2
        for i in range(num_buttons):
            y_positions.append(start_y + i * (self.button_height + 20))

        for i, text in enumerate(button_texts):
            self.main_buttons.append(
                Button(self.center_x, y_positions[i], self.max_button_width, self.button_height, text)
            )

    def handle_events(self):
        mouse_pos = pg.mouse.get_pos()
        mouse_pressed = pg.mouse.get_pressed()

        if not self.main_buttons:
            self.create_menu_buttons()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if self.state == 'main':
                for button in self.main_buttons:
                    button.update(mouse_pos, self.game)
                    if button.is_clicked(event, self.game):
                        if button.text == "Start Game" or button.text == "Continue Game":
                            self.state = 'game'
                            pg.mouse.set_visible(False)
                            return True
                        elif button.text == "Reset Level":
                            self.state = 'game'
                            pg.mouse.set_visible(False)
                            self.game.reset_current_level()
                            return True
                        elif button.text == "Settings":
                            self.state = 'settings'
                        elif button.text == "Exit":
                            pg.quit()
                            sys.exit()

            elif self.state == 'settings':
                for button in self.settings_buttons:
                    button.update(mouse_pos, self.game)
                    if button.is_clicked(event, self.game):
                        if button.text == "Back":
                            self.state = 'main'
                            self.apply_settings()

        if self.state == 'settings':
            for slider in self.sliders:
                slider.update(mouse_pos, mouse_pressed)

        return False

    def apply_settings(self):
        self.game.sound.music_volume = self.sliders[0].value
        pg.mixer.music.set_volume(self.sliders[0].value)
        self.game.sound.sfx_volume = self.sliders[1].value
        self.game.sound.update_sfx_volume()

    def draw_title(self, title_text, y_pos=100):
        if not hasattr(self, 'ui_renderer'):
            self.ui_renderer = MetallicUIRenderer(self.screen)

        border_color = self.ui_renderer.bg_color
        return self.ui_renderer.draw_metallic_text(title_text, self.title_font, (HALF_WIDTH, y_pos), border_color=border_color, bg_alpha=128)

    def draw(self):
        self.screen.blit(self.bg_image, (0, 0))

        if self.state == 'main':
            self.draw_title("Galaxy's Doom", 120)

            for button in self.main_buttons:
                button.draw(self.screen)

            self.screen.blit(self.version_text, self.version_rect)
            self.screen.blit(self.credits_text, self.credits_rect)

        elif self.state == 'settings':
            self.draw_title("Settings")

            for slider in self.sliders:
                slider.draw(self.screen)

            for button in self.settings_buttons:
                button.draw(self.screen)

        pg.display.flip()

    def run(self):
        pg.mouse.set_visible(True)
        self.create_menu_buttons()

        while self.state != 'game':
            start_game = self.handle_events()
            if start_game:
                break
            self.draw()
            self.game.clock.tick(60)
