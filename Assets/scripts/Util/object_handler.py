from Assets.scripts.Util.sprite_object import *
from Assets.scripts.Weapons.powerup import PowerUp
from random import choices, shuffle
from Assets.scripts.Util.heal_item import Heal_item

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

        self.spawn_npc()
        self.load_decorative_sprites()

    def spawn_npc(self):
        if len(self.npc_list) > 0:
            self.npc_list = []
            self.npc_positions = {}
            self.win_message_shown = False

        enemy_config = self.game.level_manager.get_enemy_config()
        self.enemies_from_pool_count = enemy_config['count']
        self.npc_types = enemy_config['types']
        self.weights = enemy_config['weights']
        self.restricted_area = enemy_config['restricted_area']
        fixed_positions_config = enemy_config.get('fixed_positions', [])

        for item in fixed_positions_config:
            if isinstance(item, dict):
                npc_class_to_spawn = item['type']
                pos_tuple = item['position']
                x, y = pos_tuple

                if (pos_tuple in self.game.map.world_map) or (pos_tuple in self.restricted_area):
                    continue

                self.add_npc(npc_class_to_spawn(self.game, pos=(x + 0.5, y + 0.5)))

        enemies_spawned_from_pool_so_far = 0
        for item in fixed_positions_config:
            if isinstance(item, tuple):
                if enemies_spawned_from_pool_so_far >= self.enemies_from_pool_count:
                    break

                x, y = item

                if (item in self.game.map.world_map) or (item in self.restricted_area):
                    continue

                if not self.npc_types:
                    continue
                npc_type_class = choices(self.npc_types, self.weights)[0]
                self.add_npc(npc_type_class(self.game, pos=(x + 0.5, y + 0.5)))
                enemies_spawned_from_pool_so_far += 1

        remaining_pool_enemies_to_spawn = self.enemies_from_pool_count - enemies_spawned_from_pool_so_far
        if remaining_pool_enemies_to_spawn > 0:
            if self.npc_types:
                self._spawn_random_enemies(remaining_pool_enemies_to_spawn)

    def check_win(self):
        hostile_npcs = [npc for npc in self.npc_list if npc.alive and not hasattr(npc, 'is_friendly')]
        all_enemies_defeated_now = len(hostile_npcs) == 0

        if all_enemies_defeated_now and not self.win_message_shown and (self.enemies_from_pool_count > 0 or any(isinstance(item, dict) for item in self.game.level_manager.get_enemy_config().get('fixed_positions', []))):
            self.win_message_shown = True
            self.game.object_renderer.show_message(f"All hostile entities neutralized! Find the exit door.")
            self.enable_level_exit()
        elif all_enemies_defeated_now and self.enemies_from_pool_count == 0 and not any(isinstance(item, dict) for item in self.game.level_manager.get_enemy_config().get('fixed_positions', [])):
            self.enable_level_exit(show_message=False)

        self.all_enemies_defeated = all_enemies_defeated_now

    def update(self):
        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}
        [sprite.update() for sprite in self.sprite_list]
        [npc.update() for npc in self.npc_list]
        self.check_win()

    def add_npc(self, npc):
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

    def _spawn_random_enemies(self, count):
        if not self.npc_types:
            return

        valid_positions = []
        for y in range(self.game.map.rows):
            for x in range(self.game.map.cols):
                pos = (x, y)
                if (pos not in self.game.map.world_map) and \
                   (pos not in self.restricted_area) and \
                   (pos not in self.npc_positions):
                    valid_positions.append(pos)

        shuffle(valid_positions)

        spawned = 0
        for pos in valid_positions:
            if spawned >= count:
                break

            x, y = pos
            npc_type_class = choices(self.npc_types, self.weights)[0]
            self.add_npc(npc_type_class(self.game, pos=(x + 0.5, y + 0.5)))
            spawned += 1

    def reset(self):
        self.sprite_list = []
        self.npc_list = []
        self.npc_positions = {}
        self.win_message_shown = False
        self.all_enemies_defeated = False

        self.spawn_npc()
        self.load_decorative_sprites()


    def add_heal_item(self,pos):#heal_item
        heal_item = Heal_item(self.game, pos=pos)
        self.add_sprite(heal_item)
        return heal_item