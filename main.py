
import pygame as pg
import gc
import time
import math
import random


# Reduce GC frequency to avoid periodic FPS drops.
# Default (700, 10, 10) causes frequent pauses in game loops.
gc.set_threshold(25000, 50, 50)

from Assets.settings import *
from Assets.Levels.map import *
from Assets.scripts.Character.player import *
from Assets.scripts.Util.raycasting import *
from Assets.scripts.Util.object_renderer import *
from Assets.scripts.Util.sprite_object import *
from Assets.scripts.Util.object_handler import *
from Assets.scripts.Weapons.weapon import Pistol, SMG, PlasmaGun
from Assets.sound import *
from Assets.scripts.Util.pathfinding import *
from Assets.scripts.Character.interaction import Interaction
from Assets.Levels.level_manager import LevelManager
from Assets.dialogue import DialogueManager
from Assets.scripts.UI.menu import Menu
from Assets.scripts.UI.intro_sequence import IntroSequence
from Assets.scripts.UI.loading_screen import LoadingScreen
from Assets.scripts.UI.level_transition import LevelTransition
from Assets.game_events import GameEvents
from Assets.scripts.UI.death_screen import DeathScreen
from Assets.scripts.UI.victory_screen import VictoryScreen
from Assets.scripts.UI.ui import GameUI
from Assets.scripts.Effects.visual_effects import DisorientingEffects
from Assets.scripts.Util.font_manager import resource_path
from Assets.scripts.MapGenerator.runtime_level import build_runtime_level

