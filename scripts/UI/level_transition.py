import pygame as pg
from settings import *

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
                self.fade_complete_callback()
                self.fade_complete_callback = None

        elif self.fade_alpha <= 0 and self.fade_direction < 0:
            self.fade_alpha = 0
            self.active = False
            if self.fade_complete_callback:
                self.fade_complete_callback()
                self.fade_complete_callback = None

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
        self.screen_transitions = ScreenTransitions(game)

    def transition_to_next_level(self):
        self.next_level_num = self.game.level_manager.current_level + 1

        if self.next_level_num > self.game.level_manager.max_level:
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

    def _load_next_level(self):
        self.game.loading_screen.set_custom_message("LOADING LEVEL...")
        pg.display.flip()

        if self.game.level_manager.current_level == 1 and hasattr(self.game, 'disorienting_effects'):
            self.game.disorienting_effects.end_effects()

        self.game.level_manager.current_level = self.next_level_num
        self.game.map.load_level(self.next_level_num)
        self.game.new_game()
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
