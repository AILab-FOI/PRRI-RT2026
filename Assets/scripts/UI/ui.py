import pygame as pg
from Assets.settings import *
from Assets.scripts.UI.ui_level_colors import *
from Assets.scripts.Util.font_manager import load_custom_font, resource_path
from Assets.scripts.UI.menu import MetallicUIRenderer


class GameUI:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.metallic_renderer = MetallicUIRenderer(self.screen)
        self.wave_manager = game.wave_manager

        self.green_color = (0, 180, 80)
        self.orange_color = (255, 100, 0)
        self.blue_color = (0, 180, 255)
        self.red_color = (220, 60, 60)
        self.yellow_color = (255, 215, 0)
        self.dark_gray = (50, 50, 50)
        self.white = (235, 235, 245)
        self.black = (10, 10, 14)
        self.hud_bg_outer = (8, 55, 60)
        self.hud_bg_main = (14, 18, 34)
        self.hud_panel = (12, 18, 135)
        self.hud_inner = (20, 28, 180)
        self.hud_border = (115, 190, 210)
        self.health_bg = (45, 45, 52)
        self.health_low = (200, 45, 45)
        self.health_mid = (220, 150, 0)

        self.tint_color_map = UI_TINT_COLORS
        self.current_level = 1

        self.label_font = load_custom_font(18)
        self.value_font = load_custom_font(26)
        self.dash_font = load_custom_font(20)
        self.small_font = load_custom_font(16)
        self.fps_font = load_custom_font(18)
        self.invulnerability_title_font = load_custom_font(24)
        self.invulnerability_timer_font = load_custom_font(40)

        self.margin_x = int(WIDTH * UI_MARGIN_PERCENT_X)
        self.margin_y = int(HEIGHT * UI_MARGIN_PERCENT_Y)

        self.powerup_icon = self.load_texture('resources/teksture/level1/powerup.png', (100, 100))
        self.item_icon = self.load_texture('resources/teksture/heal_item.png', (72, 72))
        self.item_icon_gray = self.make_gray_icon(self.item_icon)

        self.weapon_icon_height = 72
        self.weapon_icons = [
            self.load_texture_fixed_height('resources/sprites/weapon/pistol_stand.png', self.weapon_icon_height),
            self.load_texture_fixed_height('resources/sprites/weapon/puska_stand.png', self.weapon_icon_height),
            self.load_texture_fixed_height('resources/sprites/weapon/plasma_stand.png', self.weapon_icon_height),
        ]
        self.weapon_icons_gray = [self.make_gray_icon(icon) for icon in self.weapon_icons]

        self.crosshair_size = 48
        self.crosshair = self.load_texture('resources/teksture/Blue-crosshair.png', (self.crosshair_size, self.crosshair_size))
        self.crosshair_y_offset = 10
        self.hit_marker_time = 0
        self.hit_marker_duration = 150

        self.hud_height = 118
        self.hud_padding = 12
        self.hud_gap = 10
        self.viewport_bottom_gap = 6

    def bind_wave_manager(self):
        self.wave_manager = self.game.wave_manager

    def load_texture(self, path, res):
        texture_path = resource_path(path)
        texture = pg.image.load(texture_path).convert_alpha()
        return pg.transform.scale(texture, res)

    def load_texture_fixed_height(self, path, target_height):
        texture_path = resource_path(path)
        texture = pg.image.load(texture_path).convert_alpha()

        orig_w = texture.get_width()
        orig_h = texture.get_height()

        scale = target_height / orig_h
        new_w = int(orig_w * scale)
        new_h = int(target_height)

        return pg.transform.smoothscale(texture, (new_w, new_h))

    def update_screen_reference(self):
        self.screen = self.game.screen
        self.metallic_renderer.screen = self.screen
        if self.wave_manager is not self.game.wave_manager:
            self.bind_wave_manager()

    def update_level(self, level_number):
        self.current_level = level_number
        self.bind_wave_manager()

    def get_level_tint_color(self):
        return self.tint_color_map.get(self.current_level, self.tint_color_map['default'])

    def make_gray_icon(self, surface):
        return pg.transform.grayscale(surface.convert_alpha())

    def show_hit_marker(self):
        self.hit_marker_time = pg.time.get_ticks()

    def get_enemies_left(self):
        return self.wave_manager.get_enemies_left()

    def get_score(self):
        return self.wave_manager.get_score()

    def get_survival_seconds(self):
        return self.wave_manager.get_survival_seconds()

    def draw(self):
        self.update_screen_reference()
        self.draw_top_stats()
        self.draw_bottom_hud()
        self.draw_crosshair()
        self.draw_invulnerability_indicator()
        self.draw_fps()

    def draw_top_stats(self):
        score_rect = pg.Rect(18, 18, 180, 64)
        time_rect = pg.Rect(210, 18, 180, 64)

        self._draw_panel(score_rect)
        self._draw_panel(time_rect)

        self._draw_label_value(score_rect, 'SCORE', self.get_score(), self.yellow_color)
        self._draw_label_value(time_rect, 'TIME', f'{self.get_survival_seconds()}s', self.get_level_tint_color())

    def draw_fps(self):
        fps = str(int(self.game.clock.get_fps()))
        fps_surface = self.fps_font.render(f'FPS: {fps}', True, (0, 255, 0))
        self.screen.blit(fps_surface, (10, 92))

    def draw_crosshair(self):
        cx = HALF_WIDTH
        cy = HALF_HEIGHT
        crosshair_pos = (cx - self.crosshair_size // 2, cy - self.crosshair_size // 2)
        self.screen.blit(self.crosshair, crosshair_pos)

        if pg.time.get_ticks() - self.hit_marker_time < self.hit_marker_duration:
            color = (255, 255, 255)
            length = 12
            offset = 8
            thickness = 2
            pg.draw.line(self.screen, color, (cx - offset, cy - offset), (cx - offset - length, cy - offset - length), thickness)
            pg.draw.line(self.screen, color, (cx + offset, cy - offset), (cx + offset + length, cy - offset - length), thickness)
            pg.draw.line(self.screen, color, (cx - offset, cy + offset), (cx - offset - length, cy + offset + length), thickness)
            pg.draw.line(self.screen, color, (cx + offset, cy + offset), (cx + offset + length, cy + offset + length), thickness)

    def _draw_panel(self, rect):
        pg.draw.rect(self.screen, self.hud_panel, rect)
        inner = rect.inflate(-4, -4)
        pg.draw.rect(self.screen, self.hud_inner, inner)
        pg.draw.rect(self.screen, self.hud_border, rect, 2)
        pg.draw.line(self.screen, (180, 220, 255), (rect.x + 2, rect.y + 2), (rect.right - 3, rect.y + 2), 1)
        pg.draw.line(self.screen, (0, 0, 60), (rect.x + 2, rect.bottom - 3), (rect.right - 3, rect.bottom - 3), 1)

    def _draw_label_value(self, rect, label, value, value_color=None):
        label_surf = self.label_font.render(label, True, self.white)
        label_rect = label_surf.get_rect(midtop=(rect.centerx, rect.y + 6))
        self.screen.blit(label_surf, label_rect)

        color = value_color or self.white
        value_surf = self.value_font.render(str(value), True, color)
        value_rect = value_surf.get_rect(center=(rect.centerx, rect.centery + 14))
        self.screen.blit(value_surf, value_rect)

    def _get_health_fill_color(self, ratio):
        if ratio <= 0.25:
            return self.health_low
        if ratio <= 0.5:
            return self.health_mid
        return self.get_level_tint_color()

    def draw_bottom_hud(self):
        gap = self.hud_gap
        panel_y = HEIGHT - self.hud_height + self.hud_padding
        panel_h = self.hud_height - self.hud_padding * 2 - 8

        level_w = 90
        dash_w = 100
        enemy_w = 110
        health_w = 300

        pickup_w = 110
        ammo_w = 150
        weapon_w = 110

        left_total_w = level_w + dash_w + enemy_w + health_w + gap * 3
        right_total_w = pickup_w + ammo_w + weapon_w + gap * 2

        left_outer = pg.Rect(
            8,
            HEIGHT - self.hud_height,
            left_total_w + self.hud_padding * 2,
            self.hud_height - 8
        )

        right_outer = pg.Rect(
            WIDTH - 8 - (right_total_w + self.hud_padding * 2),
            HEIGHT - self.hud_height,
            right_total_w + self.hud_padding * 2,
            self.hud_height - 8
        )

        for outer in (left_outer, right_outer):
            border = outer.inflate(8, 8)
            pg.draw.rect(self.screen, self.hud_bg_outer, border)
            pg.draw.rect(self.screen, self.hud_bg_main, outer)
            pg.draw.rect(self.screen, self.hud_border, border, 3)
            pg.draw.rect(self.screen, (4, 10, 20), outer, 2)

        left_x = left_outer.x + self.hud_padding
        right_x = right_outer.x + self.hud_padding

        level_rect = pg.Rect(left_x, panel_y, level_w, panel_h)
        dash_rect = pg.Rect(level_rect.right + gap, panel_y, dash_w, panel_h)
        enemy_rect = pg.Rect(dash_rect.right + gap, panel_y, enemy_w, panel_h)
        health_rect = pg.Rect(enemy_rect.right + gap, panel_y, health_w, panel_h)

        pickup_rect = pg.Rect(right_x, panel_y, pickup_w, panel_h)
        ammo_rect = pg.Rect(pickup_rect.right + gap, panel_y, ammo_w, panel_h)
        weapon_rect = pg.Rect(ammo_rect.right + gap, panel_y, weapon_w, panel_h)

        self._draw_panel(level_rect)
        self._draw_panel(dash_rect)
        self._draw_panel(enemy_rect)
        self._draw_panel(health_rect)

        self._draw_panel(pickup_rect)
        self._draw_panel(ammo_rect)
        self._draw_panel(weapon_rect)

        self._draw_side_left(level_rect, dash_rect, enemy_rect, health_rect)
        self._draw_side_right(pickup_rect, ammo_rect, weapon_rect)

    def _draw_side_left(self, level_rect, dash_rect, enemy_rect, health_rect):
        current_level = getattr(self.game.level_manager, 'current_level', self.current_level)
        self._draw_label_value(level_rect, 'LEVEL', current_level)

        player = self.game.player
        dash_ready = True
        dash_value = 'READY'
        current_time = pg.time.get_ticks()
        if not player.is_dashing:
            time_since_last_dash = current_time - player.last_dash_time
            if time_since_last_dash < PLAYER_DASH_COOLDOWN:
                dash_ready = False
                dash_left = max(0.0, (PLAYER_DASH_COOLDOWN - time_since_last_dash) / 1000)
                dash_value = f'{dash_left:.1f}s'

        dash_color = self.green_color if dash_ready else self.orange_color
        label_surf = self.label_font.render('DASH', True, self.white)
        self.screen.blit(label_surf, label_surf.get_rect(midtop=(dash_rect.centerx, dash_rect.y + 6)))
        dash_surf = self.dash_font.render(str(dash_value), True, dash_color)
        self.screen.blit(dash_surf, dash_surf.get_rect(center=(dash_rect.centerx, dash_rect.centery + 12)))

        enemies_left = self.get_enemies_left()
        enemy_color = self.green_color if enemies_left == 0 else self.red_color
        self._draw_label_value(enemy_rect, 'ENEMIES', enemies_left, enemy_color)

        current_health = max(0, getattr(player, 'health', 100))
        max_health = max(1, getattr(player, 'max_health', 100))
        ratio = max(0.0, min(1.0, current_health / max_health))
        fill_color = self._get_health_fill_color(ratio)

        label = self.label_font.render('HEALTH', True, self.white)
        self.screen.blit(label, label.get_rect(midtop=(health_rect.centerx, health_rect.y + 6)))

        bar_rect = pg.Rect(health_rect.x + 14, health_rect.y + 36, health_rect.width - 28, 30)
        pg.draw.rect(self.screen, self.health_bg, bar_rect)

        fill_w = int(bar_rect.width * ratio)
        if fill_w > 0:
            pg.draw.rect(self.screen, fill_color, (bar_rect.x, bar_rect.y, fill_w, bar_rect.height))

        pg.draw.rect(self.screen, self.white, bar_rect, 2)

        health_text = self.value_font.render(f'{current_health}/{max_health}', True, self.white)
        self.screen.blit(health_text, health_text.get_rect(center=bar_rect.center))

    def _draw_side_right(self, pickup_rect, ammo_rect, weapon_rect):
        player = self.game.player
        weapon_index = getattr(player, 'current_weapon_index', 0)

        weapon_label = self.label_font.render('WEAPON', True, self.white)
        self.screen.blit(weapon_label, weapon_label.get_rect(midtop=(weapon_rect.centerx, weapon_rect.y + 6)))

        if 0 <= weapon_index < len(self.weapon_icons):
            weapon_icon = self.weapon_icons[weapon_index]
            icon_rect = weapon_icon.get_rect(center=(weapon_rect.centerx, weapon_rect.centery + 12))
            self.screen.blit(weapon_icon, icon_rect)

        weapon = getattr(self.game, 'weapon', None)
        ammo_value = '--/--'
        if weapon:
            ammo_value = f'{weapon.currentMagAmmount}/{weapon.bagAmount}'
        self._draw_label_value(ammo_rect, 'AMMO', ammo_value, self.get_level_tint_color())

        pickup_label = self.label_font.render('PICKUP', True, self.white)
        self.screen.blit(pickup_label, pickup_label.get_rect(midtop=(pickup_rect.centerx, pickup_rect.y + 6)))

        has_item = getattr(player, 'heal_item_count', 0) > 0
        current_time = pg.time.get_ticks()
        heal_cooldown = getattr(player, 'heal_cooldown', 5000)
        last_heal = getattr(player, 'last_heal_time', 0)
        time_since_heal = current_time - getattr(player, 'last_heal_time', 0)
        on_cooldown = last_heal > 0 and time_since_heal < heal_cooldown

        if on_cooldown:
            progress = min(1.0, time_since_heal / heal_cooldown)
            time_left = max(0.0, (heal_cooldown - time_since_heal) / 1000)
            time_surf = self.dash_font.render(f'{time_left:.1f}s', True, self.orange_color)
            self.screen.blit(time_surf, time_surf.get_rect(center=(pickup_rect.centerx, pickup_rect.centery - 4)))

            bar_w = pickup_rect.width - 28
            bar_h = 10
            bar_x = pickup_rect.x + 14
            bar_y = pickup_rect.bottom - 24
            bar_bg = pg.Rect(bar_x, bar_y, bar_w, bar_h)
            pg.draw.rect(self.screen, self.health_bg, bar_bg)
            fill_w = int(bar_w * progress)
            if fill_w > 0:
                pg.draw.rect(self.screen, self.orange_color, (bar_x, bar_y, fill_w, bar_h))
            pg.draw.rect(self.screen, self.white, bar_bg, 1)
        else:
            icon = self.item_icon if has_item else self.item_icon_gray
            icon_rect = icon.get_rect(center=(pickup_rect.centerx, pickup_rect.y + 54))
            self.screen.blit(icon, icon_rect)
        

    def draw_invulnerability_indicator(self):
        if not self.game.player.is_invulnerable:
            return

        seconds_left = max(1, int(self.game.player.invulnerability_time_left / 1000) + 1)
        indicator_x = HALF_WIDTH - 110
        indicator_y = 18
        panel = pg.Rect(indicator_x, indicator_y, 220, 170)

        self.metallic_renderer.draw_panel(panel, 10)

        title_surface = self.invulnerability_title_font.render('INVINCIBILITY', True, self.white)
        title_rect = title_surface.get_rect(center=(panel.centerx, panel.y + 22))
        self.screen.blit(title_surface, title_rect)

        icon_rect = self.powerup_icon.get_rect(center=(panel.centerx, panel.y + 74))
        self.screen.blit(self.powerup_icon, icon_rect)

        tint_color = self.get_level_tint_color()
        timer_surface = self.value_font.render(str(seconds_left), True, tint_color)
        timer_rect = timer_surface.get_rect(center=(panel.centerx - 8, panel.y + 138))
        self.screen.blit(timer_surface, timer_rect)

        sec_text = self.invulnerability_timer_font.render('s', True, self.blue_color)
        sec_rect = sec_text.get_rect(midleft=(timer_rect.right + 4, timer_rect.centery))
        self.screen.blit(sec_text, sec_rect)