import pygame as pg
from Assets.settings import *
import os
from collections import deque
from Assets.scripts.Util.font_manager import resource_path


class SpriteObject:
    def __init__(self, game, path=None,
                 pos=(10.5, 3.5), scale=0.7, shift=0.27):
        if path is None:
            path = 'resources/sprites/static_sprites/ukras1.png'
        self.game = game
        self.player = game.player
        self.x, self.y = pos

        try:
            sprite_path = resource_path(path)
            self.image = pg.image.load(sprite_path).convert_alpha()
        except Exception:
            self.image = pg.Surface((32, 32), pg.SRCALPHA)
            self.image.fill((0, 0, 0, 0))

        self.IMAGE_WIDTH = self.image.get_width()
        self.IMAGE_HALF_WIDTH = self.IMAGE_WIDTH // 2
        self.IMAGE_RATIO = self.IMAGE_WIDTH / self.image.get_height()
        self.dx, self.dy, self.theta, self.screen_x, self.dist, self.norm_dist = 0, 0, 0, 0, 1, 1
        self.sprite_half_width = 0
        self.SPRITE_SCALE = scale
        self.SPRITE_HEIGHT_SHIFT = shift
        self._current_image_id = 0
        self._scaled_image_cache = {}

    def get_sprite_projection(self):
        proj = SCREEN_DIST / self.norm_dist * self.SPRITE_SCALE
        proj_width, proj_height = proj * self.IMAGE_RATIO, proj

        proj_width = round(proj_width)
        proj_height = round(proj_height)

        cache_key = (proj_width, proj_height, self._current_image_id)

        if cache_key not in self._scaled_image_cache:
            scaled_image = pg.transform.scale(self.image, (proj_width, proj_height))
            self._scaled_image_cache[cache_key] = scaled_image

            # Limit cache size to prevent memory issues
            if len(self._scaled_image_cache) > 10:
                oldest_key = next(iter(self._scaled_image_cache))
                del self._scaled_image_cache[oldest_key]

        image = self._scaled_image_cache[cache_key]

        self.sprite_half_width = proj_width // 2
        height_shift = proj_height * self.SPRITE_HEIGHT_SHIFT
        pos = self.screen_x - self.sprite_half_width, HALF_HEIGHT - proj_height // 2 + height_shift

        self.game.raycasting.objects_to_render.append((self.norm_dist, image, pos))

    def get_sprite(self):
        dx = self.x - self.player.x
        dy = self.y - self.player.y
        self.dx, self.dy = dx, dy
        self.theta = math.atan2(dy, dx)

        delta = self.theta - self.player.angle
        if (dx > 0 and self.player.angle > math.pi) or (dx < 0 and dy < 0):
            delta += math.tau

        delta_rays = delta / DELTA_ANGLE
        self.screen_x = (HALF_NUM_RAYS + delta_rays) * SCALE

        self.dist = math.hypot(dx, dy)
        self.norm_dist = self.dist * math.cos(delta)
        if -self.IMAGE_HALF_WIDTH < self.screen_x < (WIDTH + self.IMAGE_HALF_WIDTH) and self.norm_dist > 0.5:
            self.get_sprite_projection()

    def update(self):
        self.get_sprite()


class AnimatedSprite(SpriteObject):
    def __init__(self, game, path='resources/sprites/animated_sprites/green_light/0.png',
                 pos=(11.5, 3.5), scale=0.8, shift=0.16, animation_time=120):
        super().__init__(game, path, pos, scale, shift)
        self.animation_time = animation_time
        self.path = path.rsplit('/', 1)[0]
        self.images = self.get_images(self.path)
        self.animation_time_prev = pg.time.get_ticks()
        self.animation_trigger = False

    def update(self):
        super().update()
        self.check_animation_time()
        self.animate(self.images)

    def animate(self, images):
        if self.animation_trigger:
            images.rotate(-1)
            self.image = images[0]
            self._current_image_id += 1
            self._scaled_image_cache = {}

    def check_animation_time(self):
        self.animation_trigger = False
        time_now = pg.time.get_ticks()
        if time_now - self.animation_time_prev > self.animation_time:
            self.animation_time_prev = time_now
            self.animation_trigger = True

    def get_images(self, path):
        images = deque()
        try:
            real_path = resource_path(path)
            if os.path.isdir(real_path):
                for file_name in sorted(os.listdir(real_path)):
                    file_path = os.path.join(real_path, file_name)
                    if os.path.isfile(file_path):
                        try:
                            img = pg.image.load(file_path).convert_alpha()
                            images.append(img)
                        except Exception:
                            continue
        except Exception:
            pass

        if not images:
            blank_img = pg.Surface((32, 32), pg.SRCALPHA)
            blank_img.fill((0, 0, 0, 0))
            images.append(blank_img)

        return images
