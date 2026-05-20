import pygame as pg
from Assets.settings import *
import os
import math
from collections import deque
from Assets.scripts.Util.font_manager import resource_path


_GLOBAL_IMAGE_CACHE = {}


class SpriteObject:
    def __init__(self, game, path=None, pos=(10.5, 3.5), scale=0.7, shift=0.27):
        if path is None:
            path = 'resources/sprites/static_sprites/ukras1.png'

        self.game = game
        self.player = game.player
        self.x, self.y = pos

        try:
            sprite_path = resource_path(path)
            if sprite_path not in _GLOBAL_IMAGE_CACHE:
                _GLOBAL_IMAGE_CACHE[sprite_path] = pg.image.load(sprite_path).convert_alpha()
            self.image = _GLOBAL_IMAGE_CACHE[sprite_path]
        except Exception:
            self.image = pg.Surface((32, 32), pg.SRCALPHA)
            self.image.fill((0, 0, 0, 0))

        self.IMAGE_WIDTH = self.image.get_width()
        self.IMAGE_HALF_WIDTH = self.IMAGE_WIDTH // 2
        self.IMAGE_RATIO = self.IMAGE_WIDTH / max(1, self.image.get_height())

        self.dx = 0
        self.dy = 0
        self.theta = 0
        self.screen_x = 0
        self.dist = 1
        self.norm_dist = 1
        self.sprite_half_width = 0

        self.SPRITE_SCALE = scale
        self.SPRITE_HEIGHT_SHIFT = shift
        self._current_image_id = 0
        self._scaled_image_cache = {}

        self._min_sprite_depth = 0.55
        self._near_cull_distance = 0.35
        self._max_sprite_height = int(HEIGHT * 0.9)
        self._max_sprite_width = int(WIDTH * 0.75)
        self._size_bucket = 16
        self._max_cache_entries = 24

    def _bucket_size(self, value):
        value = max(self._size_bucket, int(value))
        return max(self._size_bucket, round(value / self._size_bucket) * self._size_bucket)

    def get_sprite_projection(self):
        if self.dist <= self._near_cull_distance:
            return

        depth = max(self.norm_dist, self._min_sprite_depth)
        proj = SCREEN_DIST / depth * self.SPRITE_SCALE

        proj_width = round(proj * self.IMAGE_RATIO)
        proj_height = round(proj)

        if proj_width <= 0 or proj_height <= 0:
            return

        proj_width = min(proj_width, self._max_sprite_width)
        proj_height = min(proj_height, self._max_sprite_height)

        proj_width = self._bucket_size(proj_width)
        proj_height = self._bucket_size(proj_height)

        cache_key = (proj_width, proj_height, self._current_image_id)
        image = self._scaled_image_cache.get(cache_key)

        if image is None:
            image = pg.transform.scale(self.image, (proj_width, proj_height))
            self._scaled_image_cache[cache_key] = image

            if len(self._scaled_image_cache) > self._max_cache_entries:
                oldest_key = next(iter(self._scaled_image_cache))
                del self._scaled_image_cache[oldest_key]

        self.sprite_half_width = proj_width // 2
        height_shift = proj_height * self.SPRITE_HEIGHT_SHIFT
        pos = (
            self.screen_x - self.sprite_half_width,
            HALF_HEIGHT - proj_height // 2 + height_shift
        )

        self.game.raycasting.objects_to_render.append((depth, image, pos))

    def get_sprite(self):
        dx = self.x - self.player.x
        dy = self.y - self.player.y
        self.dx, self.dy = dx, dy

        self.theta = math.atan2(dy, dx)
        delta = self.theta - self.player.angle

        while delta > math.pi:
            delta -= math.tau
        while delta < -math.pi:
            delta += math.tau

        self.dist = math.hypot(dx, dy)
        self.norm_dist = self.dist * math.cos(delta)

        if self.norm_dist <= self._min_sprite_depth:
            return

        self.screen_x = HALF_WIDTH + math.tan(delta) * SCREEN_DIST

        if -self.IMAGE_HALF_WIDTH < self.screen_x < (WIDTH + self.IMAGE_HALF_WIDTH):
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
            self.IMAGE_WIDTH = self.image.get_width()
            self.IMAGE_HALF_WIDTH = self.IMAGE_WIDTH // 2
            self.IMAGE_RATIO = self.IMAGE_WIDTH / max(1, self.image.get_height())

    def check_animation_time(self):
        self.animation_trigger = False
        time_now = pg.time.get_ticks()
        if time_now - self.animation_time_prev > self.animation_time:
            self.animation_time_prev = time_now
            self.animation_trigger = True

    def get_images(self, path):
        real_path = resource_path(path)
        if real_path in _GLOBAL_IMAGE_CACHE:
            return deque(_GLOBAL_IMAGE_CACHE[real_path])

        images_list = []
        try:
            if os.path.isdir(real_path):
                for file_name in sorted(os.listdir(real_path)):
                    file_path = os.path.join(real_path, file_name)
                    if os.path.isfile(file_path):
                        try:
                            if file_path not in _GLOBAL_IMAGE_CACHE:
                                _GLOBAL_IMAGE_CACHE[file_path] = pg.image.load(file_path).convert_alpha()
                            images_list.append(_GLOBAL_IMAGE_CACHE[file_path])
                        except Exception:
                            continue
        except Exception:
            pass

        if not images_list:
            blank_img = pg.Surface((32, 32), pg.SRCALPHA)
            blank_img.fill((0, 0, 0, 0))
            images_list.append(blank_img)

        _GLOBAL_IMAGE_CACHE[real_path] = images_list
        return deque(images_list)