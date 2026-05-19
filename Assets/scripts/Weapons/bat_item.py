import math
import pygame as pg
from Assets.scripts.Util.sprite_object import SpriteObject


class Bat_item(SpriteObject):
    

    def __init__(self, game, pos=(1.5, 1.5),
                 path='resources/sprites/weapon/bat/bat_stand.png',
                 scale=0.35, shift=0.1, pickup_distance=0.5):
        super().__init__(game, path=path, pos=pos, scale=scale, shift=shift)
        self.pickup_distance = pickup_distance
        self.picked = False

    def check_pickup(self):
        if self.picked:
            return

        dx = self.player.x - self.x
        dy = self.player.y - self.y
        if math.hypot(dx, dy) > self.pickup_distance:
            return

       
        bat_slot = 3
        player = self.game.player #uzmi samo ako je nema
        if player.weapon_inventory[bat_slot] is not None and \
                player.weapon_unlocked[bat_slot]:
            return  # igrac je vec ima
        
        had_weapon = player.current_weapon_index != -1
        player.give_weapon(bat_slot, auto_equip=not had_weapon)
        
        bat = player.weapon_inventory[bat_slot]
        if bat is not None:
            bat.uses_left = bat.max_uses#nova palica ima max uses

        self.game.sound.play_sfx('bat_pickup')
        self.picked = True

        if self in self.game.object_handler.sprite_list:
            self.game.object_handler.sprite_list.remove(self)

    def update(self):
        self.check_pickup()
        if not self.picked:
            super().update()
