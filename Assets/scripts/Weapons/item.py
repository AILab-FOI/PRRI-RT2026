import math
from Assets.scripts.Util.sprite_object import SpriteObject


#TODO promijeni zvuk, spusti sprajt, smanji ga i dodaj brojac na menu
class Pickup_item(SpriteObject):
    def __init__(self, game, pos=(1.5, 1.5), path='resources/teksture/pickup_item1.png',
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
            self.picked = True

            if hasattr(self.game.sound, 'powerup_pickup') and self.game.sound.powerup_pickup:
                self.game.sound.powerup_pickup.play()

            if self in self.game.object_handler.sprite_list:
                self.game.object_handler.sprite_list.remove(self)

    def update(self):
        self.check_pickup()
        if not self.picked:
            super().update()