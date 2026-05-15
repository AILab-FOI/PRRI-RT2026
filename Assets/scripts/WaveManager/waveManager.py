import pygame as pg
from math import hypot
from random import choices, shuffle


class WaveManager:
    OFFMAP_POS = (-1000.5, -1000.5)
    RUNTIME_LEVEL_NUMBER = 99

    def __init__(self, game, object_handler):
        self.game = game
        self.object_handler = object_handler

        self.waves = []
        self.restricted_area = set()
        self.wave_delay = 3000
        self.current_wave_index = 0
        self.finished_all_waves = False
        self.is_waiting_for_next_wave = False
        self.next_wave_time = 0

        self.current_wave_total = 0
        self.current_wave_remaining_to_spawn = 0
        self.current_wave_max_on_map = 0
        self.current_wave_types = []
        self.current_wave_weights = []
        self.current_wave_fixed_positions = []
        self.current_wave_spawned_total = 0
        self.current_wave_killed_total = 0

        self.enemy_pool = {}
        self.active_enemies = []
        self.inactive_enemies = {}

        self.is_runtime_endless = False
        self.runtime_base_count = 8
        self.runtime_count_growth = 3
        self.runtime_base_max_on_map = 4
        self.runtime_max_on_map_growth = 1
        self.runtime_spawn_min_radius = 4
        self.runtime_spawn_max_radius = 10

        self.score = 0
        self.points_per_kill = 10
        self.level_start_time = pg.time.get_ticks()

        self.load_level_data()
        self.build_enemy_pool()

    def load_level_data(self):
        enemy_config = self.game.level_manager.get_enemy_config()
        self.restricted_area = enemy_config.get('restricted_area', set())

        current_level = getattr(self.game.level_manager, 'current_level', None)
        self.is_runtime_endless = current_level == self.RUNTIME_LEVEL_NUMBER

        if self.is_runtime_endless:
            self.wave_delay = 10000
            self.waves = []
            return

        self.wave_delay = enemy_config.get('wave_delay', 3000)

        if 'waves' in enemy_config:
            self.waves = enemy_config['waves']
        else:
            self.waves = [{
                'count': enemy_config.get('count', 0),
                'types': enemy_config.get('types', []),
                'weights': enemy_config.get('weights', []),
                'fixed_positions': enemy_config.get('fixed_positions', []),
                'max_enemies_on_map': enemy_config.get('max_enemies_on_map', enemy_config.get('count', 0))
            }]

    def build_enemy_pool(self):
        self.enemy_pool = {}
        self.inactive_enemies = {}
        self.active_enemies = []

        required_per_type = {}
        enemy_config = self.game.level_manager.get_enemy_config()

        if self.is_runtime_endless:
            runtime_types = enemy_config.get('types', [])
            runtime_fixed_positions = enemy_config.get('fixed_positions', [])
            runtime_max_on_map = enemy_config.get(
                'max_enemies_on_map',
                self.runtime_base_max_on_map + self.runtime_max_on_map_growth * 10
            )

            dict_counts = {}
            for item in runtime_fixed_positions:
                if isinstance(item, dict):
                    npc_class = item['type']
                    dict_counts[npc_class] = dict_counts.get(npc_class, 0) + 1

            for npc_class in runtime_types:
                required_per_type[npc_class] = max(required_per_type.get(npc_class, 0), runtime_max_on_map)

            for npc_class, fixed_count in dict_counts.items():
                required_per_type[npc_class] = max(required_per_type.get(npc_class, 0), fixed_count)
        else:
            for wave in self.waves:
                max_on_map = wave.get('max_enemies_on_map', wave.get('count', 0))
                types = wave.get('types', [])
                fixed_positions = wave.get('fixed_positions', [])

                dict_counts = {}
                for item in fixed_positions:
                    if isinstance(item, dict):
                        npc_class = item['type']
                        dict_counts[npc_class] = dict_counts.get(npc_class, 0) + 1

                for npc_class in types:
                    required_per_type[npc_class] = max(required_per_type.get(npc_class, 0), max_on_map)

                for npc_class, fixed_count in dict_counts.items():
                    required_per_type[npc_class] = max(required_per_type.get(npc_class, 0), fixed_count)

        for npc_class, pool_size in required_per_type.items():
            self.enemy_pool[npc_class] = []
            self.inactive_enemies[npc_class] = []
            for _ in range(pool_size):
                enemy = npc_class(self.game, pos=self.OFFMAP_POS)
                if hasattr(enemy, 'reset_for_pool'):
                    enemy.reset_for_pool()
                self.enemy_pool[npc_class].append(enemy)
                self.inactive_enemies[npc_class].append(enemy)

    def start_level(self):
        self.object_handler.npc_list = []
        self.object_handler.npc_positions = {}
        self.object_handler.win_message_shown = False
        self.object_handler.all_enemies_defeated = False
        self.finished_all_waves = False
        self.is_waiting_for_next_wave = False
        self.current_wave_index = 0
        self.next_wave_time = 0

        self.current_wave_total = 0
        self.current_wave_remaining_to_spawn = 0
        self.current_wave_max_on_map = 0
        self.current_wave_types = []
        self.current_wave_weights = []
        self.current_wave_fixed_positions = []
        self.current_wave_spawned_total = 0
        self.current_wave_killed_total = 0

        self.score = 0
        self.level_start_time = pg.time.get_ticks()

        self.recycle_all_active()

        if self.is_runtime_endless:
            self.start_runtime_wave(0)
            return

        if not self.waves:
            self.finished_all_waves = True
            self.object_handler.enable_level_exit(show_message=False)
            return

        self.start_wave(0)

    def start_runtime_wave(self, wave_index):
        enemy_config = self.game.level_manager.get_enemy_config()
        runtime_types = enemy_config.get('types', [])
        runtime_weights = enemy_config.get('weights', [])

        if not runtime_types:
            self.finished_all_waves = True
            self.object_handler.enable_level_exit(show_message=False)
            return

        self.current_wave_index = wave_index
        self.current_wave_total = self.runtime_base_count + wave_index * self.runtime_count_growth
        self.current_wave_remaining_to_spawn = self.current_wave_total
        self.current_wave_max_on_map = min(
            self.current_wave_total,
            self.runtime_base_max_on_map + wave_index * self.runtime_max_on_map_growth
        )
        self.current_wave_types = runtime_types
        self.current_wave_weights = runtime_weights if runtime_weights else [1] * len(runtime_types)
        self.current_wave_fixed_positions = []
        self.current_wave_spawned_total = 0
        self.current_wave_killed_total = 0
        self.is_waiting_for_next_wave = False

        self.game.object_renderer.show_message(
            f"Wave {wave_index + 1} starting! {self.current_wave_total} hostiles detected."
        )
        self.spawn_until_limit()

    def start_wave(self, wave_index):
        if wave_index >= len(self.waves):
            self.finished_all_waves = True
            self.object_handler.enable_level_exit()
            return

        wave = self.waves[wave_index]
        self.current_wave_index = wave_index
        self.current_wave_total = wave.get('count', 0)
        self.current_wave_remaining_to_spawn = wave.get('count', 0)
        self.current_wave_max_on_map = wave.get('max_enemies_on_map', min(15, self.current_wave_total))
        self.current_wave_types = wave.get('types', [])
        self.current_wave_weights = wave.get('weights', [])
        self.current_wave_fixed_positions = list(wave.get('fixed_positions', []))
        self.current_wave_spawned_total = 0
        self.current_wave_killed_total = 0
        self.is_waiting_for_next_wave = False

        self.spawn_until_limit()

    def update(self):
        if self.finished_all_waves:
            return

        self.collect_recyclable_dead()

        if self.is_waiting_for_next_wave:
            if pg.time.get_ticks() >= self.next_wave_time:
                if self.is_runtime_endless:
                    self.start_runtime_wave(self.current_wave_index + 1)
                else:
                    self.start_wave(self.current_wave_index + 1)
            return

        if self.is_current_wave_complete():
            if self.is_runtime_endless:
                self.is_waiting_for_next_wave = True
                self.next_wave_time = pg.time.get_ticks() + self.wave_delay
                self.game.object_renderer.show_message(
                    f"Wave {self.current_wave_index + 2} incoming in {self.wave_delay // 1000} seconds!"
                )
            else:
                if self.current_wave_index < len(self.waves) - 1:
                    self.is_waiting_for_next_wave = True
                    self.next_wave_time = pg.time.get_ticks() + self.wave_delay
                    self.game.object_renderer.show_message(
                        f"Wave {self.current_wave_index + 2} incoming in {self.wave_delay // 1000} seconds!"
                    )
                else:
                    self.finished_all_waves = True
                    self.game.object_renderer.show_message("All hostile entities neutralized! Find the exit door.")
                    self.object_handler.enable_level_exit()
            return

        self.spawn_until_limit()

    def spawn_until_limit(self):
        alive_now = self.get_alive_hostile_count()
        free_slots = self.current_wave_max_on_map - alive_now
        if free_slots <= 0:
            return
        if self.current_wave_remaining_to_spawn <= 0:
            return

        to_spawn_now = min(free_slots, self.current_wave_remaining_to_spawn)

        for _ in range(to_spawn_now):
            spawn_info = self.get_next_spawn_info()
            if spawn_info is None:
                break

            npc_class = spawn_info['type']
            grid_pos = spawn_info['position']

            if grid_pos is None:
                if self.is_runtime_endless:
                    grid_pos = self.get_random_runtime_position_near_player()
                else:
                    grid_pos = self.get_random_free_position()
            if grid_pos is None:
                break

            enemy = self.get_pooled_enemy(npc_class)
            if enemy is None:
                continue

            if self.activate_enemy(enemy, grid_pos):
                self.current_wave_remaining_to_spawn -= 1
                self.current_wave_spawned_total += 1
            else:
                self.return_to_pool(enemy)

    def get_next_spawn_info(self):
        while self.current_wave_fixed_positions:
            item = self.current_wave_fixed_positions.pop(0)

            if isinstance(item, dict):
                return {'type': item['type'], 'position': item['position']}

            if isinstance(item, tuple):
                if not self.current_wave_types:
                    continue
                npc_class = choices(self.current_wave_types, self.current_wave_weights)[0]
                return {'type': npc_class, 'position': item}

        if not self.current_wave_types:
            return None

        npc_class = choices(self.current_wave_types, self.current_wave_weights)[0]
        return {'type': npc_class, 'position': None}

    def get_pooled_enemy(self, npc_class):
        available = self.inactive_enemies.get(npc_class, [])
        if not available:
            return None
        return available.pop()

    def activate_enemy(self, enemy, grid_pos):
        if not self.is_valid_spawn_position(grid_pos):
            return False

        spawn_pos = (grid_pos[0] + 0.5, grid_pos[1] + 0.5)
        if hasattr(enemy, 'reset_for_spawn'):
            enemy.reset_for_spawn(spawn_pos)
        else:
            enemy.x, enemy.y = spawn_pos
            enemy.alive = True
            enemy.should_remove = False

        if enemy not in self.object_handler.npc_list:
            self.object_handler.npc_list.append(enemy)
        if enemy not in self.active_enemies:
            self.active_enemies.append(enemy)
        return True

    def collect_recyclable_dead(self):
        for enemy in self.active_enemies[:]:
            if getattr(enemy, 'should_remove', False):
                self.recycle_enemy(enemy)
                self.current_wave_killed_total += 1
                self.score += self.points_per_kill

    def recycle_enemy(self, enemy):
        if enemy in self.active_enemies:
            self.active_enemies.remove(enemy)
        if enemy in self.object_handler.npc_list:
            self.object_handler.npc_list.remove(enemy)
        self.return_to_pool(enemy)

    def return_to_pool(self, enemy):
        enemy_class = enemy.__class__
        if hasattr(enemy, 'reset_for_pool'):
            enemy.reset_for_pool()
        else:
            enemy.x, enemy.y = self.OFFMAP_POS
            enemy.alive = False
            enemy.should_remove = False
        self.inactive_enemies.setdefault(enemy_class, []).append(enemy)

    def recycle_all_active(self):
        for enemy in self.active_enemies[:]:
            self.recycle_enemy(enemy)

    def is_current_wave_complete(self):
        return self.current_wave_remaining_to_spawn <= 0 and self.get_alive_hostile_count() <= 0

    def get_alive_hostile_count(self):
        return len([
            npc for npc in self.active_enemies
            if getattr(npc, 'alive', False) and not getattr(npc, 'is_friendly', False)
        ])

    def get_enemies_left(self):
        return max(0, self.current_wave_remaining_to_spawn + self.get_alive_hostile_count())

    def get_current_wave_number(self):
        return self.current_wave_index + 1

    def get_score(self):
        return self.score

    def get_survival_seconds(self):
        return max(0, (pg.time.get_ticks() - self.level_start_time) // 1000)

    def is_valid_spawn_position(self, pos):
        occupied_positions = {npc.map_pos for npc in self.active_enemies if getattr(npc, 'alive', False)}
        return (
            pos not in self.game.map.world_map and
            pos not in self.restricted_area and
            pos not in occupied_positions
        )

    def get_random_free_position(self):
        occupied_positions = {npc.map_pos for npc in self.active_enemies if getattr(npc, 'alive', False)}
        valid_positions = []

        for y in range(self.game.map.rows):
            for x in range(self.game.map.cols):
                pos = (x, y)
                if pos in self.game.map.world_map:
                    continue
                if pos in self.restricted_area:
                    continue
                if pos in occupied_positions:
                    continue
                valid_positions.append(pos)

        shuffle(valid_positions)
        return valid_positions[0] if valid_positions else None

    def get_random_runtime_position_near_player(self):
        occupied_positions = {npc.map_pos for npc in self.active_enemies if getattr(npc, 'alive', False)}
        player_grid_x = int(self.game.player.x)
        player_grid_y = int(self.game.player.y)
        nearby_positions = []
        fallback_positions = []

        for y in range(self.game.map.rows):
            for x in range(self.game.map.cols):
                pos = (x, y)
                if pos in self.game.map.world_map:
                    continue
                if pos in self.restricted_area:
                    continue
                if pos in occupied_positions:
                    continue

                distance = hypot(x - player_grid_x, y - player_grid_y)
                if self.runtime_spawn_min_radius <= distance <= self.runtime_spawn_max_radius:
                    nearby_positions.append(pos)
                elif distance > self.runtime_spawn_max_radius:
                    fallback_positions.append(pos)

        shuffle(nearby_positions)
        shuffle(fallback_positions)

        if nearby_positions:
            return nearby_positions[0]
        if fallback_positions:
            return fallback_positions[0]
        return self.get_random_free_position()

    def reset(self):
        self.load_level_data()
        self.recycle_all_active()
        self.build_enemy_pool()
        self.start_level()