from Assets.scripts.Util.sprite_object import AnimatedSprite
from random import randint, random
import math
from Assets.settings import *


class StaticNPC(AnimatedSprite):
    def __init__(self, game, path='resources/sprites/npc/dialogue_npc/0.png', pos=(10.5, 5.5),
                 scale=0.6, shift=0.38, animation_time=180):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.size = 20
        self.alive = True
        idle_images = self.get_images(self.path + '/idle')
        if idle_images and len(idle_images) > 0:
            self.static_image = idle_images[0]
        else:
            self.static_image = self.image
        self.image = self.static_image

    def update(self):
        self.check_animation_time()
        self.get_sprite()
        self.run_logic()

    def run_logic(self):
        if self.alive:
            self.image = self.static_image

    def get_distance_to_player(self):
        """Calculate the direct distance to the player (no ray casting)"""
        return ((self.game.player.x - self.x) ** 2 + (self.game.player.y - self.y) ** 2) ** 0.5

    @property
    def map_pos(self):
        return int(self.x), int(self.y)


class NPC(AnimatedSprite):
    def __init__(self, game, path='resources/sprites/npc/soldier/0.png', pos=(10.5, 5.5),
                 scale=0.6, shift=0.38, animation_time=180, config=None):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.config = {
            'attack_dist': randint(3, 6),
            'speed': 0.03,
            'size': 20,
            'health': 100,
            'attack_damage': 10,
            'accuracy': 0.15,
            'death_height_shift': 0.5,
            'behavior': 'basic',
            'sounds': {
                'attack': 'npc_attack',
                'pain': 'npc_pain',
                'death': 'npc_death'
            }
        }
        if config:
            self._update_config_recursive(self.config, config)
        self._load_animations()
        self.attack_dist = self.config['attack_dist']
        self.speed = self.config['speed']
        self.size = self.config['size']
        self.health = self.config['health']
        self.attack_damage = self.config['attack_damage']
        self.accuracy = self.config['accuracy']
        self.death_height_shift = self.config['death_height_shift']
        self.behavior = self.config['behavior']
        self.alive = True
        self.pain = False
        self.ray_cast_value = False
        self.death_frame = 0
        self.player_search_trigger = False
        self.play_death_sound = False
        self.death_sound_delay = 0

    def _update_config_recursive(self, target, source):
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_config_recursive(target[key], value)
            else:
                target[key] = value

    def _load_animations(self):
        self.attack_images = self.get_images(self.path + '/attack')
        self.death_images = self.get_images(self.path + '/death')
        self.idle_images = self.get_images(self.path + '/idle')
        self.pain_images = self.get_images(self.path + '/pain')
        self.walk_images = self.get_images(self.path + '/walk')

    def update(self):
        self.check_animation_time()
        self.get_sprite()
        self.run_logic()

    def check_wall(self, x, y):
        return (x, y) not in self.game.map.world_map

    def check_wall_collision(self, dx, dy):
        if self.check_wall(int(self.x + dx * self.size), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * self.size)):
            self.y += dy

    def movement(self):
        next_pos = self.game.pathfinding.get_next_step(self.map_pos)
        next_x, next_y = next_pos
        if next_pos not in self.game.object_handler.npc_positions:
            angle = math.atan2(next_y + 0.5 - self.y, next_x + 0.5 - self.x)
            dx = math.cos(angle) * self.speed
            dy = math.sin(angle) * self.speed
            self.check_wall_collision(dx, dy)

    def attack(self):
        if self.animation_trigger:
            sound_name = self.config['sounds']['attack']
            if hasattr(self.game.sound, sound_name):
                getattr(self.game.sound, sound_name).play()
            if random() < self.accuracy:
                self.game.player.get_damage(self.attack_damage)

    def animate_death(self):
        if not self.alive:
            if self.play_death_sound:
                self.death_sound_delay -= 1
                if self.death_sound_delay <= 0:
                    sound_name = self.config['sounds']['death']
                    if hasattr(self.game.sound, sound_name):
                        getattr(self.game.sound, sound_name).play()
                    self.play_death_sound = False

            if self.animation_trigger and self.death_frame < len(self.death_images) - 1:
                self.death_frame += 1
                self.image = self.death_images[self.death_frame]
                if hasattr(self, '_current_image_id'):
                    self._current_image_id += 1
                else:
                    self._current_image_id = 0
                if hasattr(self, '_scaled_image_cache'):
                    self._scaled_image_cache = {}

    def animate_pain(self):
        self.animate(self.pain_images)
        if self.animation_trigger:
            self.pain = False

    def check_hit_in_npc(self):
        if self.ray_cast_value and self.game.player.shot:
            if HALF_WIDTH - self.sprite_half_width < self.screen_x < HALF_WIDTH + self.sprite_half_width:
                sound_name = self.config['sounds']['pain']
                if hasattr(self.game.sound, sound_name):
                    getattr(self.game.sound, sound_name).play()
                self.game.player.shot = False
                self.pain = True
                self.health -= self.game.weapon.damage
                
                if hasattr(self.game, 'game_ui'):
                    self.game.game_ui.show_hit_marker()
                    
                self.check_health()

    def check_health(self):
        if self.health < 1 and self.alive:
            self.alive = False
            self.play_death_sound = True
            self.death_sound_delay = 5
            self.death_frame = 0
            self.SPRITE_HEIGHT_SHIFT = self.death_height_shift

            self.image = self.death_images[0]
            if hasattr(self, '_current_image_id'):
                self._current_image_id += 1
            else:
                self._current_image_id = 0
            if hasattr(self, '_scaled_image_cache'):
                self._scaled_image_cache = {}

    def run_logic(self):
        if not self.alive:
            self.animate_death()
            return
        self.ray_cast_value = self.ray_cast_player_npc()
        self.check_hit_in_npc()
        if self.pain:
            self.animate_pain()
            return
        if self.behavior == 'ranged':
            self._run_ranged_behavior()
        elif self.behavior == 'melee':
            self._run_melee_behavior()
        else:
            self._run_basic_behavior()

    def _run_basic_behavior(self):
        if self.ray_cast_value:
            self.player_search_trigger = True
            if self.dist < self.attack_dist:
                self.animate(self.attack_images)
                self.attack()
            else:
                self.animate(self.walk_images)
                self.movement()
        elif self.player_search_trigger:
            self.animate(self.walk_images)
            self.movement()
        else:
            self.animate(self.idle_images)

    def _run_ranged_behavior(self):
        if self.ray_cast_value:
            self.player_search_trigger = True
            if self.dist < self.attack_dist * 0.5:
                self._retreat_from_player()
            elif self.dist < self.attack_dist:
                self.animate(self.attack_images)
                self.attack()
            else:
                self.animate(self.walk_images)
                self.movement()
        elif self.player_search_trigger:
            self.animate(self.walk_images)
            self.movement()
        else:
            self.animate(self.idle_images)

    def _run_melee_behavior(self):
        if self.ray_cast_value:
            self.player_search_trigger = True
            if self.dist < self.attack_dist:
                self.animate(self.attack_images)
                self.attack()
            else:
                self.speed = self.config['speed'] * 1.2
                self.animate(self.walk_images)
                self.movement()
        elif self.player_search_trigger:
            self.speed = self.config['speed']
            self.animate(self.walk_images)
            self.movement()
        else:
            self.animate(self.idle_images)

    def _retreat_from_player(self):
        angle = math.atan2(self.y - self.game.player.y, self.x - self.game.player.x)
        dx = math.cos(angle) * self.speed
        dy = math.sin(angle) * self.speed
        self.check_wall_collision(dx, dy)
        self.animate(self.walk_images)

    @property
    def map_pos(self):
        return int(self.x), int(self.y)

    def ray_cast_player_npc(self):
        if self.game.player.map_pos == self.map_pos:
            return True

        wall_dist_v, wall_dist_h = 0, 0
        player_dist_v, player_dist_h = 0, 0

        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos

        ray_angle = self.theta

        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        EPSILON = 1e-6
        sin_a = sin_a if abs(sin_a) > EPSILON else EPSILON * (1 if sin_a >= 0 else -1)
        cos_a = cos_a if abs(cos_a) > EPSILON else EPSILON * (1 if cos_a >= 0 else -1)

        # Check horizontal lines
        y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)
        depth_hor = (y_hor - oy) / sin_a
        x_hor = ox + depth_hor * cos_a
        delta_depth = dy / sin_a
        dx = delta_depth * cos_a

        for _ in range(MAX_DEPTH):
            tile_hor = int(x_hor), int(y_hor)
            if tile_hor == self.map_pos:
                player_dist_h = depth_hor
                break
            if tile_hor in self.game.map.world_map:
                wall_dist_h = depth_hor
                break
            x_hor += dx
            y_hor += dy
            depth_hor += delta_depth

        # Check vertical lines
        x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)
        depth_vert = (x_vert - ox) / cos_a
        y_vert = oy + depth_vert * sin_a
        delta_depth = dx / cos_a
        dy = delta_depth * sin_a

        for _ in range(MAX_DEPTH):
            tile_vert = int(x_vert), int(y_vert)
            if tile_vert == self.map_pos:
                player_dist_v = depth_vert
                break
            if tile_vert in self.game.map.world_map:
                wall_dist_v = depth_vert
                break
            x_vert += dx
            y_vert += dy
            depth_vert += delta_depth

        player_dist = max(player_dist_v, player_dist_h)
        wall_dist = max(wall_dist_v, wall_dist_h)

        if 0 < player_dist < wall_dist or not wall_dist:
            return True
        return False
