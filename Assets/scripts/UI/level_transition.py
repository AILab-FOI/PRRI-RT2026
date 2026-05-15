import pygame as pg
from Assets.settings import *


class ScreenTransitions:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.active = False
        self.fade_surface = pg.Surface(RES, pg.SRCALPHA)
        self.fade_alpha = 0
        self.fade_speed = 5
        self.fade_direction = 1
        self.fade_complete_callback = None

    def start_fade_in(self, speed=5, callback=None):
        self.active = True
        self.fade_alpha = 0
        self.fade_direction = 1
        self.fade_speed = speed
        self.fade_complete_callback = callback

    def start_fade_out(self, speed=5, callback=None):
        self.active = True
        self.fade_alpha = 255
        self.fade_direction = -1
        self.fade_speed = speed
        self.fade_complete_callback = callback

    def update(self):
        if not self.active:
            return

        self.fade_alpha += self.fade_speed * self.fade_direction

        if self.fade_alpha >= 255 and self.fade_direction > 0:
            self.fade_alpha = 255
            if self.fade_complete_callback:
                callback = self.fade_complete_callback
                self.fade_complete_callback = None
                callback()

        elif self.fade_alpha <= 0 and self.fade_direction < 0:
            self.fade_alpha = 0
            self.active = False
            if self.fade_complete_callback:
                callback = self.fade_complete_callback
                self.fade_complete_callback = None
                callback()

    def draw(self):
        if not self.active and self.fade_alpha <= 0:
            return

        self.fade_surface.fill((0, 0, 0, self.fade_alpha))
        self.screen.blit(self.fade_surface, (0, 0))


class LevelTransition:
    def __init__(self, game):
        self.game = game
        self.transition_state = None
        self.next_level_num = None
        self.loading_duration = 2000
        self.loading_start_time = 0
        self.screen_transitions = ScreenTransitions(game)

    def transition_to_next_level(self):
        self.next_level_num = self.game.level_manager.current_level + 1

        if (self.next_level_num > self.game.level_manager.max_level) and (self.next_level_num != 99):
            self.screen_transitions.start_fade_in(speed=8, callback=self._show_victory_screen)
            return True

        self.transition_state = "fade_out"
        self.screen_transitions.start_fade_in(speed=8, callback=self._show_loading_screen)
        return True

    def _show_victory_screen(self):
        self.game.victory_screen.start()
        self.transition_state = None
        self.screen_transitions.start_fade_out(speed=5)

    def _show_loading_screen(self):
        self.game.loading_screen.start(self.next_level_num)
        self.transition_state = "loading"
        self.loading_start_time = pg.time.get_ticks()
        self.screen_transitions.start_fade_out(speed=5)
        pg.time.set_timer(pg.USEREVENT + 1, 16)

    def update_loading_screen(self):
        if self.transition_state != "loading":
            return

        current_time = pg.time.get_ticks()
        if current_time - self.loading_start_time >= self.loading_duration:
            self._load_next_level()

    def _reset_wave_related_state(self):
        wave_manager = getattr(self.game, 'wave_manager', None)
        if wave_manager is not None:
            if hasattr(wave_manager, 'current_wave_remaining_to_spawn'):
                wave_manager.current_wave_remaining_to_spawn = 0
            if hasattr(wave_manager, 'current_wave_index'):
                wave_manager.current_wave_index = 0
            if hasattr(wave_manager, 'waves_config'):
                wave_manager.waves_config = []
            if hasattr(wave_manager, 'is_waiting_for_wave'):
                wave_manager.is_waiting_for_wave = False
            if hasattr(wave_manager, 'wave_spawn_time'):
                wave_manager.wave_spawn_time = 0
            if hasattr(wave_manager, 'spawn_wave'):
                try:
                    wave_manager.spawn_wave()
                except Exception:
                    pass
            elif hasattr(wave_manager, 'reset'):
                try:
                    wave_manager.reset()
                except Exception:
                    pass

        object_handler = getattr(self.game, 'object_handler', None)
        if object_handler is not None:
            if hasattr(object_handler, 'all_enemies_defeated'):
                object_handler.all_enemies_defeated = False
            if hasattr(object_handler, 'win_message_shown'):
                object_handler.win_message_shown = False

    def _load_next_level(self):
        if self.transition_state != "loading":
            return

        pg.time.set_timer(pg.USEREVENT + 1, 0)
        self.game.loading_screen.set_custom_message("LOADING LEVEL...")
        pg.display.flip()

        if self.game.level_manager.current_level == 1 and hasattr(self.game, 'disorienting_effects'):
            self.game.disorienting_effects.end_effects()

        self.game.level_manager.current_level = self.next_level_num
        self.game.map.load_level(self.next_level_num)
        self.game.new_game()
        self._reset_wave_related_state()

        if hasattr(self.game, 'game_ui'):
            self.game.game_ui.update_level(self.next_level_num)

        self.screen_transitions.start_fade_in(speed=8, callback=self._finish_transition)
        self.transition_state = "fading_to_game"

    def _finish_transition(self):
        self.transition_state = None
        pg.time.set_timer(pg.USEREVENT + 1, 0)
        self.screen_transitions.start_fade_out(speed=5)

    def handle_event(self, event):
        if self.transition_state == "loading" and event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            self._load_next_level()
            return True

        if event.type == pg.USEREVENT + 1:
            self.update_loading_screen()
            return True

        return False

    def update(self):
        self.screen_transitions.update()

    def draw(self):
        self.screen_transitions.draw()