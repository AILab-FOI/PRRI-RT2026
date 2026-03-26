from Assets.scripts.Util.sprite_object import *
from Assets.config.weapon_config import get_weapon_config

class Weapon(AnimatedSprite):
    def __init__(self, game, path='resources/sprites/weapon/pistol/0.png', scale=0.4, animation_time=90, damage=50, name='pistol'):
        super().__init__(game=game, path=path, scale=scale, animation_time=animation_time)
        self.images = deque(
            [pg.transform.smoothscale(img, (self.image.get_width() * scale, self.image.get_height() * scale))
             for img in self.images])
        self.weapon_pos = (HALF_WIDTH - self.images[0].get_width() // 2, HEIGHT - self.images[0].get_height())
        self.reloading = False
        self.num_images = len(self.images)
        self.frame_counter = 0
        self.damage = damage
        self.name = name
        self.accuracy = 1.0
        self.auto_fire = False

    def animate_shot(self):
        if self.reloading:
            self.game.player.shot = False
            if self.animation_trigger:
                self.images.rotate(-1)
                self.image = self.images[0]
                if hasattr(self, '_current_image_id'):
                    self._current_image_id += 1
                else:
                    self._current_image_id = 0
                if hasattr(self, '_scaled_image_cache'):
                    self._scaled_image_cache = {}
                self.frame_counter += 1
                if self.frame_counter == self.num_images:
                    self.reloading = False
                    self.frame_counter = 0

    def draw(self):
        if hasattr(self.game, 'intro_sequence') and self.game.intro_sequence.active:
            return

        self.game.screen.blit(self.images[0], self.weapon_pos)

    def update(self):
        self.check_animation_time()
        self.animate_shot()


class SMG(Weapon):
    def __init__(self, game):
        config = get_weapon_config('smg')

        super().__init__(game=game,
                         path=config['path'],
                         scale=config['scale'],
                         animation_time=config['animation_time'],
                         damage=config['damage'],
                         name=config['name'])
        self.accuracy = config['accuracy']
        self.auto_fire = config['auto_fire']

        right_offset = config.get('right_offset', 230)
        self.weapon_pos = (HALF_WIDTH - self.images[0].get_width() // 2 + right_offset,
                          HEIGHT - self.images[0].get_height())

class Pistol(Weapon):
    def __init__(self, game):
        config = get_weapon_config('pistol')

        super().__init__(game=game,
                         path=config['path'],
                         scale=config['scale'],
                         animation_time=config['animation_time'],
                         damage=config['damage'],
                         name=config['name'])

        self.accuracy = config['accuracy']
        self.auto_fire = config['auto_fire']

        self.weapon_pos = (HALF_WIDTH - self.images[0].get_width() // 2,
                          HEIGHT - self.images[0].get_height())

class PlasmaGun(Weapon):
    def __init__(self, game):
        config = get_weapon_config('plasmagun')

        super().__init__(game=game,
                         path=config['path'],
                         scale=config['scale'],
                         animation_time=config['animation_time'],
                         damage=config['damage'],
                         name=config['name'])

        self.accuracy = config['accuracy']
        self.auto_fire = config['auto_fire']

        right_offset = config.get('right_offset', 200)
        self.weapon_pos = (HALF_WIDTH - self.images[0].get_width() // 2 + right_offset,
                          HEIGHT - self.images[0].get_height())