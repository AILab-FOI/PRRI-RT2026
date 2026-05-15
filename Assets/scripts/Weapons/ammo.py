import math
from Assets.scripts.Util.sprite_object import SpriteObject


class Ammo_item(SpriteObject):
    def __init__(self, game, pos = (0,0), path='resources/sprites/temp_ammo.png',
                 scale=0.4, shift=0.1, pickup_distance=0.5):
        super().__init__(game, path=path, pos=pos, scale=scale, shift=shift)
        self.pickup_distance = pickup_distance
        self.picked = False

    def check_pickup(self):
        if self.picked:
            return

        dx = self.player.x - self.x
        dy = self.player.y - self.y
        distance = math.hypot(dx, dy)

        if distance <= self.pickup_distance:
            if self.game.player.try_addAmmo(99):
                self.picked = True

                if hasattr(self.game.sound, 'ammo_pickup') and self.game.sound.ammo_pickup:
                    self.game.sound.ammo_pickup.play()

                if self in self.game.object_handler.sprite_list:
                    self.game.object_handler.sprite_list.remove(self)

    def update(self):
        self.check_pickup()
        if not self.picked:
            super().update()