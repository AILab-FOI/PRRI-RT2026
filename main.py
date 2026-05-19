import pygame as pg
import gc
import time
import math
import random
import threading
import traceback


gc.set_threshold(25000, 50, 50)


from Assets.settings import *
from Assets.Levels.map import *
from Assets.scripts.Character.player import *
from Assets.scripts.Util.raycasting import *
from Assets.scripts.Util.object_renderer import *
from Assets.scripts.Util.sprite_object import *
from Assets.scripts.Util.object_handler import *
from Assets.scripts.Weapons.weapon import Pistol, SMG, PlasmaGun, Bat
from Assets.scripts.Weapons.bat_item import Bat_item
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
        pg.display.set_caption("PEST CONTROL")

        icon_path = resource_path('resources/icons/game_icon.ico')
        icon = pg.image.load(icon_path)
        pg.display.set_icon(icon)

        pg.mouse.set_visible(False)
        pg.event.set_grab(True)
        pg.mouse.get_rel()
        self.is_fullscreen = False
        self.update_display_mode()
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        self.level_load_done_event = pg.USEREVENT + 20
        self.level_load_failed_event = pg.USEREVENT + 21
        self.sound = Sound(self)
        self.menu = Menu(self)
        self.intro_sequence = IntroSequence(self)
        self.loading_screen = LoadingScreen(self)
        self.level_transition = LevelTransition(self)
        self.death_screen = DeathScreen(self)
        self.victory_screen = VictoryScreen(self)
        self.game_events = GameEvents(self)
        self.disorienting_effects = DisorientingEffects(self)
        self.weapon_classes = [Pistol, SMG, PlasmaGun, Bat]
        self.weapon_slot_count = len(self.weapon_classes)

        self.level_manager = LevelManager(self)
        self.wave_manager = None
        self._start_intro_after_loading = False
        self.loading_thread = None
        self.loading_exception = None
        self.loading_target_level = None

        self.bat_consumed_time = 0

        self._loading_in_progress=False

        self.player_level_start_ammo = {}
        self._last_snapshot_level = -1

        self.game_initialized = False
        self.show_menu(play_menu_music=True)
        

    def update_display_mode(self):
        if self.is_fullscreen:
            self.screen = pg.display.set_mode(RES, pg.FULLSCREEN)
        else:
            self.screen = pg.display.set_mode(RES)

        if hasattr(self, 'menu'):
            self.menu.screen = self.screen

    def _finish_level1_loading(self):
        self._start_intro_after_loading = True

    def _build_level_runtime(self):
        self.sound.stop_all_sfx()

        if not hasattr(self, 'map'):
            self.map = Map(self)
        self.map.load_level(self.level_manager.current_level)

        if not hasattr(self, 'player') or self.player is None:
            self.player = Player(self)
        else:
            saved = self.player_level_start_ammo
            self.player.reset()
            for i, data in saved.items():
                weapon = self.player.weapon_inventory[i]
                if weapon is not None:
                    weapon.bagAmount = data['bag']
                    weapon.currentMagAmmount = data['mag']

        if not hasattr(self, 'weapon'):
            self.weapon = None

        if not hasattr(self, 'object_renderer'):
            self.object_renderer = ObjectRenderer(self)

        if not hasattr(self, 'raycasting'):
            self.raycasting = RayCasting(self)

        if not hasattr(self, 'pathfinding'):
            self.pathfinding = PathFinding(self)

        if not hasattr(self, 'interaction'):
            self.interaction = Interaction(self)
        else:
            self.interaction.interaction_objects.clear()

        if not hasattr(self, 'dialogue_manager'):
            self.dialogue_manager = DialogueManager(self)

        if not hasattr(self, 'object_handler'):
            self.object_handler = ObjectHandler(self)
        else:
            self.object_handler.reset()

        self.wave_manager = self.object_handler.wave_manager

        if not hasattr(self, 'game_ui'):
            self.game_ui = GameUI(self)
        else:
            self.game_ui.update_level(self.level_manager.current_level)
            self.game_ui.bind_wave_manager()

        self.level_manager.setup_dialogue_npcs()
        self.level_manager.setup_interactive_objects()  
        self.pathfinding.update_graph()

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

        self.object_renderer.update_sky_image()
        self.sound.change_music_for_level(self.level_manager.current_level)

    
        if self._last_snapshot_level != self.level_manager.current_level:
            self._last_snapshot_level = self.level_manager.current_level

            
            LEVEL_ENTRY_AMMO_BONUS = {
                'pistol': 15,
                'smg':    35,
            }
            for i, weapon in enumerate(self.player.weapon_inventory):
                if weapon is None or not self.player.weapon_unlocked[i]:
                    continue
                bonus = LEVEL_ENTRY_AMMO_BONUS.get(weapon.name, 0)
                if bonus > 0:
                    weapon.bagAmount = min(999, weapon.bagAmount + bonus)

            self.player_level_start_ammo = {}
            for i, weapon in enumerate(self.player.weapon_inventory):
                if weapon is not None and self.player.weapon_unlocked[i]:
                    self.player_level_start_ammo[i] = {
                        'bag': weapon.bagAmount,
                        'mag': weapon.currentMagAmmount
                    }

    def _background_load_worker(self, level_number):
        try:
            self.level_manager.current_level = level_number
            self._build_level_runtime()
            pg.event.post(pg.event.Event(self.level_load_done_event, {"level_number": level_number}))
        except Exception:
            self.loading_exception = traceback.format_exc()
            pg.event.post(pg.event.Event(self.level_load_failed_event, {"level_number": level_number}))

    def begin_new_game_load(self, level_number):
        self.loading_target_level = level_number
        self.loading_exception = None
        self._start_intro_after_loading = False

        self.loading_screen.start(
            level_number=level_number,
            auto_continue=True,
            use_custom_level1_image=(level_number == 1),
            message="Loading...",
            on_complete_callback=self._finish_level1_loading if level_number == 1 else None
        )

        self.loading_screen.draw()
        pg.display.flip()

        self.loading_thread = threading.Thread(
            target=self._background_load_worker,
            args=(level_number,),
            daemon=True
        )
        self.loading_thread.start()

    def new_game(self):
        self.begin_new_game_load(self.level_manager.current_level)

    def update(self):
        if self.death_screen.active:
            self.death_screen.update()
            return

        if self.victory_screen.active:
            self.victory_screen.update()
            return

        self.loading_screen.update()
        self.level_transition.update()

        if self.loading_screen.active:
            self.sound.update()
            return

        if self._start_intro_after_loading:
            self.intro_sequence.start()
            self._start_intro_after_loading = False

        self.sound.update()

        if hasattr(self, 'player'):
            self.player.update()
        if hasattr(self, 'pathfinding'):
            self.pathfinding.update()
        if hasattr(self, 'raycasting'):
            self.raycasting.update()
        if hasattr(self, 'object_handler'):
            self.object_handler.update()

        if hasattr(self, 'weapon') and self.weapon:
            self.weapon.update()

        if hasattr(self, 'interaction'):
            self.interaction.update()
        if hasattr(self, 'dialogue_manager'):
            self.dialogue_manager.update()

        self.intro_sequence.update()
        self.disorienting_effects.update()

    def draw(self):
        if self.death_screen.active:
            self.death_screen.draw()
            return

        if self.victory_screen.active:
            self.victory_screen.draw()
            return

        if self.loading_screen.active:
            self.loading_screen.draw()
            self.level_transition.draw()
            pg.display.flip()
            return

        if hasattr(self, 'object_renderer'):
            self.object_renderer.draw()

        if hasattr(self, 'weapon') and self.weapon:
            self.weapon.draw()

        if hasattr(self, 'game_ui'):
            self.game_ui.draw()
        if hasattr(self, 'interaction'):
            self.interaction.draw()
        if hasattr(self, 'dialogue_manager'):
            self.dialogue_manager.draw()

        self.disorienting_effects.draw()
        self.intro_sequence.draw()
        self.level_transition.draw()

        pg.display.flip()

    def check_events(self):
        if self.death_screen.active:
            return self.death_screen.handle_events()

        if self.victory_screen.active:
            return self.victory_screen.handle_events()

        buffered_events = []
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return True
            if event.type == self.level_load_done_event:
                if self.loading_target_level == 1:
                    self.loading_screen.mark_loading_complete()
                    self.loading_screen.auto_continue = False
                    self.loading_screen.waiting_for_input = True
                else:
                    self.loading_screen.mark_loading_complete("Loading complete")
                    self.loading_screen.start_time = time.time() - max(0, self.loading_screen.duration - 0.15)
                continue
            
            if event.type == self.level_load_failed_event:
                self.loading_screen.mark_loading_complete("Loading failed")
                print(self.loading_exception)
                continue
 
            if self.loading_screen.active and self.loading_screen.handle_continue_key(event):
                continue
 
            buffered_events.append(event)
 
        for event in buffered_events:
            pg.event.post(event)
 
        return self.game_events.process_events()

    def next_level(self):
        return self.level_transition.transition_to_next_level()

    def reset_current_level(self):
        current_level = self.level_manager.current_level
        self.sound.current_music_level = -1
        self.begin_new_game_load(current_level)
        pg.mouse.set_visible(False)

    def respawn_player(self):
        if hasattr(self, 'player'):
            self.player.reset()

    def show_menu(self, play_menu_music=False):
        pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
        pg.event.set_grab(False)
        pg.mouse.set_visible(True)

        if play_menu_music:
            self.sound.change_music_for_level(0)

        self.menu.state = 'main'
        self.menu.run()

        if not self.game_initialized:
            if self.menu.start_mode == 'gauntlet':
                self.transition_to_runtime_level()
            else:
                self.begin_new_game_load(self.level_manager.current_level)
            self.game_initialized = True

        pg.event.set_grab(True)
        pg.mouse.set_visible(False)
        pg.mouse.get_rel()

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

        self.begin_new_game_load(runtime_level_number)

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
        elif chosen == 'powerups':
            self.object_handler.add_powerup(pos=pos)
        elif chosen == 'bat':
            import pygame as pg
            BAT_LOCKOUT_MS = 5000
            bat_slot = 3
            player = self.player
            player_has_bat = (
                player.weapon_inventory[bat_slot] is not None and
                player.weapon_unlocked[bat_slot]
            )
            bat_on_cooldown = (
                pg.time.get_ticks() - self.bat_consumed_time < BAT_LOCKOUT_MS
            )
            if not player_has_bat and not bat_on_cooldown:
                bat_item = Bat_item(self, pos=pos)
                self.object_handler.add_sprite(bat_item)

    def update_ammo_snapshot_for_slot(self, slot_index):
        weapon = self.player.weapon_inventory[slot_index]
        if weapon is None:
            return
        if slot_index not in self.player_level_start_ammo:
            self.player_level_start_ammo[slot_index] = {
                'bag': weapon.bagAmount,
                'mag': weapon.currentMagAmmount
            }

    def game_loop(self):
        while True:
            if self.check_events():
                return
            self.update()
            self.draw()
            self.delta_time = self.clock.tick(FPS)

    
    

if __name__ == '__main__':
    game = Game()
    while True:
        game.game_loop()
        game.show_menu(play_menu_music=False)