import os
import importlib
import pkgutil
import re

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

            level_folders = sorted(
                name for name in os.listdir(levels_path)
                if os.path.isdir(os.path.join(levels_path, name))
                and re.match(r'^Lvl(\d+)$', name)
            )

            for folder in level_folders:
                match = re.match(r'^Lvl(\d+)$',folder)
                level_num = int(match.group(1))
                module_path = f'Assets.Levels.Lvl{level_num}.level{level_num}'
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


            """
            Old #Ostvaviti za svaku slucaj 
            for level_num in range(1, self.max_level + 1):
                try:
                    print("importint level ",level_num)
                    level_module = importlib.import_module(f'Assets.Levels.Lvl{level_num}.level{level_num}')
                    self.level_data[level_num] = level_module.get_level_data()
                except ImportError:
                    from Levels.base_level import create_base_level_structure
                    print("import error  level ",level_num)
                    self.level_data[level_num] = create_base_level_structure()
            """
        except Exception:
            print(f"Critical error during level initialization: {e}")
            self.level_data = {}
            self.max_level = 0

    def load_level(self, level_number):
        if level_number in self.level_data:
            self.current_level = level_number
            return self.level_data[level_number]
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
                if hasattr(self.game, 'weapon') and self.game.weapon and \
                   self.game.weapon.name == weapon_data['weapon_type']:
                    continue

                weapon_pickup = InteractiveObject(
                    self.game,
                    path=weapon_data['path'],
                    pos=weapon_data['position'],
                    interaction_type="weapon",
                    weapon_type=weapon_data['weapon_type']
                )
                self.game.object_handler.add_sprite(weapon_pickup)
                self.game.interaction.add_object(weapon_pickup)

        if 'powerups' in level_data:
            for powerup_data in level_data['powerups']:
                self.game.object_handler.add_powerup(
                    pos=powerup_data['position'],
                    powerup_type=powerup_data['powerup_type']
                )

        exit_positions = {
            1: (5, 24),
            2: (12, 34),
            3: (31, 33),
            4: (17, 34),
            5: (13, 34)
        }

        if self.current_level in exit_positions:
            exit_pos = exit_positions[self.current_level]
            level_exit = InteractiveObject(
                self.game,
                path=level_door_path,
                pos=exit_pos,
                interaction_type="level_door",
                is_level_exit=True
            )
            self.game.object_handler.add_sprite(level_exit)
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
                        1: (5, 24),
                        2: (12, 34),
                        3: (31, 33),
                        4: (17, 34),
                        5: (13, 34)
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
        if level_data and 'dialogue_npcs' in level_data:
            create_dialogue_npcs(self.game, level_data['dialogue_npcs'])

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