class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption("*INSERT NEW GAME NAME HERE*")

        icon_path = resource_path('resources/icons/game_icon.ico')
        icon = pg.image.load(icon_path)
        pg.display.set_icon(icon)

        pg.mouse.set_visible(False)
        pg.event.set_grab(True)  # lock mouse inside window
        pg.mouse.get_rel()       # reset cursor to center
        self.is_fullscreen = False
        self.update_display_mode()
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        self.sound = Sound(self)
        self.menu = Menu(self)
        self.intro_sequence = IntroSequence(self)
        self.loading_screen = LoadingScreen(self)
        self.level_transition = LevelTransition(self)
        self.death_screen = DeathScreen(self)
        self.victory_screen = VictoryScreen(self)
        self.game_events = GameEvents(self)
        self.disorienting_effects = DisorientingEffects(self)
        self.weapon_classes = [Pistol, SMG, PlasmaGun]
        self.weapon_slot_count = len(self.weapon_classes)

        self.level_manager = LevelManager(self)

        self.game_initialized = False
        self.show_menu(play_menu_music=True)

    def update_display_mode(self):
        if self.is_fullscreen:
            self.screen = pg.display.set_mode(RES, pg.FULLSCREEN)
        else:
            self.screen = pg.display.set_mode(RES)

        if hasattr(self, 'menu'):
            self.menu.screen = self.screen

    def new_game(self):
        # --- 1. ALWAYS create map and then load the current level ---

        if not hasattr(self, 'map'):
            self.map = Map(self)

        self.map.load_level(self.level_manager.current_level)

        # --- 2. Core objects (only create once, otherwise reset) ---

        if not hasattr(self, 'player'):
            self.player = Player(self)
        else:
            self.player.reset()

        if not hasattr(self, 'weapon'):
            self.weapon = None

        if not hasattr(self, 'object_renderer'):
            self.object_renderer = ObjectRenderer(self)

        if not hasattr(self, 'raycasting'):
            self.raycasting = RayCasting(self)

        if not hasattr(self, 'object_handler'):
            self.object_handler = ObjectHandler(self)
        else:
            self.object_handler.reset()

        if not hasattr(self, 'pathfinding'):
            self.pathfinding = PathFinding(self)

        if not hasattr(self, 'interaction'):
            self.interaction = Interaction(self)

        if not hasattr(self, 'dialogue_manager'):
            self.dialogue_manager = DialogueManager(self)

        if not hasattr(self, 'game_ui'):
            self.game_ui = GameUI(self)
        else:
            self.game_ui.update_level(self.level_manager.current_level)

        # --- 3. Setup world data on top of the loaded map ---

        self.level_manager.setup_dialogue_npcs()
        self.level_manager.setup_interactive_objects()
        self.pathfinding.update_graph()

        # --- 4. Spawn player ---

        current_level_data = self.level_manager.get_current_level_data()
        spawn = current_level_data.get('player_spawn') if current_level_data else None

        if spawn:
            self.player.x, self.player.y = spawn
            self.player.angle = 0
        elif self.level_manager.current_level == 1:
            self.player.x, self.player.y = PLAYER_POS
        elif self.level_manager.current_level == 2:
            self.player.x, self.player.y = PLAYER_POS_LEVEL2
            self.player.angle = math.pi / 2
        elif self.level_manager.current_level == 3:
            self.player.x, self.player.y = PLAYER_POS_LEVEL3
        elif self.level_manager.current_level == 4:
            self.player.x, self.player.y = PLAYER_POS_LEVEL4
        elif self.level_manager.current_level == 5:
            self.player.x, self.player.y = PLAYER_POS_LEVEL5
        elif self.level_manager.current_level == 6:
            self.player.x, self.player.y = PLAYER_POS_LEVEL6

        # --- 5. Audio and UI ---

        self.object_renderer.update_sky_image()
        self.sound.change_music_for_level(self.level_manager.current_level)

        if self.level_manager.current_level == 1:
            self.intro_sequence.start()

    def update(self):
        if self.death_screen.active:
            self.death_screen.update()
            return

        if self.victory_screen.active:
            self.victory_screen.update()
            return

        self.sound.update()

        self.player.update()
        self.pathfinding.update()
        self.raycasting.update()
        self.object_handler.update()
        if self.weapon:
            self.weapon.update()
        self.interaction.update()
        self.dialogue_manager.update()

        self.intro_sequence.update()
        self.disorienting_effects.update()
        self.loading_screen.update()
        self.level_transition.update()

        pg.display.flip()
        self.delta_time = self.clock.tick(FPS)

    def draw(self):
        if self.death_screen.active:
            self.death_screen.draw()
            return

        if self.victory_screen.active:
            self.victory_screen.draw()
            return

        self.object_renderer.draw()
        if self.weapon:
            self.weapon.draw()
        self.game_ui.draw()
        self.interaction.draw()
        self.dialogue_manager.draw()

        self.disorienting_effects.draw()
        self.intro_sequence.draw()
        self.loading_screen.draw()
        self.level_transition.draw()

    def check_events(self):
        if self.death_screen.active:
            return self.death_screen.handle_events()

        if self.victory_screen.active:
            return self.victory_screen.handle_events()

        return self.game_events.process_events()

    def next_level(self):
        return self.level_transition.transition_to_next_level()

    def reset_current_level(self):
        current_level = self.level_manager.current_level
        self.sound.current_music_level = -1
        self.map.load_level(current_level)
        self.new_game()
        pg.mouse.set_visible(False)

    def show_menu(self, play_menu_music=False):
        pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
        pg.event.set_grab(False)
        pg.mouse.set_visible(True)

        if play_menu_music:
            self.sound.change_music_for_level(0)

        self.menu.state = 'main'
        self.menu.run()

        if not self.game_initialized:
            self.transition_to_runtime_level()
            self.game_initialized = True

        pg.event.set_grab(True)
        pg.mouse.set_visible(False)
        pg.mouse.get_rel()
        self.game_loop()

    def transition_to_runtime_level(self):
        seed = int(time.time())
        runtime_level_number = 99

        level_data = build_runtime_level(seed)
        self.level_manager.register_runtime_level(runtime_level_number, level_data)
        self.level_manager.current_level = runtime_level_number

        print(f"[DEBUG] Generated runtime level with seed: {seed}")
        print(f"[DEBUG] Player spawn: {level_data.get('player_spawn')}")
        for row in level_data['map']:
            print(row)

        self.new_game()
        
    def spawn_npc_drop(self, pos):
        if not NPC_DROP_SETTINGS.get('enabled', False):
            return

        if random.randint(1, 100) > NPC_DROP_SETTINGS.get('drop_chance', 0):
            return

        weights = NPC_DROP_SETTINGS.get('item_weights', {})
        chosen = random.choices(list(weights.keys()), weights=list(weights.values()), k=1)[0]

        if chosen == 'heal':
            self.object_handler.add_heal_item(pos=pos)
        elif chosen == 'ammo':
            self.object_handler.add_ammo_item(pos=pos)
        
    

    def game_loop(self):
        while True:
            if self.check_events():
                return
            self.update()
            self.draw()


if __name__ == '__main__':
    game = Game()
    
    