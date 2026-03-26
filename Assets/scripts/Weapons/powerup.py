import math
from Assets.settings import *
from Assets.scripts.Util.sprite_object import SpriteObject


class PowerUp(SpriteObject):
    def __init__(self, game, path='resources/teksture/level1/powerup.png', pos=(10.5, 3.5), powerup_type='invulnerability'):
        if isinstance(pos, tuple) and len(pos) == 2:
            if pos[0] == int(pos[0]) and pos[1] == int(pos[1]):
                pos = (pos[0] + 0.5, pos[1] + 0.5)

        super().__init__(game, path, pos, scale=0.35, shift=1)

        self.powerup_type = powerup_type
        self.pickup_distance = POWERUP_PICKUP_DISTANCE
        self.collected = False

    def update(self):
        super().update()

        if not self.collected:
            player_pos = self.game.player.pos
            distance = math.hypot(player_pos[0] - self.x, player_pos[1] - self.y)

            if distance < self.pickup_distance:
                self.collect()

    def collect(self):
        if self.collected:
            return

        self.collected = True

        if self.powerup_type == 'invulnerability':
            self.game.player.activate_invulnerability()

        if self in self.game.object_handler.sprite_list:
            self.game.object_handler.sprite_list.remove(self)
