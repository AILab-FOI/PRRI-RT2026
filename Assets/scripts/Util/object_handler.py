from Assets.scripts.Util.sprite_object import *
import pygame as pg
from Assets.scripts.Weapons.powerup import PowerUp
from random import choices, shuffle
from Assets.scripts.Weapons.heal_item import Heal_item
from Assets.scripts.Weapons.ammo import Ammo_item

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

        self.current_wave_index = 0
        self.waves_config = []
        self.is_waiting_for_wave = False
        self.wave_spawn_time = 0
        self.wave_delay = 3000

        self.spawn_wave()
        self.load_decorative_sprites()

    def spawn_wave(self):
        if len(self.npc_list) > 0:
            self.npc_list = []
            self.npc_positions = {}
            self.win_message_shown = False

        enemy_config = self.game.level_manager.get_enemy_config()
        
        if 'waves' in enemy_config:
            self.waves_config = enemy_config['waves']
            self.restricted_area = enemy_config.get('restricted_area', set())
        else:
            self.waves_config = [{
                'count': enemy_config.get('count', 0),
                'types': enemy_config.get('types', []),
                'weights': enemy_config.get('weights', []),
                'fixed_positions': enemy_config.get('fixed_positions', [])
            }]
            self.restricted_area = enemy_config.get('restricted_area', set())

        if self.current_wave_index >= len(self.waves_config):
            return

        current_wave = self.waves_config[self.current_wave_index]

        self.enemies_from_pool_count = current_wave.get('count', 0)
        self.npc_types = current_wave.get('types', [])
        self.weights = current_wave.get('weights', [])
        fixed_positions_config = current_wave.get('fixed_positions', [])

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

    def current_wave_has_enemies(self):
        if not self.waves_config or self.current_wave_index >= len(self.waves_config):
            return False
        current_wave = self.waves_config[self.current_wave_index]
        return current_wave.get('count', 0) > 0 or any(isinstance(item, dict) for item in current_wave.get('fixed_positions', []))

    def check_win(self):
        hostile_npcs = [npc for npc in self.npc_list if npc.alive and not hasattr(npc, 'is_friendly')]
        all_enemies_defeated_now = len(hostile_npcs) == 0

        if all_enemies_defeated_now and not self.win_message_shown and not self.is_waiting_for_wave:
            if self.current_wave_index < len(self.waves_config) - 1:
                self.is_waiting_for_wave = True
                self.wave_spawn_time = pg.time.get_ticks()
                self.game.object_renderer.show_message(f"Wave {self.current_wave_index + 2} incoming in 3 seconds!")
            else:
                if self.current_wave_has_enemies():
                    self.win_message_shown = True
                    self.game.object_renderer.show_message(f"All hostile entities neutralized! Find the exit door.")
                    self.enable_level_exit()
                else:
                    self.enable_level_exit(show_message=False)

        self.all_enemies_defeated = all_enemies_defeated_now

    def update(self):
        # Remove corpses whose linger timer has expired
        self.npc_list = [npc for npc in self.npc_list if not getattr(npc, 'should_remove', False)]

        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}
        for sprite in self.sprite_list:
            sprite.update()
        for npc in self.npc_list:
            npc.update()
        
        if self.is_waiting_for_wave:
            if pg.time.get_ticks() - self.wave_spawn_time >= self.wave_delay:
                self.is_waiting_for_wave = False
                self.current_wave_index += 1
                self.spawn_wave()
        else:
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
        
        self.current_wave_index = 0
        self.waves_config = []
        self.is_waiting_for_wave = False

        self.spawn_wave()
        self.load_decorative_sprites()


    def add_heal_item(self,pos):#heal_item
        heal_item = Heal_item(self.game, pos=pos)
        self.add_sprite(heal_item)
        return heal_item
    
    def add_ammo_item(self,pos):
        ammo_item = Ammo_item(self.game,pos=pos)
        self.add_sprite(ammo_item)
        return ammo_item