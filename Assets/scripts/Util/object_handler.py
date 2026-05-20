from Assets.scripts.Util.sprite_object import *
from Assets.scripts.Weapons.powerup import PowerUp
from Assets.scripts.Weapons.heal_item import Heal_item
from Assets.scripts.Weapons.ammo import Ammo_item
from Assets.scripts.WaveManager.waveManager import WaveManager
from Assets.scripts.Weapons.item import Pickup_item


class ObjectHandler:
    def __init__(self, game):
        self.game = game
        self.sprite_list = []
        self.npc_list = []
        self.npc_sprite_path = 'resources/sprites/npc/'
        self.static_sprite_path = 'resources/sprites/static_sprites/'
        self.anim_sprite_path = 'resources/sprites/animated_sprites/'
        self.npc_positions = {}
        self.win_message_shown = False
        self.all_enemies_defeated = False

        self.game.object_handler = self
        self.wave_manager = WaveManager(game, self)
        self.game.wave_manager = self.wave_manager
        self.wave_manager.start_level()
        self.load_decorative_sprites()

    def update(self):
        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}

        for sprite in self.sprite_list:
            sprite.update()
        for npc in self.npc_list[:]:
            npc.update()

        self.wave_manager.update()

    def add_npc(self, npc):
        if npc not in self.npc_list:
            self.npc_list.append(npc)

    def enable_level_exit(self, show_message=True):
        for obj in self.game.interaction.interaction_objects:
            if hasattr(obj, 'is_level_exit') and obj.is_level_exit:
                obj.is_enabled = True
                if show_message:
                    self.game.object_renderer.show_message("The exit door is now open!")
                break

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)

    def add_powerup(self, pos, powerup_type='invulnerability'):
        powerup = PowerUp(self.game, pos=pos, powerup_type=powerup_type)
        self.add_sprite(powerup)
        return powerup

    def load_decorative_sprites(self):
        sprite_data = self.game.level_manager.get_sprite_data()

        for sprite_info, pos in sprite_data:
            sprite_path_to_load = None
            if isinstance(sprite_info, tuple) and len(sprite_info) == 2:
                folder, sprite_type = sprite_info
                if folder == 'static':
                    sprite_path_to_load = self.static_sprite_path + sprite_type + '.png'
                elif folder == 'level1':
                    sprite_path_to_load = 'resources/teksture/level1/' + sprite_type + '.png'
                elif folder == 'level2':
                    sprite_path_to_load = 'resources/teksture/level2/' + sprite_type + '.png'
                elif folder == 'level3':
                    sprite_path_to_load = 'resources/teksture/level3/' + sprite_type + '.png'
                elif folder == 'level4':
                    sprite_path_to_load = 'resources/teksture/level4/' + sprite_type + '.png'
                elif folder == 'teksture':
                    sprite_path_to_load = 'resources/teksture/' + sprite_type + '.png'
                else:
                    sprite_path_to_load = self.static_sprite_path + sprite_type + '.png'
            elif isinstance(sprite_info, str):
                sprite_type = sprite_info
                sprite_path_to_load = self.static_sprite_path + sprite_type + '.png'
            else:
                continue

            if sprite_path_to_load:
                self.add_sprite(SpriteObject(self.game, path=sprite_path_to_load, pos=pos))

    def reset(self):
        self.sprite_list = []
        self.npc_list = []
        self.npc_positions = {}
        self.win_message_shown = False
        self.all_enemies_defeated = False

        self.wave_manager.reset()
        self.game.wave_manager = self.wave_manager
        self.load_decorative_sprites()

    def add_heal_item(self, pos):
        heal_item = Heal_item(self.game, pos=pos)
        self.add_sprite(heal_item)
        return heal_item

    def add_ammo_item(self, pos):
        ammo_item = Ammo_item(self.game, pos=pos)
        self.add_sprite(ammo_item)
        return ammo_item
    
    def add_pickup_item(self, pos, message=None):
        pickup_item = Pickup_item(self.game, pos=pos, message=message)
        self.add_sprite(pickup_item)
        return pickup_item