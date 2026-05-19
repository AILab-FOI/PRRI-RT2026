import math
from Assets.scripts.Util.sprite_object import SpriteObject


class Pickup_item(SpriteObject):
    def __init__(self, game, pos=(1.5, 1.5), path='resources/teksture/pickup_item1.png',
                 scale=0.35, shift=0.27, pickup_distance=0.5, message=None):
        super().__init__(game, path=path, pos=pos, scale=scale, shift=shift)
        self.pickup_distance = pickup_distance
        self.picked = False
        self.message = message

    def check_pickup(self):
        if self.picked:
            return

        dx = self.player.x - self.x
        dy = self.player.y - self.y
        distance = math.hypot(dx, dy)

        if distance <= self.pickup_distance:
            self.player.pickup_item_count += 1
            self.picked = True

            if hasattr(self.game.sound, 'powerup_pickup') and self.game.sound.powerup_pickup:
                self.game.sound.powerup_pickup.play()

            if self.message:
                self.game.lore_popup.show_message(self.message)

            if self in self.game.object_handler.sprite_list:
                self.game.object_handler.sprite_list.remove(self)

    def update(self):
        self.check_pickup()
        if not self.picked:
            super().update()