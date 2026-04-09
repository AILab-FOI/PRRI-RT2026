from Assets.scripts.Util.sprite_object import *
from Assets.config.weapon_config import get_weapon_config

class Weapon(AnimatedSprite):
    def __init__(self, game, path='resources/sprites/weapon/pistol/0.png', scale=0.4, animation_time=90, damage=50,magAmount = 1,bagAmount = 10, name='pistol'):
        super().__init__(game=game, path=path, scale=scale, animation_time=animation_time)
        self.images = deque(
            [pg.transform.smoothscale(img, (self.image.get_width() * scale, self.image.get_height() * scale))
             for img in self.images])
        self.weapon_pos = (HALF_WIDTH - self.images[0].get_width() // 2, HEIGHT - self.images[0].get_height())
        self.is_firing = False
        self.is_reloading = False
        
        self.reload_start_time = 0
        self.reload_duration = 400

        self.num_images = len(self.images)
        self.frame_counter = 0
        self.damage = damage
        self.name = name
        self.accuracy = 1.0
        self.auto_fire = False
        self.maxMagAmount = magAmount
        self.bagAmount = bagAmount
        self.currentMagAmmount = magAmount

    def animate_shot(self):
        if self.is_firing:
            self.game.player.shot = False
            if self.animation_trigger:
                self.images.rotate(-1)
                self.image = self.images[0]
                self.frame_counter += 1
                if self.frame_counter == self.num_images:
                    self.is_firing = False
                    self.frame_counter = 0

    def draw(self):
        if hasattr(self.game, 'intro_sequence') and self.game.intro_sequence.active:
            return

        image = self.images[0]

        if self.is_reloading:
            elapsed = pg.time.get_ticks() - self.reload_start_time
            progress = min(1.0, elapsed / self.reload_duration)

            angle = -35 * math.sin(progress * math.pi)
            scale_x = 1.0 - 0.25 * math.sin(progress * math.pi)
            offset_y = 60 * math.sin(progress * math.pi)

            w, h = image.get_size()
            transformed = pg.transform.smoothscale(image, (int(w * scale_x), h))
            transformed = pg.transform.rotate(transformed, angle)
            rect = transformed.get_rect(midbottom=(self.weapon_pos[0] + w // 2,
                                               self.weapon_pos[1] + h + offset_y))
            self.game.screen.blit(transformed, rect)

            if progress >= 1.0:
                self.is_reloading = False
        else:
            self.game.screen.blit(image, self.weapon_pos)

    def draw_transformed(self, image, pos, angle=0, scale_x=1.0, scale_y=1.0):
        w, h = image.get_size()
        transformed = pg.transform.smoothscale(image, (int(w * scale_x), int(h * scale_y)))
        transformed = pg.transform.rotate(transformed, angle)
        rect = transformed.get_rect(midbottom=(pos[0] + w // 2, pos[1] + h))
        self.game.screen.blit(transformed, rect)

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
                         magAmount=config['magSize'],
                         bagAmount=config['bagSize'],
                         name=config['name'],)
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
                         magAmount=config['magSize'],
                         bagAmount=config['bagSize'],
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
                         magAmount=config['magSize'],
                         bagAmount=config['bagSize'],
                         name=config['name'])

        self.accuracy = config['accuracy']
        self.auto_fire = config['auto_fire']

        right_offset = config.get('right_offset', 200)
        self.weapon_pos = (HALF_WIDTH - self.images[0].get_width() // 2 + right_offset,
                          HEIGHT - self.images[0].get_height())