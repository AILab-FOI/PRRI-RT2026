import pygame as pg
import math
from Assets.settings import *
from Assets.scripts.Util.font_manager import load_custom_font, resource_path


class ObjectRenderer:
    def draw_text_with_background(self, text, font, color, position, center=False,
                                  bg_color=(0, 0, 0, 150), padding=(20, 10)):
        text_surface = font.render(text, True, color)

        if center:
            text_rect = text_surface.get_rect(center=position)
        else:
            text_rect = text_surface.get_rect(topleft=position)

        bg_rect = text_rect.inflate(padding[0], padding[1])
        bg_surface = pg.Surface((bg_rect.width, bg_rect.height), pg.SRCALPHA)
        bg_surface.fill(bg_color)
        self.screen.blit(bg_surface, bg_rect)
        self.screen.blit(text_surface, text_rect)
        return text_rect

    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.wall_textures = self.load_wall_textures()

        self.sky_images = {
            1: self.get_sky_texture('resources/teksture/level2/sky2.png'),
            2: self.get_sky_texture('resources/teksture/level1/sky1.png'),
            3: self.get_sky_texture('resources/teksture/level2/sky2.png'),
            4: self.get_sky_texture('resources/teksture/level3/sky.png'),
            5: self.get_sky_texture('resources/teksture/level4/sky1.png')
        }
        self.sky_image = self.sky_images[1]

        self._unfolded_width = WIDTH
        self._sky_unfolded = {}
        for lvl, sky_img in self.sky_images.items():
            scaled = pg.transform.scale(sky_img, (WIDTH, HALF_HEIGHT)).convert()
            # Create a seamless texture by mirroring the image horizontally
            seamless = pg.Surface((WIDTH * 2, HALF_HEIGHT)).convert()
            seamless.blit(scaled, (0, 0))
            seamless.blit(pg.transform.flip(scaled, True, False), (WIDTH, 0))
            self._sky_unfolded[lvl] = seamless
            
        self._sky_current = self._sky_unfolded[1]

        self.blood_screen = self.get_texture('resources/teksture/blood_screen.png', RES, alpha=True)
        self.heal_screen = self.get_texture('resources/teksture/heal_screen.png', RES, alpha=True)

        self.damage_alpha = 0
        self.damage_timer = 0
        self.heal_alpha = 0
        self.heal_timer = 0

        self.damage_max_alpha = 224
        self.heal_max_alpha = 196
        self.damage_frame_count = 30
        self.heal_frame_count = 20

        self.damage_frames = self._build_overlay_frames(
            self.blood_screen,
            self.damage_frame_count,
            self.damage_max_alpha,
            curve='ease_out'
        )
        self.heal_frames = self._build_overlay_frames(
            self.heal_screen,
            self.heal_frame_count,
            self.heal_max_alpha,
            curve='ease_in_out'
        )

        self.damage_frame_index = -1
        self.heal_frame_index = -1

        self.game_over_image = self.get_texture('resources/teksture/theEnd.png', RES)
        self.win_image = self.get_texture('resources/teksture/win.png', RES)

        self.message_font = load_custom_font(30)
        self.message = ""
        self.message_time = 0
        self.message_duration = 5000

        self.message_bg_surface = pg.Surface((WIDTH, 80), pg.SRCALPHA)
        self.message_bg_surface.fill((0, 0, 0, 180))
        self.cached_message_surface = None
        self.cached_message_rect = None

    def _build_overlay_frames(self, base_surface, frame_count, max_alpha, curve='linear'):
        frames = []

        for i in range(frame_count):
            if frame_count <= 1:
                progress = 1.0
            else:
                progress = i / (frame_count - 1)

            if curve == 'ease_out':
                alpha_factor = 1.0 - (progress * progress)
            elif curve == 'ease_in_out':
                alpha_factor = (1.0 - progress) * (1.0 - progress)
            else:
                alpha_factor = 1.0 - progress

            alpha = max(0, min(255, int(max_alpha * alpha_factor)))

            frame = base_surface.copy()
            frame.set_alpha(alpha)
            frames.append(frame)

        return frames

    def draw(self):
        self.draw_background()
        self.render_game_objects()
        self.draw_message()

        if 0 <= self.damage_frame_index < len(self.damage_frames):
            self.screen.blit(self.damage_frames[self.damage_frame_index], (0, 0))
            self.damage_alpha = max(0, int(self.damage_max_alpha * (1.0 - (self.damage_frame_index / max(1, len(self.damage_frames) - 1)))))
            self.damage_timer = max(0, len(self.damage_frames) - self.damage_frame_index - 1)
            self.damage_frame_index += 1
        else:
            self.damage_frame_index = -1
            self.damage_alpha = 0
            self.damage_timer = 0

        if 0 <= self.heal_frame_index < len(self.heal_frames):
            self.screen.blit(self.heal_frames[self.heal_frame_index], (0, 0))
            self.heal_alpha = max(0, int(self.heal_max_alpha * (1.0 - (self.heal_frame_index / max(1, len(self.heal_frames) - 1)))))
            self.heal_timer = max(0, len(self.heal_frames) - self.heal_frame_index - 1)
            self.heal_frame_index += 1
        else:
            self.heal_frame_index = -1
            self.heal_alpha = 0
            self.heal_timer = 0

    def win(self):
        self.screen.blit(self.win_image, (0, 0))

    def game_over(self):
        self.screen.blit(self.game_over_image, (0, 0))

    def player_damage(self):
        self.damage_alpha = self.damage_max_alpha
        self.damage_timer = len(self.damage_frames)
        self.damage_frame_index = 0

    def player_heal(self):
        self.heal_alpha = self.heal_max_alpha
        self.heal_timer = len(self.heal_frames)
        self.heal_frame_index = 0

    def show_message(self, text):
        self.message = text
        self.message_time = pg.time.get_ticks()

        margin_y = int(HEIGHT * UI_MARGIN_PERCENT_Y)
        position = (HALF_WIDTH, margin_y + 140)
        self.cached_message_surface = self.message_font.render(text, True, (255, 255, 255))
        self.cached_message_rect = self.cached_message_surface.get_rect(center=position)

    def draw_message(self):
        if self.message and pg.time.get_ticks() - self.message_time < self.message_duration:
            margin_y = int(HEIGHT * UI_MARGIN_PERCENT_Y)
            self.screen.blit(self.message_bg_surface, (0, margin_y + 100))
            if self.cached_message_surface and self.cached_message_rect:
                self.screen.blit(self.cached_message_surface, self.cached_message_rect)

    def update_sky_image(self):
        if hasattr(self.game, 'level_manager'):
            current_level = self.game.level_manager.current_level
            if current_level in self.sky_images:
                self.sky_image = self.sky_images[current_level]
            else:
                self.sky_image = self.sky_images[3]

            if current_level in self._sky_unfolded:
                self._sky_current = self._sky_unfolded[current_level]
            else:
                self._sky_current = self._sky_unfolded.get(3, next(iter(self._sky_unfolded.values())))

    def draw_background(self):
        self.draw_sky()

        floor_color = FLOOR_COLOR
        if hasattr(self.game, 'level_manager'):
            current_level = self.game.level_manager.current_level
            if current_level in FLOOR_COLORS:
                floor_color = FLOOR_COLORS[current_level]

        pg.draw.rect(self.screen, floor_color, (0, HALF_HEIGHT, WIDTH, HALF_HEIGHT))

    def draw_sky(self):
        self.update_sky_image()

        sky = self._sky_current
        
        current_level = 1
        if hasattr(self.game, 'level_manager'):
            current_level = self.game.level_manager.current_level

        sky_w = sky.get_width()
        level_rotation = LEVEL_ROTATION.get(current_level, 0.0)
        angle = self.game.player.angle + level_rotation
        start_x = int((angle / math.tau) * (2 * WIDTH)) % sky_w

        if start_x + WIDTH <= sky_w:
            self.screen.blit(sky, (0, 0), (start_x, 0, WIDTH, HALF_HEIGHT))
        else:
            part1_w = sky_w - start_x
            self.screen.blit(sky, (0, 0), (start_x, 0, part1_w, HALF_HEIGHT))
            self.screen.blit(sky, (part1_w, 0), (0, 0, WIDTH - part1_w, HALF_HEIGHT))

    def render_game_objects(self):
        objs = self.game.raycasting.objects_to_render
        objs.sort(key=lambda t: t[0], reverse=True)
        blit = self.screen.blit
        for _, image, pos in objs:
            blit(image, pos)

    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE), alpha=False):
        texture_path = resource_path(path)
        texture = pg.image.load(texture_path)
        texture = texture.convert_alpha() if alpha else texture.convert()
        return pg.transform.scale(texture, res)

    def get_sky_texture(self, path):
        texture_path = resource_path(path)
        image = pg.image.load(texture_path).convert_alpha()
        w, h = image.get_size()
        new_w = int(w * (HALF_HEIGHT / h))
        return pg.transform.scale(image, (new_w, HALF_HEIGHT))

    def load_wall_textures(self):
        return {
            1: self.get_texture('resources/teksture/1.jpg'),
            2: self.get_texture('resources/teksture/2.jpg'),
            3: self.get_texture('resources/teksture/3.jpg'),
            6: self.get_texture('resources/teksture/6.jpg'),
            7: self.get_texture('resources/teksture/11.png'),
            8: self.get_texture('resources/teksture/8.png'),
            9: self.get_texture('resources/teksture/9.png'),
            10: self.get_texture('resources/teksture/level2/zid1.png'),
            13: self.get_texture('resources/teksture/level2/zid2.png'),
            11: self.get_texture('resources/teksture/vrata1.png'),
            12: self.get_texture('resources/teksture/ukras4.png'),
            14: self.get_texture('resources/teksture/ukras1.png'),
            15: self.get_texture('resources/teksture/novizid1.png'),
            4: self.get_texture('resources/teksture/level2/zid2.png'),
            16: self.get_texture('resources/teksture/level2/vrata1.png'),
            17: self.get_texture('resources/teksture/uvod/zid5.jpg'),
            18: self.get_texture('resources/teksture/level2/zid3.png'),
            19: self.get_texture('resources/teksture/level2/panel.png'),
            20: self.get_texture('resources/teksture/level2/zagonetka1.png'),
            21: self.get_texture('resources/teksture/level2/zagonetka2.png'),
            22: self.get_texture('resources/teksture/level2/zagonetka3.png'),
            23: self.get_texture('resources/teksture/level2/zagonetka4.png'),
            24: self.get_texture('resources/teksture/level2/zid4.png'),
            30: self.get_texture('resources/teksture/level2/vrataPrelaz2.png'),
            31: self.get_texture('resources/teksture/level2/vrataZagonetka.png'),
            25: self.get_texture('resources/teksture/level3/zid2.png'),
            26: self.get_texture('resources/teksture/level3/zid3.png'),
            27: self.get_texture('resources/teksture/level3/zid1.png'),
            28: self.get_texture('resources/teksture/level3/zid4.png'),
            29: self.get_texture('resources/teksture/level3/vrata2.png'),
            32: self.get_texture('resources/teksture/level3/ekstenzije/VrataPrijelaz/0.png'),
            39: self.get_texture('resources/teksture/level3/ekstenzije/VrataPrijelaz/1.png'),
            33: self.get_texture('resources/teksture/uvod/zid1.png'),
            34: self.get_texture('resources/teksture/uvod/zid2.jpg'),
            35: self.get_texture('resources/teksture/uvod/zid3.jpg'),
            36: self.get_texture('resources/teksture/uvod/zid4.jpg'),
            37: self.get_texture('resources/teksture/uvod/zid5.jpg'),
            38: self.get_texture('resources/teksture/uvod/vrata5.png'),
            40: self.get_texture('resources/teksture/level4/zid1.png'),
            41: self.get_texture('resources/teksture/level4/zid2.png'),
            42: self.get_texture('resources/teksture/level4/zid3.png'),
            43: self.get_texture('resources/teksture/level4/zid4.png'),
        }