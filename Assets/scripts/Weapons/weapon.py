from Assets.scripts.Util.sprite_object import *
from Assets.config.weapon_config import get_weapon_config

class Weapon(AnimatedSprite):
    def __init__(self, game, path='resources/sprites/weapon/pistol/0.png', scale=0.4, animation_time=90, damage=50,magAmount = 1,bagAmount = 10, name='pistol', fire_cooldown=None):
        super().__init__(game=game, path=path, scale=scale, animation_time=animation_time)
        self.images = deque(
            [pg.transform.smoothscale(img, (self.image.get_width() * scale, self.image.get_height() * scale))
             for img in self.images])
        self.image = self.images[0]
        self.weapon_pos = (HALF_WIDTH - self.images[0].get_width() // 2, HEIGHT - self.images[0].get_height())
        #self.is_firing = False
        
        self.is_reloading = False
        self.reload_start_time = 0
        self.reload_duration = 400
        
        self.fire_cooldown = fire_cooldown if fire_cooldown is not None else 300
        self.last_fire_time = -9999
# Remove: self.is_firing, self.frame_counter, self.num_images usage for animation
        self.is_firing = False  # keep for sound/shot logic compatibility

        #self.num_images = len(self.images)
        #self.frame_counter = 0
        self.damage = damage
        self.name = name
        self.accuracy = 1.0
        self.auto_fire = False
        self.maxMagAmount = magAmount
        self.bagAmount = bagAmount
        self.currentMagAmmount = magAmount
        
        #weapon feel
        self.kick_start_time = 0
        self.kick_duration = 80
        self.is_kicking = False
        
    def animate_shot(self):
        elapsed = pg.time.get_ticks() - self.last_fire_time
        if elapsed < self.fire_cooldown:
            # Show fired sprite only for first 40% of cooldown
            if elapsed < self.fire_cooldown * 0.6:
                self.image = self.images[1]
            else:
                self.image = self.images[0]
            self.is_firing = True
            self.game.player.shot = False
        else:
            self.image = self.images[0]
            self.is_firing = False
            
    def can_fire(self):
        return pg.time.get_ticks() - self.last_fire_time >= self.fire_cooldown

    def register_fire(self):
        now = pg.time.get_ticks()
        self.last_fire_time = now
        self.is_kicking = True
        self.kick_start_time = now
        
    
    def draw(self):
        if hasattr(self.game, 'intro_sequence') and self.game.intro_sequence.active:
            return

        image = self.image

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
        elif self.is_kicking:
            elapsed = pg.time.get_ticks() - self.kick_start_time
            progress = min(1.0,elapsed/self.kick_duration)
            
            kick_curve = math.sin(progress * math.pi)
            
            angle = 5 * kick_curve          # slight tilt back
            offset_y = -18 * kick_curve     # jump up (negative = up on screen)
            scale_y = 1.0 - 0.05 * kick_curve  # very subtle squish
            
            w, h = image.get_size()
            transformed = pg.transform.smoothscale(image, (w, int(h * scale_y)))
            transformed = pg.transform.rotate(transformed, angle)
            rect = transformed.get_rect(midbottom=(
                self.weapon_pos[0] + w // 2,
                self.weapon_pos[1] + h + offset_y
            ))
            self.game.screen.blit(transformed, rect)
            
            if progress >= 1.0:
                self.is_kicking = False
        else:
            # Idle sway — gentle floating motion
            t = pg.time.get_ticks() / 1000.0   # seconds
            sway_x = math.sin(t * 1.2) * 3          # slow left-right drift
            sway_y = math.sin(t * 0.8) * 2          # slower up-down bob
            pos = (self.weapon_pos[0] + sway_x, self.weapon_pos[1] + sway_y)
            self.game.screen.blit(image, pos)

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
                         name=config['name'],
                         fire_cooldown=config['fire_cooldown'])
        self.accuracy = config['accuracy']
        self.auto_fire = config['auto_fire']
        self.reload_duration = config.get('reload_duration', 400)
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
                         name=config['name'],
                         fire_cooldown=config['fire_cooldown'])

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
                         name=config['name'],
                         fire_cooldown=config['fire_cooldown'])

        self.accuracy = config['accuracy']
        self.auto_fire = config['auto_fire']

        right_offset = config.get('right_offset', 200)
        self.weapon_pos = (HALF_WIDTH - self.images[0].get_width() // 2 + right_offset,
                          HEIGHT - self.images[0].get_height())

class Bat(Weapon):

    """
    Palica koja je kao meele weapon koji ce bit rare kada smanjimo spawn u settings.py
    4 udarca, zatim palica pukne odnosno nestane dok je ne pokupi opet, one shot je za sve enemyie
    fora je da odjednom moze ubit 3 enemia ako su u rangeu od bat_range koji je trenutno - 3
    """


    def __init__(self, game):
        config = get_weapon_config('bat')

        super().__init__(
            game=game,
            path=config['path'],
            scale=config['scale'],
            animation_time=config['animation_time'],
            damage=config['damage'],
            magAmount=config['magSize'],
            bagAmount=config['bagSize'],
            name=config['name'],
            fire_cooldown=config['fire_cooldown'],
        )

        self.accuracy  = config['accuracy']
        self.auto_fire = config['auto_fire']
        self.max_uses  = config['max_uses']       # 4 udarca pa pukne
        self.uses_left = self.max_uses
        self.bat_range = config['bat_range']      # 1.0 tile
        self.max_targets = config['max_targets']  # 3 odjednom

        
        self.weapon_pos = (
            HALF_WIDTH - self.images[0].get_width() // 2,
            HEIGHT - self.images[0].get_height()
        )

    
    def can_fire(self):
        if self.uses_left <= 0:
            return False
        return pg.time.get_ticks() - self.last_fire_time >= self.fire_cooldown

    def register_fire(self):
        super().register_fire()
        self.uses_left -= 1
        if self.uses_left <= 0:
            self._consume()

   
    def do_melee_hit(self):
        hits = 0
        for npc in list(self.game.object_handler.npc_list):
            if not npc.alive:
                continue
            if hits >= self.max_targets:
                break
            dx = npc.x - self.game.player.x
            dy = npc.y - self.game.player.y
            dist = (dx**2 + dy**2) ** 0.5
            if dist <= self.bat_range:
                npc.health = 0
                npc.pain   = True
                if hasattr(self.game, 'game_ui'):
                    self.game.game_ui.show_hit_marker()
                npc.check_health()
                hits += 1

    
    def _consume(self):
        """Remove bat from player inventory and start spawn lockout."""
        bat_slot = 3
        player = self.game.player

        # Un-equip: switch to any other available weapon
        player.weapon_unlocked[bat_slot] = False
        if player.current_weapon_index == bat_slot:
            switched = False
            for i, w in enumerate(player.weapon_inventory):
                if i != bat_slot and w is not None and player.weapon_unlocked[i]:
                    player.equip_weapon_by_index(i)
                    switched = True
                    break
            if not switched:
                player.current_weapon_index = -1
                self.game.weapon = None

        
        self.game.bat_consumed_time = pg.time.get_ticks() #negira spawnanje novih palica iducih 5 sec
        self.game.sound.play_sfx('bat_break')