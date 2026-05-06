from Assets.settings import *
import pygame as pg
import math
from Assets.config.weapon_config import get_weapon_config
from Assets.scripts.Weapons.weapon import Pistol, SMG, PlasmaGun


class Player:
    def __init__(self, game):
        self.game = game
        self.x, self.y = PLAYER_POS
        self.angle = PLAYER_ANGLE
        self.shot = False
        self.health = PLAYER_MAX_HEALTH
        self.rel = 0
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

        self.is_damage_invulnerable = False
        self.damage_invulnerability_start_time = 0
        self.damage_invulnerability_duration = 200

        self.last_heal_time = 0
        self.heal_cooldown = 5000
        self.heal_item_count = 0

        self.last_step_time = 0
        self.step_delay = 350

        self.vel_x = 0
        self.vel_y = 0
        self.friction = 0.8
        self.acceleration = 0.9

        self.weapon_inventory = [None] * self.game.weapon_slot_count
        self.weapon_unlocked = [False] * self.game.weapon_slot_count
        self.current_weapon_index = -1

    def reset(self):
        self.health = PLAYER_MAX_HEALTH
        self.vel_x = 0
        self.vel_y = 0
        self.is_dashing = False
        self.is_invulnerable = False
        self.invulnerability_time_left = 0
        self.is_damage_invulnerable = False
        self.shot = False
        self.auto_fire = False

        self.heal_item_count = 1
        for weapon in self.weapon_inventory:
            if weapon is not None:
                weapon.bagAmount = 999
                weapon.currentMagAmmount = weapon.maxMagAmount

    def check_game_over(self):
        if self.health < 1:
            self.game.death_screen.start()

    def get_damage(self, damage):
        if self.is_invulnerable or self.is_damage_invulnerable:
            return

        self.health -= damage
        self.is_damage_invulnerable = True
        self.damage_invulnerability_start_time = pg.time.get_ticks()

        self.game.object_renderer.player_damage()
        self.game.sound.play_sfx('igrac_damage')
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

        if not self.game.weapon.can_fire():
            return

        if self.game.weapon.currentMagAmmount <= 0:
            return

        if weapon_config and 'sound' in weapon_config:
            sound_name = weapon_config['sound']
            if self.game.sound.get_sound(sound_name) is not None:
                self.game.sound.play_sfx(sound_name)
        else:
            if self.game.weapon.name == 'smg':
                self.game.sound.play_sfx('smg')
            else:
                self.game.sound.play_sfx('pistolj')

        self.shot = True
        self.game.weapon.currentMagAmmount -= 1
        self.game.weapon.register_fire()
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

        weapon_config=get_weapon_config(self.game.weapon.name)
        if weapon_config and 'reload_sound' in weapon_config:
                self.game.sound.play_sfx(weapon_config['reload_sound'])

        self.game.weapon.currentMagAmmount += ammo_to_reload
        self.game.weapon.bagAmount -= ammo_to_reload
        return True

    def try_heal(self):
        current_time = pg.time.get_ticks()
        if (
            self.heal_item_count > 0
            and self.health < PLAYER_MAX_HEALTH
            and current_time - self.last_heal_time >= self.heal_cooldown
        ):
            self.health = min(self.health + 20, PLAYER_MAX_HEALTH)
            self.heal_item_count -= 1
            self.game.sound.play_sfx('heal')
            self.game.object_renderer.player_heal()
            self.last_heal_time = current_time

    def try_addAmmo(self, amount):
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

        current_time = pg.time.get_ticks()
        if (abs(self.vel_x) > 0.01 or abs(self.vel_y) > 0.01) and not self.is_dashing:
            if current_time - self.last_step_time >= self.step_delay:
                if self.game.sound.get_sound('footstep') is not None:
                    self.game.sound.play_sfx('footstep')
                self.last_step_time = current_time

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

        if not pg.event.get_grab():
            return

        rel_x = pg.mouse.get_rel()[0]
        rel_x = max(-MOUSE_MAX_REL, min(MOUSE_MAX_REL, rel_x))
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

        self.game.sound.play_sfx('player_dash')
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
        self.game.sound.play_sfx('powerup_pickup')
        self.game.sound.play_sfx('powerup_active', loops=-1)

    def update_invulnerability(self):
        if not self.is_invulnerable:
            return

        current_time = pg.time.get_ticks()
        elapsed = current_time - self.invulnerability_start_time

        self.invulnerability_time_left = max(0, POWERUP_INVULNERABILITY_DURATION - elapsed)

        if self.invulnerability_time_left <= 0:
            self.is_invulnerable = False
            self.game.sound.stop_sfx('powerup_active')
            self.game.sound.play_sfx('powerup_end')

    def update_damage_invulnerability(self):
        if not self.is_damage_invulnerable:
            return

        if pg.time.get_ticks() - self.damage_invulnerability_start_time > self.damage_invulnerability_duration:
            self.is_damage_invulnerable = False

    def update(self):
        if self.dialogue_mode or (
            hasattr(self.game, 'intro_sequence') and self.game.intro_sequence.active
        ) or (
            hasattr(self.game, 'interaction') and self.game.interaction.input_active
        ):
            return

        if not self.is_dashing:
            self.movement()

        self.update_dash()
        self.update_invulnerability()
        self.update_damage_invulnerability()
        self.mouse_control()
        self.update_auto_fire()

    def update_auto_fire(self):
        if not hasattr(self.game, 'weapon') or self.game.weapon is None:
            return

        if self.auto_fire and hasattr(self.game.weapon, 'auto_fire') and self.game.weapon.auto_fire:
            current_time = pg.time.get_ticks()
            if not self.game.weapon.is_reloading and current_time - self.last_auto_fire_time >= self.auto_fire_delay:
                self.fire_weapon()

    def give_weapon(self, index, auto_equip=True):
        if index < 0 or index >= len(self.weapon_inventory):
            return False

        already_owned = self.weapon_inventory[index] is not None

        if not already_owned:
            weapon_class = self.game.weapon_classes[index]
            new_weapon = weapon_class(self.game)
            self.weapon_inventory[index] = new_weapon
            print(f"Created new weapon instance in slot {index}: {new_weapon.name}")

        self.weapon_unlocked[index] = True

        if auto_equip:
            self.equip_weapon_by_index(index)

        return not already_owned

    def equip_weapon_by_index(self, index, auto_equip=True):
        if index < 0 or index >= len(self.weapon_inventory):
            return False

        if not self.weapon_unlocked[index]:
            return False

        if self.weapon_inventory[index] is None:
            return False

        self.current_weapon_index = index
        self.game.weapon = self.weapon_inventory[index]
        self.auto_fire = False
        return True

    def next_weapon(self):
        if not any(weapon is not None for weapon in self.weapon_inventory):
            return

        start = self.current_weapon_index

        if start == -1:
            for i, weapon in enumerate(self.weapon_inventory):
                if weapon is not None and self.weapon_unlocked[i]:
                    self.equip_weapon_by_index(i)
                    self.print_weapon_inventory()
                    return

        for i in range(1, len(self.weapon_inventory) + 1):
            index = (start + i) % len(self.weapon_inventory)
            if self.weapon_unlocked[index] and self.weapon_inventory[index] is not None:
                self.equip_weapon_by_index(index)
                return

    def prev_weapon(self):
        if not any(weapon is not None for weapon in self.weapon_inventory):
            return

        start = self.current_weapon_index

        if start == -1:
            for i in range(len(self.weapon_inventory) - 1, -1, -1):
                if self.weapon_inventory[i] is not None and self.weapon_unlocked[i]:
                    self.equip_weapon_by_index(i)
                    self.print_weapon_inventory()
                    return

        for i in range(1, len(self.weapon_inventory) + 1):
            index = (start - i) % len(self.weapon_inventory)
            if self.weapon_unlocked[index] and self.weapon_inventory[index] is not None:
                self.equip_weapon_by_index(index)
                self.print_weapon_inventory()
                return

    def print_weapon_inventory(self):
        print("=== PLAYER WEAPON INVENTORY ===")
        for i, weapon in enumerate(self.weapon_inventory):
            unlocked = self.weapon_unlocked[i]
            selected = (i == self.current_weapon_index)

            if weapon is None:
                weapon_name = "EMPTY"
            else:
                weapon_name = weapon.name

            print(f"Slot {i}: {weapon_name}, unlocked={unlocked}, selected={selected}")

    @property
    def pos(self):
        return self.x, self.y

    @property
    def map_pos(self):
        return int(self.x), int(self.y)