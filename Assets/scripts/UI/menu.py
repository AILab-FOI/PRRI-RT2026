from multiprocessing import Value
import pygame as pg
import sys
from Assets.settings import *
from Assets.scripts.Util.font_manager import load_custom_font, resource_path


class MetallicUIRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.bg = (16, 24, 32)
        self.panel_fill = (34, 49, 63)
        self.panel_fill_2 = (26, 38, 49)
        self.panel_border_light = (112, 145, 171)
        self.panel_border_dark = (8, 12, 18)

        self.button_fill = (58, 92, 128)
        self.button_hover = (82, 128, 179)
        self.button_pressed = (43, 73, 107)
        self.button_border_light = (173, 216, 255)
        self.button_border_dark = (18, 31, 46)

        self.utility_button_fill = (92, 58, 64)
        self.utility_button_hover = (128, 79, 88)
        self.utility_button_pressed = (76, 45, 52)
        self.utility_border_light = (224, 170, 180)
        self.utility_border_dark = (40, 18, 22)

        self.text = (240, 248, 255)
        self.text_shadow = (0, 0, 0)
        self.title_color = (255, 214, 102)
        self.title_shadow = (84, 48, 0)

        self.slider_track = (42, 52, 62)
        self.slider_fill = (255, 170, 60)
        self.slider_handle = (230, 236, 240)
        self.slider_handle_dark = (90, 96, 104)

        self.pixel = 4

    def _rect(self, rect):
        return rect if isinstance(rect, pg.Rect) else pg.Rect(rect)

    def draw_panel(self, rect, fill=None):
        rect = self._rect(rect)
        fill = fill or self.panel_fill
        pg.draw.rect(self.screen, fill, rect)

        inner = rect.inflate(-self.pixel * 2, -self.pixel * 2)
        if inner.width > 0 and inner.height > 0:
            pg.draw.rect(self.screen, self.panel_fill_2, inner, self.pixel)

        pg.draw.line(self.screen, self.panel_border_light, rect.topleft, (rect.right - 1, rect.top), self.pixel)
        pg.draw.line(self.screen, self.panel_border_light, rect.topleft, (rect.left, rect.bottom - 1), self.pixel)
        pg.draw.line(self.screen, self.panel_border_dark, (rect.left, rect.bottom - 1), (rect.right - 1, rect.bottom - 1), self.pixel)
        pg.draw.line(self.screen, self.panel_border_dark, (rect.right - 1, rect.top), (rect.right - 1, rect.bottom - 1), self.pixel)
        return rect

    def draw_button(self, rect, hovered=False, pressed=False, utility=False):
        rect = self._rect(rect)

        if utility:
            base = self.utility_button_pressed if pressed else self.utility_button_hover if hovered else self.utility_button_fill
            light = self.utility_border_light
            dark = self.utility_border_dark
        else:
            base = self.button_pressed if pressed else self.button_hover if hovered else self.button_fill
            light = self.button_border_light
            dark = self.button_border_dark

        pg.draw.rect(self.screen, base, rect)
        pg.draw.line(self.screen, light, rect.topleft, (rect.right - 1, rect.top), self.pixel)
        pg.draw.line(self.screen, light, rect.topleft, (rect.left, rect.bottom - 1), self.pixel)
        pg.draw.line(self.screen, dark, (rect.left, rect.bottom - 1), (rect.right - 1, rect.bottom - 1), self.pixel)
        pg.draw.line(self.screen, dark, (rect.right - 1, rect.top), (rect.right - 1, rect.bottom - 1), self.pixel)

        inner = rect.inflate(-self.pixel * 2, -self.pixel * 2)
        if inner.width > 0 and inner.height > 0:
            pg.draw.rect(self.screen, (255, 255, 255), inner, 1)

    def draw_text(self, text, font, center, color=None, shadow_color=None, shadow_offset=3):
        color = color or self.text
        shadow_color = shadow_color or self.text_shadow

        shadow = font.render(text, False, shadow_color)
        surf = font.render(text, False, color)

        shadow_rect = shadow.get_rect(center=(center[0] + shadow_offset, center[1] + shadow_offset))
        rect = surf.get_rect(center=center)

        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(surf, rect)
        return rect

    def draw_title_banner(self, text, font, center_x, y):
        title_surface = font.render(text, False, self.title_color)
        title_rect = title_surface.get_rect(midtop=(center_x, y))
        banner = pg.Rect(title_rect.left - 24, title_rect.top - 16, title_rect.width + 48, title_rect.height + 24)
        self.draw_panel(banner, (46, 38, 72))
        self.draw_text(text, font, title_rect.center, self.title_color, self.title_shadow, 4)
        return banner

    def draw_slider_track(self, rect):
        pg.draw.rect(self.screen, self.slider_track, rect)
        pg.draw.line(self.screen, self.panel_border_light, rect.topleft, (rect.right - 1, rect.top), 2)
        pg.draw.line(self.screen, self.panel_border_light, rect.topleft, (rect.left, rect.bottom - 1), 2)
        pg.draw.line(self.screen, self.panel_border_dark, (rect.left, rect.bottom - 1), (rect.right - 1, rect.bottom - 1), 2)
        pg.draw.line(self.screen, self.panel_border_dark, (rect.right - 1, rect.top), (rect.right - 1, rect.bottom - 1), 2)

    def draw_slider_fill(self, rect):
        pg.draw.rect(self.screen, self.slider_fill, rect)

    def draw_slider_handle(self, rect, dragging=False):
        fill = self.slider_fill if dragging else self.slider_handle
        pg.draw.rect(self.screen, fill, rect)
        pg.draw.line(self.screen, (255, 255, 255), rect.topleft, (rect.right - 1, rect.top), 2)
        pg.draw.line(self.screen, (255, 255, 255), rect.topleft, (rect.left, rect.bottom - 1), 2)
        pg.draw.line(self.screen, self.slider_handle_dark, (rect.left, rect.bottom - 1), (rect.right - 1, rect.bottom - 1), 2)
        pg.draw.line(self.screen, self.slider_handle_dark, (rect.right - 1, rect.top), (rect.right - 1, rect.bottom - 1), 2)


