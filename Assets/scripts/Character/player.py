from Assets.settings import *
import pygame as pg
import math
from Assets.config.weapon_config import get_weapon_config

class Player:
    def __init__(self, game):
        self.game = game
        self.x, self.y = PLAYER_POS
        self.angle = PLAYER_ANGLE
        self.shot = False
        self.health = PLAYER_MAX_HEALTH
        self.rel = 0
        #self.health_recovery_delay = 700
        self.time_prev = pg.time.get_ticks()

        self.is_dashing = False
        self.dash_direction = (0, 0)
        self.dash_start_time = 0
        self.last_dash_time = 0

        self.dialogue_mode = False

        self.auto_fire = False
        self.auto_fire_delay = 150
        self.last_auto_fire_time = 0

        self.is_invulnerable = False
        self.invulnerability_start_time = 0
        self.invulnerability_time_left = 0
        

        self.last_heal_time = 0
        self.heal_cooldown = 5000  # 5 sekundi
        self.heal_item_count = 0

        self.last_step_time = 0 #timeri za hodanje za zvukove
        self.step_delay = 350

        self.vel_x = 0
        self.vel_y = 0
        self.friction = 0.8
        self.acceleration = 0.9
        
        
        
        

    """ def recover_health(self):
        if self.check_health_recovery_delay() and self.health < PLAYER_MAX_HEALTH:
            self.health += 1 """

    """ def check_health_recovery_delay(self):
        time_now = pg.time.get_ticks()
        if time_now - self.time_prev > self.health_recovery_delay:
            self.time_prev = time_now
            return True """

    def check_game_over(self):
        if self.health < 1:
            self.game.death_screen.start()

    def get_damage(self, damage):
        if self.is_invulnerable:
            return

        self.health -= damage
        self.game.object_renderer.player_damage()
        self.game.sound.igrac_damage.play()
        self.check_game_over()

    def single_fire_event(self, event):
        if self.dialogue_mode or (hasattr(self.game, 'intro_sequence') and self.game.intro_sequence.active):
            return
        
        if not hasattr(self.game, 'weapon') or self.game.weapon is None:
            return

        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and not self.shot and not self.game.weapon.is_reloading:
                if hasattr(self.game.weapon, 'auto_fire') and self.game.weapon.auto_fire:
                    self.auto_fire = True
                    weapon_config = get_weapon_config(self.game.weapon.name)
                    if weapon_config and 'auto_fire_delay' in weapon_config:
                        self.auto_fire_delay = weapon_config['auto_fire_delay']
                self.fire_weapon()

        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                self.auto_fire = False
                

    def fire_weapon(self):
        if not hasattr(self.game, 'weapon') or self.game.weapon is None:
            return

        weapon_config = get_weapon_config(self.game.weapon.name)

        if self.game.weapon.is_reloading:
            return
    
        if(self.game.weapon.currentMagAmmount <= 0):
            return
        
        if weapon_config and 'sound' in weapon_config:
            sound_name = weapon_config['sound']
            if hasattr(self.game.sound, sound_name):
                getattr(self.game.sound, sound_name).play()
        else:
            if self.game.weapon.name == 'smg':
                self.game.sound.smg.play()
            else:
                self.game.sound.pistolj.play()

        self.shot = True
        self.game.weapon.is_firing = True
        self.game.weapon.currentMagAmmount -= 1
        self.last_auto_fire_time = pg.time.get_ticks()

    def reload_weapon(self):
        if not hasattr(self.game, 'weapon') or self.game.weapon is None:
            return

        weapon_config = get_weapon_config(self.game.weapon.name)
        if self.game.weapon.bagAmount <= 0 or self.game.weapon.currentMagAmmount == self.game.weapon.maxMagAmount:
            return False
        
        missing_ammo = self.game.weapon.maxMagAmount - self.game.weapon.currentMagAmmount
        ammo_to_reload = min(missing_ammo, self.game.weapon.bagAmount)

        self.game.weapon.is_reloading = True
        self.game.weapon.reload_start_time = pg.time.get_ticks()

        self.game.weapon.currentMagAmmount += ammo_to_reload
        self.game.weapon.bagAmount -= ammo_to_reload



    def try_heal(self):
        current_time = pg.time.get_ticks()
        if (self.heal_item_count > 0 and self.health < PLAYER_MAX_HEALTH and
            current_time - self.last_heal_time >= self.heal_cooldown):
                self.health = min(self.health + 20, PLAYER_MAX_HEALTH)
                self.heal_item_count -= 1
                self.game.sound.heal.play()
                self.game.object_renderer.player_heal()

                self.last_heal_time = current_time

    """
    def heal_player(self):
        current_time = pg.time.get_ticks()

        if self.health >= PLAYER_MAX_HEALTH:
            return False

        if current_time - self.last_heal_time < self.heal_cooldown:
            return False

        self.health = min(self.health + PLAYER_BASE_HEAL, PLAYER_MAX_HEALTH)
        self.last_heal_time = current_time
        return True
        """
    
    def try_addAmmo(self,amount):
        if not hasattr(self.game, 'weapon') or self.game.weapon is None:
            return False

        if self.game.weapon.bagAmount + amount >= 999:
            return False
        
        self.game.weapon.bagAmount = min(999, self.game.weapon.bagAmount + amount)
        return True


    def movement(self):
        if self.game.interaction.input_active:
            self.vel_x *= 0.5 
            self.vel_y *= 0.5
            return

        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        dt = self.game.delta_time / 1000 if self.game.delta_time > 1 else self.game.delta_time
        acc = self.acceleration * dt
        self.vel_x *= self.friction
        self.vel_y *= self.friction

        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.vel_x += acc * cos_a
            self.vel_y += acc * sin_a
        if keys[pg.K_s]:
            self.vel_x -= acc * cos_a
            self.vel_y -= acc * sin_a
        if keys[pg.K_a]:
            self.vel_x += acc * sin_a
            self.vel_y -= acc * cos_a
        if keys[pg.K_d]:
            self.vel_x -= acc * sin_a
            self.vel_y += acc * cos_a


        current_time = pg.time.get_ticks() #hodanje i zvukovi
        if (abs(self.vel_x) > 0.01 or abs(self.vel_y) > 0.01) and not self.is_dashing:
            if current_time - self.last_step_time >= self.step_delay:
                if self.game.sound.footstep:
                    self.game.sound.footstep.play()
                self.last_step_time = current_time


        """if abs(self.vel_x) > 0.1 or abs(self.vel_y) > 0.1:
            length = math.sqrt(self.vel_x * self.vel_x + self.vel_y * self.vel_y)
            self.dash_direction = (self.vel_x / length, self.vel_y / length)
        else:
            self.dash_direction = (cos_a, sin_a)"""

        if keys[pg.K_SPACE] and not self.is_dashing:
            self.dash()

        self.check_wall_collision(self.vel_x, self.vel_y)
        self.angle %= math.tau

    def check_wall(self, x, y):
        return (x, y) not in self.game.map.world_map

    def check_wall_collision(self, dx, dy):
        offset = 0.15 if dx > 0 else -0.15
    
        if self.check_wall(int(self.x + dx + offset), int(self.y)):
            self.x += dx
        else:
            self.vel_x = 0

        offset = 0.2 if dy > 0 else -0.2
        if self.check_wall(int(self.x), int(self.y + dy + offset)):
            self.y += dy
        else:
            self.vel_y = 0

    def mouse_control(self):
        if self.dialogue_mode or (hasattr(self.game, 'intro_sequence') and self.game.intro_sequence.active):
            return

        """mx, _ = pg.mouse.get_pos()
        if mx < MOUSE_BORDER_LEFT or mx > MOUSE_BORDER_RIGHT:
            pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])"""

        if not pg.event.get_grab():
            return

        """self.rel = pg.mouse.get_rel()[0]
        self.rel = max(-MOUSE_MAX_REL, min(MOUSE_MAX_REL, self.rel))
        self.angle += self.rel * MOUSE_SENSITIVITY * self.game.delta_time"""
        rel_x = pg.mouse.get_rel()[0]
        rel_x= max(-MOUSE_MAX_REL, min(MOUSE_MAX_REL, rel_x))
        self.angle += rel_x * MOUSE_SENSITIVITY * self.game.delta_time

    def get_dash_direction(self):
        keys = pg.key.get_pressed()

        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)

        dx, dy = 0, 0

        if keys[pg.K_w]:
            dx += cos_a
            dy += sin_a
        if keys[pg.K_s]:
            dx -= cos_a
            dy -= sin_a
        if keys[pg.K_a]:
            dx += sin_a
            dy -= cos_a
        if keys[pg.K_d]:
            dx -= sin_a
            dy += cos_a

        length = math.sqrt(dx * dx + dy * dy)
        if length == 0:
            return 0, 0
        return dx / length, dy / length

    """def dash(self):
        if hasattr(self.game, 'intro_sequence') and self.game.intro_sequence.active:
            return False

        current_time = pg.time.get_ticks()
        if current_time - self.last_dash_time < PLAYER_DASH_COOLDOWN:
            return False

        dash_dx, dash_dy = self.get_dash_direction()
        if dash_dx==0 and dash_dy==0:
               return 0;

        self.is_dashing = True
        self.dash_start_time = current_time
        self.last_dash_time = current_time

        self.game.sound.player_dash.play()
        return True"""

    def dash(self):
        if hasattr(self.game, 'intro_sequence') and self.game.intro_sequence.active:
         return False

        current_time = pg.time.get_ticks()
        if current_time - self.last_dash_time < PLAYER_DASH_COOLDOWN:
            return False

        dash_dx, dash_dy = self.get_dash_direction()
        if dash_dx == 0 and dash_dy == 0:
            return False

        self.dash_direction = (dash_dx, dash_dy)
        self.is_dashing = True
        self.dash_start_time = current_time
        self.last_dash_time = current_time

        self.game.sound.player_dash.play()
        return True

    def update_dash(self):
        if not self.is_dashing:
            return

        current_time = pg.time.get_ticks()
        if current_time - self.dash_start_time > PLAYER_DASH_DURATION:
            self.is_dashing = False
            return

        dx, dy = self.dash_direction
        dash_speed = PLAYER_SPEED * PLAYER_DASH_MULTIPLIER * self.game.delta_time
        self.check_wall_collision(dx * dash_speed, dy * dash_speed)

    def activate_invulnerability(self):
        self.is_invulnerable = True
        self.invulnerability_start_time = pg.time.get_ticks()
        self.invulnerability_time_left = POWERUP_INVULNERABILITY_DURATION
        self.game.sound.powerup_pickup.play()
        self.game.sound.powerup_active.play(-1)

    def update_invulnerability(self):
        if not self.is_invulnerable:
            return

        current_time = pg.time.get_ticks()
        elapsed = current_time - self.invulnerability_start_time

        self.invulnerability_time_left = max(0, POWERUP_INVULNERABILITY_DURATION - elapsed)

        if self.invulnerability_time_left <= 0:
            self.is_invulnerable = False
            self.game.sound.powerup_active.stop()
            self.game.sound.powerup_end.play()

    def update(self):
        if self.dialogue_mode or (hasattr(self.game, 'intro_sequence') and self.game.intro_sequence.active)or (hasattr(self.game, 'interaction') and self.game.interaction.input_active):
            return
        if not self.is_dashing:
            self.movement()
        self.update_dash()
        self.update_invulnerability()
        self.mouse_control()
        #self.recover_health()
        self.update_auto_fire()

    def update_auto_fire(self):
        if not hasattr(self.game, 'weapon') or self.game.weapon is None:
            return

        if self.auto_fire and hasattr(self.game.weapon, 'auto_fire') and self.game.weapon.auto_fire:
            current_time = pg.time.get_ticks()
            if not self.game.weapon.is_reloading and current_time - self.last_auto_fire_time >= self.auto_fire_delay:
                self.fire_weapon()


    @property
    def pos(self):
        return self.x, self.y

    @property
    def map_pos(self):
        return int(self.x), int(self.y)
