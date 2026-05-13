import os
import importlib
import re
import pygame as pg

from Assets.scripts.Character.interaction import InteractiveObject
from Assets.npcs.enemy_npcs import KlonoviNPC, StakorNPC, TosterNPC, ParazitNPC, JazavacNPC
from Assets.npcs.dialogue_npc import create_dialogue_npcs

class LevelManager:
    def __init__(self, game):
        self.game = game
        self.current_level = 1
        self.level_data = {}
        self.max_level = 0 #deprecated trebalo bi biti automatic
        self.current_weapon_type = 'pistol'
        self.initialize_levels()
        

    def initialize_levels(self):
        try:
            import Assets.Levels as levels_pkg
        
            levels_paths = list(levels_pkg.__path__)
            if not levels_paths:
                raise RuntimeError("Assets.Levels package path not found")

            levels_path = levels_paths[0]

            level_files = sorted(
                name for name in os.listdir(levels_path)
                if os.path.isfile(os.path.join(levels_path, name))
                and re.match(r'^level(\d+)\.py$', name)
            )

            for file_name in level_files:
                match = re.match(r'^level(\d+)\.py$', file_name)
                level_num = int(match.group(1))
                module_path = f'Assets.Levels.level{level_num}'

                try:
                    print(f"Importing level {level_num} from {module_path}")
                    level_module = importlib.import_module(module_path)
                    self.level_data[level_num] = level_module.get_level_data()
                except ImportError as e:
                    from Assets.Levels.base_level import create_base_level_structure
                    print(f"Import error for level {level_num}: {e}")
                    self.level_data[level_num] = create_base_level_structure()

            self.max_level = max(self.level_data.keys(), default=0)
            print(f"Loaded {len(self.level_data)} levels. Max level: {self.max_level}")
            
        except Exception as e:
            print(f"Critical error during level initialization: {e}")
            self.level_data = {}
            self.max_level = 0
           

    def load_level(self, level_number):
        # 1. If it's a known handcrafted level (1-6)
        if level_number in self.level_data:
            self.current_level = level_number
            return self.level_data[level_number]
            
        # 2. If it's Level 99 (Procedural Endless/Arena)
        elif level_number == 99:
            import time
            seed = int(time.time())
            
            # Generate the level and register it so it behaves like a normal level
            print(f"Generating Procedural Level {level_number}...")
            evel_data = self.create_and_register_runtime_level(level_number, seed)
            
            self.current_level = level_number
            return self.level_data
            
        return None

    def get_current_level_data(self):
        return self.level_data.get(self.current_level, None)

    def get_enemy_config(self):
        level_data = self.get_current_level_data()
        if level_data and 'enemies' in level_data:
            return level_data['enemies']
        return {
            'count': 5,
            'types': [KlonoviNPC, StakorNPC, TosterNPC, ParazitNPC, JazavacNPC],
            'weights': [20, 20, 20, 20, 20],
            'restricted_area': {(i, j) for i in range(10) for j in range(10)},
            'fixed_positions': []
        }

    def get_sprite_data(self):
        level_data = self.get_current_level_data()
        if level_data and 'sprites' in level_data:
            return level_data['sprites']
        return []

    def setup_interactive_objects(self):
        level_data = self.get_current_level_data()
        if not level_data:
            self.auto_detect_interactive_objects()
            return

        self.game.interaction.interaction_objects.clear()

        terminal_path = 'resources/sprites/static_sprites/terminal.png'
        door_path = 'resources/sprites/static_sprites/door.png'
        level_door_path = 'resources/sprites/static_sprites/level_door.png'

        if not os.path.isfile(level_door_path):
            level_door_path = door_path

        for terminal_data in level_data['terminals']:
            terminal = InteractiveObject(
                self.game,
                path=terminal_path,
                pos=terminal_data['position'],
                interaction_type="terminal",
                code=terminal_data['code'],
                unlocks_door_id=terminal_data.get('unlocks_door_id')
            )
            self.game.object_handler.add_sprite(terminal)
            self.game.interaction.add_object(terminal)

        for door_data in level_data['doors']:
            door = InteractiveObject(
                self.game,
                path=door_path,
                pos=door_data['position'],
                interaction_type="door",
                door_id=door_data['door_id'],
                requires_code=door_data.get('requires_code', False),
                requires_door_id=door_data.get('requires_door_id'),
                code=door_data.get('code')
            )
            self.game.object_handler.add_sprite(door)
            self.game.interaction.add_object(door)

        if 'weapons' in level_data:
            for weapon_data in level_data['weapons']:
                weapon_index = weapon_data['weapon_index']

                if self.game.player.weapon_unlocked[weapon_index]:
                    continue
            
                weapon_pickup = InteractiveObject(
                    self.game,
                    path=weapon_data['path'],
                    pos=weapon_data['position'],
                    interaction_type="weapon",
                    weapon_index=weapon_index
                )
                self.game.object_handler.add_sprite(weapon_pickup)
                self.game.interaction.add_object(weapon_pickup)

        if 'powerups' in level_data:
            for powerup_data in level_data['powerups']:
                self.game.object_handler.add_powerup(
                    pos=powerup_data['position'],
                    powerup_type=powerup_data['powerup_type']
                )

        if 'heal_item' in level_data:#heal_item
            for heal_item_data in level_data['heal_item']:
                self.game.object_handler.add_heal_item(
                    pos=heal_item_data['position']
                )
                    
                #self.game.object_handler.add_sprite(heal_item)
               #self.game.interaction.add_object(heal_item)

        if 'ammo_pickup' in level_data:
            for ammo_item in level_data['ammo_pickup']:
                    self.game.object_handler.add_ammo_item(
                        pos = ammo_item['position']
                    )

        exit_positions = {
            1: (14.5, 3.5),
            2: (18.5, 17.5),
            3: (12.5, 23.5),
            4: (19, 9),
            5: (13.5, 23.5),
            6: (10.5, 15.5)
        }

        if self.current_level in exit_positions:
            exit_pos = exit_positions[self.current_level]
            
            # Postavljanje koda za 2. level (kod je '8332' kao na terminalu)
            req_code = False
            exit_code = None
            if self.current_level == 2:
                req_code = True
                exit_code = '8332'
                
            level_exit = InteractiveObject(
                self.game,
                path=level_door_path,
                pos=exit_pos,
                interaction_type="level_door",
                is_level_exit=True,
                requires_code=req_code,
                code=exit_code
            )
            # Ne dodajemo u sprite_list jer user koristi zidnu teksturu na mapi
            # self.game.object_handler.add_sprite(level_exit)
            self.game.interaction.add_object(level_exit)

    def auto_detect_interactive_objects(self):
        self.game.interaction.interaction_objects.clear()

        terminal_path = 'resources/sprites/static_sprites/terminal.png'
        door_path = 'resources/sprites/static_sprites/door.png'

        terminal_positions = []
        door_positions = []
        level_exit_positions = []

        for y, row in enumerate(self.game.map.mini_map):
            for x, value in enumerate(row):
                if value == 14:
                    terminal_positions.append((x, y))
                elif value == 11:
                    exit_positions = {
                        1: (10, 20),
                        2: (11, 24),
                        3: (12, 24),
                        4: (12, 24),
                        5: (13, 24)
                    }

                    current_pos = (x, y)
                    if self.current_level in exit_positions and current_pos == exit_positions[self.current_level]:
                        level_exit_positions.append(current_pos)
                    else:
                        door_positions.append(current_pos)

        default_code = "1337"

        for i, pos in enumerate(terminal_positions):
            terminal = InteractiveObject(
                self.game,
                path=terminal_path,
                pos=pos,
                interaction_type="terminal",
                code=default_code,
                unlocks_door_id=i+1
            )
            self.game.object_handler.add_sprite(terminal)
            self.game.interaction.add_object(terminal)

        for i, pos in enumerate(door_positions):
            door = InteractiveObject(
                self.game,
                path=door_path,
                pos=pos,
                interaction_type="door",
                door_id=i+1,
                requires_code=True,
                code=default_code,
                requires_door_id=i if i > 0 else None
            )
            self.game.object_handler.add_sprite(door)
            self.game.interaction.add_object(door)

        for pos in level_exit_positions:
            level_exit = InteractiveObject(
                self.game,
                path=door_path,
                pos=pos,
                interaction_type="level_door",
                is_level_exit=True
            )
            self.game.object_handler.add_sprite(level_exit)
            self.game.interaction.add_object(level_exit)

    def setup_dialogue_npcs(self):
        level_data = self.get_current_level_data()
        print(f"[DEBUG] setup_dialogue_npcs called, level: {self.current_level}")
        print(f"[DEBUG] level_data keys: {list(level_data.keys()) if level_data else 'None'}")

        if level_data and 'dialogue_npcs' in level_data:
            create_dialogue_npcs(self.game, level_data['dialogue_npcs'])

        # Auto-dijalog pri ulasku na razinu
        if level_data and 'intro_dialogue' in level_data:
            dialogue_id = level_data['intro_dialogue']
            pg.time.set_timer(pg.USEREVENT + 10, 5250, loops=1)
            self.game._pending_intro_dialogue = dialogue_id
        

    def prepare_next_level(self):
        next_level = self.current_level + 1
        if next_level <= self.max_level and next_level in self.level_data:
            self._next_level = next_level
            return True
        elif next_level > self.max_level:
            return False
        return False

    def activate_next_level(self):
        if hasattr(self, '_next_level'):
            if self.current_level == 1 and hasattr(self.game, 'disorienting_effects'):
                self.game.disorienting_effects.end_effects()

            self.current_level = self._next_level
            self.game.map.load_level(self.current_level)

            if hasattr(self.game, 'game_ui'):
                self.game.game_ui.update_level(self.current_level)

            return True
        return False

    def next_level(self):
        next_level = self.current_level + 1
        if next_level <= self.max_level and next_level in self.level_data:
            if self.current_level == 1 and hasattr(self.game, 'disorienting_effects'):
                self.game.disorienting_effects.end_effects()

            self.current_level = next_level
            self.game.map.load_level(next_level)

            if hasattr(self.game, 'game_ui'):
                self.game.game_ui.update_level(self.current_level)

            self.game.new_game()
            return True
        elif next_level > self.max_level:
            return False
        return False
    
    def register_runtime_level(self, level_number, level_data):
        self.level_data[level_number] = level_data
        self.max_level = max(self.max_level, level_number)

    def create_and_register_runtime_level(self, level_number, seed):
        # Updated to import from your actual path (make sure this path matches your files!)
        from Assets.scripts.MapGenerator.runtime_level import build_runtime_level
        
        # Pass the level_number so settings.py knows which rules to apply
        level_data = build_runtime_level(seed, level_id=level_number) 
        
        self.register_runtime_level(level_number, level_data)
        return level_data