class Button:
    def __init__(self, x, y, width, height, text, font_size=24, text_color=(240, 248, 255), utility=False):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.text_color = text_color
        self.hovered = False
        self.was_hovered = False
        self.pressed = False
        self.font = load_custom_font(self.font_size)
        self.utility = utility
        self.renderer = None
        self.update_text(text)

    def update_text(self, new_text):
        self.text = new_text
        self.text_surface = self.font.render(self.text, False, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def update(self, mouse_pos, game=None):
        self.was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.pressed = pg.mouse.get_pressed()[0] and self.hovered

        if game and self.hovered and not self.was_hovered:
            game.sound.play_sfx('menu_hover')

    def draw(self, screen):
        renderer = getattr(self, 'renderer', None) or MetallicUIRenderer(screen)
        self.renderer = renderer
        renderer.draw_button(self.rect, self.hovered, self.pressed, self.utility)

        text_center = self.rect.center
        if self.pressed:
            text_center = (text_center[0] + 2, text_center[1] + 2)

        renderer.draw_text(self.text, self.font, text_center, self.text_color, (0, 0, 0), 2)

    def is_clicked(self, event, game=None):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.hovered:
            if game:
                game.sound.play_sfx('menu_click')
            return True
        return False


class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, text, font_size=18):
        self.rect = pg.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.text = text
        self.font_size = font_size
        self.dragging = False
        self.font = load_custom_font(self.font_size)
        self.handle_rect = pg.Rect(0, 0, 20, height + 16)
        self.renderer = None
        self.update_handle_position()
        self.update_text()

    def update_text(self):
        self.text_surface = self.font.render(f"{self.text}: {int(self.value)}%", False, (240, 248, 255))
        self.text_rect = self.text_surface.get_rect(midbottom=(self.rect.centerx, self.rect.y - 10))

    def update_handle_position(self):
        normalized = (self.value - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + int((self.rect.width - self.handle_rect.width) * normalized)
        self.handle_rect.x = handle_x
        self.handle_rect.y = self.rect.y - 8

    def update(self, mouse_pos, mouse_pressed):
        if mouse_pressed[0]:
            if self.handle_rect.collidepoint(mouse_pos):
                self.dragging = True
            if self.dragging:
                normalized = (mouse_pos[0] - self.rect.x) / self.rect.width
                normalized = max(0, min(1, normalized))
                self.value = self.min_val + normalized * (self.max_val - self.min_val)
                self.update_handle_position()
                self.update_text()
        else:
            self.dragging = False

    def draw(self, screen):
        renderer = getattr(self, 'renderer', None) or MetallicUIRenderer(screen)
        self.renderer = renderer
        renderer.draw_text(self.text, self.font, self.text_rect.center, (240, 248, 255), (0, 0, 0), 2)

        renderer.draw_slider_track(self.rect)

        fill_width = int((self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        if fill_width > 0:
            fill_rect = pg.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            renderer.draw_slider_fill(fill_rect)

        renderer.draw_slider_handle(self.handle_rect, self.dragging)


class Menu:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.state = 'main'
        self.start_mode = 'normal'
        self.ui_renderer = MetallicUIRenderer(self.screen)

        self.utility_texts = ["Settings", "Exit"]
        self.pause_utility_texts = ["Settings", "Main Menu", "Exit"]

        self.main_buttons = []
        self.utility_buttons = []
        self.level_buttons = []

        self._setup_layout()
        self._setup_settings_ui()
        self._load_background()
        self._setup_text()

    def _setup_layout(self):
        self.button_width = 320
        self.button_height = 54
        self.button_gap = 16

        panel_width = 360
        action_h = 300
        utility_h = 150
        panel_gap = 22

        total_h = action_h + panel_gap + utility_h
        start_y = HALF_HEIGHT - total_h // 2

        self.action_panel = pg.Rect(0, start_y, panel_width, action_h)
        self.action_panel.centerx = HALF_WIDTH

        self.utility_panel = pg.Rect(0, self.action_panel.bottom + panel_gap, panel_width, utility_h)
        self.utility_panel.centerx = HALF_WIDTH

        self.settings_panel = pg.Rect(HALF_WIDTH -260, HALF_HEIGHT -200, 520, 430)
        self.settings_panel.center = (HALF_WIDTH, HALF_HEIGHT)

    def _setup_settings_ui(self):
        bx = self.settings_panel.x + 100
        by = self.settings_panel.y + 290
        bw = self.settings_panel.width - 200
        bh = 48

        self.settings_buttons = [
            Button(bx, by, bw, bh, "Windowed", utility=True),
            Button(bx, by + 64, bw, bh, "Fullscreen", utility=True),
            Button(bx, by + 128, bw, bh, "Back", utility=True),
        ]

        slider_w = self.settings_panel.width - 120
        slider_x = self.settings_panel.x + 60

        sens_percent = (MOUSE_SENSITIVITY - MOUSE_SENSITIVITY_MIN) / \
                   (MOUSE_SENSITIVITY_MAX - MOUSE_SENSITIVITY_MIN) * 100

        self.sliders = [
            Slider(slider_x, self.settings_panel.y + 80, slider_w, 14, 0, 100,
                   self.game.sound.music_slider_percent, "Music Volume"),
            Slider(slider_x, self.settings_panel.y + 150, slider_w, 14, 0, 100,
                   self.game.sound.sfx_slider_percent, "SFX Volume"),
            Slider(slider_x, self.settings_panel.y + 220, slider_w, 14, 0, 100, sens_percent, "Mouse Sensitivity"),
        ]

    def _load_background(self):
        bg_image_path = resource_path('resources/teksture/pocetna.png')
        self.bg_image = pg.image.load(bg_image_path).convert()
        self.bg_image = pg.transform.scale(self.bg_image, self.screen.get_size())

        self.bg_overlay = pg.Surface(self.screen.get_size(), pg.SRCALPHA)
        self.bg_overlay.fill((0, 0, 0, 120))

    def _setup_text(self):
        self.title_font = load_custom_font(56)
        self.small_font = load_custom_font(14)
        self.version = "v0.1"
        self.credits = "2026 PRRI-RT Team"

    def _refresh_screen_refs(self):
        self.screen = self.game.screen
        self.ui_renderer = MetallicUIRenderer(self.screen)
        self.bg_image = pg.transform.scale(self.bg_image, self.screen.get_size())
        self.bg_overlay = pg.Surface(self.screen.get_size(), pg.SRCALPHA)
        self.bg_overlay.fill((0, 0, 0, 120))

    def create_menu_buttons(self):
        self.main_buttons = []
        self.utility_buttons = []

        is_game_running = hasattr(self.game, 'game_initialized') and self.game.game_initialized

        if is_game_running:
            action_texts = ["Continue Game", "Reset Level", "Gauntlet", "Level Select"]
            utility_texts = self.pause_utility_texts
        else:
            action_texts = ["Start Game", "Gauntlet", "Level Select"]
            utility_texts = self.utility_texts

        action_h = 28 + len(action_texts) * self.button_height + max(0, len(action_texts) - 1) * self.button_gap + 16
        self.action_panel.height = action_h
        
        self.utility_panel.y = self.action_panel.bottom + 32
        utility_h = 24 + len(utility_texts) * self.button_height + max(0, len(utility_texts) - 1) * self.button_gap + 16
        self.utility_panel.height = utility_h

        start_y = self.action_panel.y + 28
        for i, text in enumerate(action_texts):
            y = start_y + i * (self.button_height + self.button_gap)
            self.main_buttons.append(
                Button(self.action_panel.x + 20, y, self.button_width, self.button_height, text, utility=False)
            )

        util_start_y = self.utility_panel.y + 24
        for i, text in enumerate(utility_texts):
            y = util_start_y + i * (self.button_height + self.button_gap)
            self.utility_buttons.append(
                Button(self.utility_panel.x + 20, y, self.button_width, self.button_height, text, utility=True)
            )

    def create_level_buttons(self):
        self.level_buttons = []
        num_levels = self.game.level_manager.max_level or 6

        cols = 3
        button_w = 180
        button_h = 50
        spacing = 16
        panel = pg.Rect(HALF_WIDTH - 320, 220, 640, 300)
        self.level_panel = panel

        total_width = cols * button_w + (cols - 1) * spacing
        start_x = panel.x + (panel.width - total_width) // 2
        start_y = panel.y + 34

        for i in range(num_levels):
            row = i // cols
            col = i % cols
            x = start_x + col * (button_w + spacing)
            y = start_y + row * (button_h + spacing)
            self.level_buttons.append(Button(x, y, button_w, button_h, f"Level {i+1}", font_size=20))

        back_y = start_y + ((num_levels - 1) // cols + 1) * (button_h + spacing) + 24
        self.level_buttons.append(Button(HALF_WIDTH - 90, back_y, 180, button_h, "Back", font_size=20, utility=True))

    def handle_events(self):
        mouse_pos = pg.mouse.get_pos()
        mouse_pressed = pg.mouse.get_pressed()

        if not self.main_buttons and self.state == 'main':
            self.create_menu_buttons()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if self.state == 'main':
                for button in self.main_buttons + self.utility_buttons:
                    button.update(mouse_pos, self.game)
                    if button.is_clicked(event, self.game):
                        if button.text in ("Start Game", "Continue Game"):
                            self.start_mode = 'normal'
                            self.state = 'game'
                            pg.mouse.set_visible(False)
                            return True

                        elif button.text == "Gauntlet":
                            self.start_mode = 'gauntlet'
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

                        elif button.text == "Level Select":
                            self.state = 'level_select'
                            self.create_level_buttons()

                        elif button.text == "Main Menu":
                            self.game.game_initialized = False
                            self.state = 'main'
                            self.create_menu_buttons()

                        elif button.text == "Exit":
                            pg.quit()
                            sys.exit()

            elif self.state == 'level_select':
                for button in self.level_buttons:
                    button.update(mouse_pos, self.game)
                    if button.is_clicked(event, self.game):
                        if button.text == "Back":
                            self.state = 'main'
                            self.create_menu_buttons()
                        else:
                            level_num = int(button.text.split(" ")[1])
                            self.game.level_manager.current_level = level_num
                            self.start_mode = 'normal'
                            self.state = 'game'
                            self.game.game_initialized = False
                            pg.mouse.set_visible(False)
                            return True

            elif self.state == 'settings':
                for button in self.settings_buttons:
                    button.update(mouse_pos, self.game)
                    if button.is_clicked(event, self.game):
                        if button.text == "Back":
                            self.state = 'main'
                            self.apply_settings()

                        elif button.text == "Windowed":
                            self.game.is_fullscreen = False
                            self.game.update_display_mode()
                            self._refresh_screen_refs()

                        elif button.text == "Fullscreen":
                            self.game.is_fullscreen = True
                            self.game.update_display_mode()
                            self._refresh_screen_refs()

        if self.state == 'settings':
            self.sliders[0].update(mouse_pos, mouse_pressed)
            self.sliders[1].update(mouse_pos, mouse_pressed)
            self.sliders[2].update(mouse_pos, mouse_pressed)
            self.game.sound.set_music_slider(self.sliders[0].value)
            self.game.sound.set_sfx_slider(self.sliders[1].value)

            import Assets.settings as _s
            _s.MOUSE_SENSITIVITY = _s.MOUSE_SENSITIVITY_MIN + (self.sliders[2].value / 100) * (MOUSE_SENSITIVITY_MAX - MOUSE_SENSITIVITY_MIN)

        elif self.state == 'main':
            for button in self.main_buttons + self.utility_buttons:
                button.update(mouse_pos, self.game)

        elif self.state == 'level_select':
            for button in self.level_buttons:
                button.update(mouse_pos, self.game)

        return False

    def apply_settings(self):
        self.game.sound.set_music_slider(self.sliders[0].value)
        self.game.sound.set_sfx_slider(self.sliders[1].value)

    def draw_main_menu(self):
        self.ui_renderer.draw_title_banner("PEST CONTROL", self.title_font, HALF_WIDTH, 56)

        self.ui_renderer.draw_panel(self.action_panel)
        self.ui_renderer.draw_text(
            "GAME",
            self.small_font,
            (self.action_panel.centerx, self.action_panel.y + 14),
            self.ui_renderer.title_color,
            (0, 0, 0),
            2
        )
        for button in self.main_buttons:
            button.draw(self.screen)

        self.ui_renderer.draw_panel(self.utility_panel, (54, 38, 46))
        self.ui_renderer.draw_text(
            "SYSTEM",
            self.small_font,
            (self.utility_panel.centerx, self.utility_panel.y + 14),
            self.ui_renderer.title_color,
            (0, 0, 0),
            2
        )
        for button in self.utility_buttons:
            button.draw(self.screen)

        self.ui_renderer.draw_text(self.version, self.small_font, (WIDTH - 64, 22), (220, 220, 220), (0, 0, 0), 2)
        self.ui_renderer.draw_text(self.credits, self.small_font, (96, 22), (220, 220, 220), (0, 0, 0), 2)

    def draw_settings(self):
        self.ui_renderer.draw_title_banner("SETTINGS", self.title_font, HALF_WIDTH, 56)
        self.ui_renderer.draw_panel(self.settings_panel, (34, 42, 52))

        for slider in self.sliders:
            slider.draw(self.screen)

        for button in self.settings_buttons:
            button.draw(self.screen)

    def draw_level_select(self):
        self.ui_renderer.draw_title_banner("LEVEL SELECT", self.title_font, HALF_WIDTH, 56)
        self.ui_renderer.draw_panel(self.level_panel, (34, 42, 52))

        for button in self.level_buttons:
            button.draw(self.screen)

    def draw(self):
        self.screen.blit(self.bg_image, (0, 0))
        self.screen.blit(self.bg_overlay, (0, 0))

        if self.state == 'main':
            self.draw_main_menu()
        elif self.state == 'settings':
            self.draw_settings()
        elif self.state == 'level_select':
            self.draw_level_select()

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
