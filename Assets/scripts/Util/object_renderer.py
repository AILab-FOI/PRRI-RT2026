import pygame as pg
from Assets.settings import *
from Assets.scripts.Util.font_manager import load_custom_font, resource_path


class ObjectRenderer:
    def draw_text_with_background(self, text, font, color, position, center=False, bg_color=(0, 0, 0, 150), padding=(20, 10)):
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
            4: self.get_sky_texture('resources/teksture/level3/sky.png',),
            5: self.get_sky_texture('resources/teksture/level4/sky1.png')
        }
        self.sky_image = self.sky_images[1]

        # Pre-scale sky panoramas to full unfolded width so draw_sky
        # never needs pg.transform.scale per frame (major perf win).
        self._unfolded_width = int(WIDTH * math.tau / FOV)
        self._sky_unfolded = {}
        for lvl, sky_img in self.sky_images.items():
            self._sky_unfolded[lvl] = pg.transform.scale(
                sky_img, (self._unfolded_width, HALF_HEIGHT)
            ).convert()
        self._sky_current = self._sky_unfolded[1]


        self.blood_screen = self.get_texture('resources/teksture/blood_screen.png', RES, alpha=True)
        self.damage_alpha = 0
        self.damage_timer = 0
        self.heal_screen = self.get_texture('resources/teksture/heal_screen.png', RES, alpha=True)
        self.heal_alpha = 0
        self.heal_timer = 0
        self.game_over_image = self.get_texture('resources/teksture/theEnd.png', RES)
        self.win_image = self.get_texture('resources/teksture/win.png', RES)
        self.message_font = load_custom_font(30)
        self.message = ""
        self.message_time = 0
        self.message_duration = 5000

    def draw(self):
        self.draw_background()
        self.render_game_objects()
        self.draw_message()

        if self.damage_timer > 0:
            overlay = self.blood_screen.copy()
            overlay.set_alpha(self.damage_alpha)
            self.screen.blit(overlay, (0, 0))
            self.damage_alpha -= 12
            self.damage_timer -= 1

        if self.heal_timer > 0:
            overlay = self.heal_screen.copy()
            overlay.set_alpha(self.heal_alpha)
            self.screen.blit(overlay, (0, 0))
            self.heal_alpha -= 4
            self.heal_timer -= 1

    def win(self):
        self.screen.blit(self.win_image, (0, 0))

    def game_over(self):
        self.screen.blit(self.game_over_image, (0, 0))

    def player_damage(self):
        self.damage_alpha = 224   # transparentnost slike
        self.damage_timer = 30    # koliko frameova je na ekranu

    def player_heal(self):
        self.heal_alpha = 256
        self.heal_timer = 60

    def show_message(self, text):
        self.message = text
        self.message_time = pg.time.get_ticks()

    def draw_message(self):
        if self.message and pg.time.get_ticks() - self.message_time < self.message_duration:
            margin_y = int(HEIGHT * UI_MARGIN_PERCENT_Y)

            bg_surface = pg.Surface((WIDTH, 80), pg.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))
            self.screen.blit(bg_surface, (0, margin_y + 100))

            position = (HALF_WIDTH, margin_y + 140)
            text_surface = self.message_font.render(self.message, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=position)
            self.screen.blit(text_surface, text_rect)

    def update_sky_image(self):
        if hasattr(self.game, 'level_manager'):
            current_level = self.game.level_manager.current_level
            if current_level in self.sky_images:
                self.sky_image = self.sky_images[current_level]
            else:
                self.sky_image = self.sky_images[3]
            # Update fast-path unfolded sky reference
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
        sky_w = self._unfolded_width

        current_level = 1
        if hasattr(self.game, 'level_manager'):
            current_level = self.game.level_manager.current_level

        level_rotation = LEVEL_ROTATION.get(current_level, 0.0)
        left_angle = (self.game.player.angle - HALF_FOV + level_rotation) % math.tau
        start_x = int((left_angle / math.tau) * sky_w) % sky_w

        # Fast path: just blit a WIDTH-wide region, no scaling needed
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
            #1. level
            1: self.get_texture('resources/teksture/1.jpg'),
            2: self.get_texture('resources/teksture/2.jpg'),
            3: self.get_texture('resources/teksture/3.jpg'),

            6: self.get_texture('resources/teksture/6.jpg'),
            7: self.get_texture('resources/teksture/11.png'),
            8: self.get_texture('resources/teksture/8.png'),
            9: self.get_texture('resources/teksture/9.png'),
            10: self.get_texture('resources/teksture/level2/zid1.png'),
            13: self.get_texture('resources/teksture/level2/zid2.png'),

            11: self.get_texture('resources/teksture/vrata1.png'), ## vrata crna zatvorena
            12: self.get_texture('resources/teksture/ukras4.png'), ## ne korišteno warning terminal

            14: self.get_texture('resources/teksture/ukras1.png'), ## panel za level 1 crno sivi
            15: self.get_texture('resources/teksture/novizid1.png'), ## novo test

            #2. level
            4: self.get_texture('resources/teksture/level2/zid2.png'), ## bijeli zid level 1 / level 2 - prijelaz/vanjski
            16: self.get_texture('resources/teksture/level2/vrata1.png'), ##vrata bijela zatvorena
            17: self.get_texture('resources/teksture/uvod/zid5.jpg'), ## zid sa malo krvi (manje od uvod/zid1)
            18: self.get_texture('resources/teksture/level2/zid3.png'), ##zid s kockama sobe
            19: self.get_texture('resources/teksture/level2/panel.png'), ## bijeli panel

            20: self.get_texture('resources/teksture/level2/zagonetka1.png'), ## Zid sa Ultimate
            21: self.get_texture('resources/teksture/level2/zagonetka2.png'), ## Zid sa Six 6
            22: self.get_texture('resources/teksture/level2/zagonetka3.png'), ## Zid sa Multiply
            23: self.get_texture('resources/teksture/level2/zagonetka4.png'), ## Zid sa Seven 7

            24: self.get_texture('resources/teksture/level2/zid4.png'), ## bijeli zid s drugacijim paternom
            30: self.get_texture('resources/teksture/level2/vrataPrelaz2.png'), ## završna vrata na levelu 2
            31: self.get_texture('resources/teksture/level2/vrataZagonetka.png'), ## vrata za zagonetku

            #3. level
            25: self.get_texture('resources/teksture/level3/zid2.png'), ## glavni zid za mapu žučkast
            26: self.get_texture('resources/teksture/level3/zid3.png'), ## sporedni zid za mapu žučkast sa bačvama
            27: self.get_texture('resources/teksture/level3/zid1.png'), ## labaratorijski zid sa najviše detalja alien
            28: self.get_texture('resources/teksture/level3/zid4.png'), ## labaratorijski zid sa manje detalja biljka
            29: self.get_texture('resources/teksture/level3/vrata2.png'), ## žučkasta vrata za mapu lagano otvorena
            32: self.get_texture('resources/teksture/level3/ekstenzije/VrataPrijelaz/0.png'),
            39: self.get_texture('resources/teksture/level3/ekstenzije/VrataPrijelaz/1.png'), #vrata prijelaz na sljedeci level


            #uvodni level
            33: self.get_texture('resources/teksture/uvod/zid1.png'), #bijeli zid crvena svjetla manja količina krvi u sredini
            34: self.get_texture('resources/teksture/uvod/zid2.jpg'), #bijeli zid s srednjom količinom krvi
            35: self.get_texture('resources/teksture/uvod/zid3.jpg'), #bijeli zid s velikom količinom krvi
            36: self.get_texture('resources/teksture/uvod/zid4.jpg'), #bijeli zid s krvavom rukom u sredini
            37: self.get_texture('resources/teksture/uvod/zid5.jpg'), #bijeli zid s manjom količinom krvi niže od prvog zida
            38: self.get_texture('resources/teksture/uvod/vrata5.png'),

            #boss level (zadnji level)
            40: self.get_texture('resources/teksture/level4/zid1.png'), #base zid
            41: self.get_texture('resources/teksture/level4/zid2.png'), #base zid sa malim prozorom
            42: self.get_texture('resources/teksture/level4/zid3.png'), #base zid s konzolom i prozor
            43: self.get_texture('resources/teksture/level4/zid4.png'), #base zid s velikim prozorom


        }
