import pygame as pg
import os
from Assets.settings import *
from Assets.scripts.UI.ui_level_colors import *
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

        self.tint_color_map = UI_TINT_COLORS

        self.dash_font = load_custom_font(18)
        self.enemy_counter_font = load_custom_font(20)
        self.invulnerability_title_font = load_custom_font(24)
        self.invulnerability_timer_font = load_custom_font(40)

        self.margin_x = int(WIDTH * UI_MARGIN_PERCENT_X)
        self.margin_y = int(HEIGHT * UI_MARGIN_PERCENT_Y)

        self.dash_indicator_width = 180
        self.dash_indicator_height = 24
        self.dash_chamfer_size = 6

        self.current_level = 1
        self.hud_number_font = load_custom_font(48)
        self.hud_big_font = load_custom_font(64)

        self.powerup_icon = self.load_texture('resources/teksture/level1/powerup.png', (100, 100))
        self.item_icon = self.load_texture('resources/teksture/heal_item.png',(128,128))
        self.item_icon_gray = self.make_gray_icon(self.item_icon)

        self.weapon_icon_size = (96, 96)

        self.weapon_icons = [
        self.load_texture('resources/sprites/weapon/pistol_stand.png', self.weapon_icon_size),
        self.load_texture('resources/sprites/weapon/puska_stand.png', self.weapon_icon_size),
        self.load_texture('resources/sprites/weapon/plasma_stand.png', self.weapon_icon_size),
        
        ]
        self.weapon_icons_gray = [self.make_gray_icon(icon) for icon in self.weapon_icons]


        self.crosshair_size = 48
        self.crosshair = self.load_texture('resources/teksture/Blue-crosshair.png', (self.crosshair_size, self.crosshair_size))
        self.crosshair_y_offset = 40
        self.crosshair_pos = (
            HALF_WIDTH - self.crosshair_size // 2,
            HALF_HEIGHT - self.crosshair_size // 2 + self.crosshair_y_offset
        )
        
        self.hit_marker_time = 0
        self.hit_marker_duration = 150


    def load_texture(self, path, res):
        texture_path = resource_path(path)
        texture = pg.image.load(texture_path).convert_alpha()
        return pg.transform.scale(texture, res)


    def draw(self):
        self.draw_player_health()
        self.draw_health_icon(self.game.player.heal_item_count > 0)
        self.draw_weapon_icons()
        self.draw_dash_indicator()
        self.draw_enemy_counter()
        self.draw_invulnerability_indicator()
        self.draw_crosshair()
        self.draw_weapon_ammo()
        self.draw_fps()

    def draw_fps(self):
        fps = str(int(self.game.clock.get_fps()))
        fps_surface = self.enemy_counter_font.render(f"FPS: {fps}", True, (0, 255, 0))
        self.screen.blit(fps_surface, (10, 10))

    def draw_crosshair(self):
        """Draw the crosshair in the center of the screen"""
        if not hasattr(self.game, 'interaction') or not self.game.interaction.is_showing_indicator:
            self.screen.blit(self.crosshair, self.crosshair_pos)
            
            if pg.time.get_ticks() - self.hit_marker_time < self.hit_marker_duration:
                cx = HALF_WIDTH
                cy = HALF_HEIGHT + self.crosshair_y_offset
                color = (255, 255, 255)
                length = 12
                offset = 8
                thickness = 2
                
                pg.draw.line(self.screen, color, (cx - offset, cy - offset), (cx - offset - length, cy - offset - length), thickness)
                pg.draw.line(self.screen, color, (cx + offset, cy - offset), (cx + offset + length, cy - offset - length), thickness)
                pg.draw.line(self.screen, color, (cx - offset, cy + offset), (cx - offset - length, cy + offset + length), thickness)
                pg.draw.line(self.screen, color, (cx + offset, cy + offset), (cx + offset + length, cy + offset + length), thickness)

    def show_hit_marker(self):
        self.hit_marker_time = pg.time.get_ticks()

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
        health = max(0,self.game.player.health)
        tint_color = self.get_level_tint_color()

        health_text = f"{health}/100"
        text_surface = self.hud_big_font.render(health_text,True,tint_color)
        text_rect = text_surface.get_rect(topleft=(self.margin_x, self.margin_y))
        self.screen.blit(text_surface, text_rect)

    def draw_weapon_ammo(self):
        if not self.game.weapon:
            return
        
        weapon = self.game.weapon
        tint_color = self.get_level_tint_color()
        ammo_text =   f"{weapon.currentMagAmmount}/{weapon.bagAmount}"

        text_surface = self.hud_big_font.render(ammo_text, True, tint_color)
        text_rect = text_surface.get_rect(
            bottomright=(
                self.screen.get_width() - self.margin_x,
                self.screen.get_height() - self.margin_y
                )
        )
        self.screen.blit(text_surface, text_rect)

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

        tint_color = self.get_level_tint_color()
        timer_surface = self.hud_big_font.render(str(seconds_left), True, tint_color)
        timer_rect = timer_surface.get_rect(center=(center_x, indicator_y + 155))
        self.screen.blit(timer_surface, timer_rect)

        sec_text = self.invulnerability_timer_font.render("s", True, self.blue_color)
        sec_rect = sec_text.get_rect(midleft=(timer_rect.right + 8, timer_rect.centery))
        self.screen.blit(sec_text, sec_rect)
    
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
        text_surface = self.enemy_counter_font.render(counter_text, True, self.get_level_tint_color())
        text_rect = text_surface.get_rect(bottomleft=(self.margin_x, HEIGHT - self.margin_y))
        self.screen.blit(text_surface, text_rect)

    def update_level(self, level_number):
        if self.current_level != level_number:
            self.current_level = level_number
    
    def get_level_tint_color(self):
        return self.tint_color_map.get(self.current_level, self.tint_color_map["default"])
    
    def draw_health_icon(self, has_item):
        icon = self.item_icon if has_item else self.item_icon_gray
        dash_x = WIDTH - self.dash_indicator_width - self.margin_x
        dash_y = self.margin_y + 30

        spacing = 20  # gap below dash bar
        rect = icon.get_rect()
        rect.topright = (dash_x + self.dash_indicator_width, dash_y + self.dash_indicator_height + spacing)
        self.screen.blit(icon, rect)

    def make_gray_icon(self, surface):
        return pg.transform.grayscale(surface.convert_alpha())
    
    def draw_weapon_icons(self):
        start_x = self.margin_x
        start_y = HEIGHT - self.margin_y - 140
        spacing = 20

        for i, weapon_class in enumerate(self.game.weapon_classes):
            unlocked = self.game.player.weapon_unlocked[i]

            icon = self.weapon_icons[i] if unlocked else self.weapon_icons_gray[i]

            x = start_x + i * (self.weapon_icon_size[0] + spacing)
            y = start_y
            self.screen.blit(icon, (x, y))

            if i == self.game.player.current_weapon_index:
                rect = pg.Rect(x, y, self.weapon_icon_size[0], self.weapon_icon_size[1])
                pg.draw.rect(self.screen, (255, 255, 255), rect, 3)
