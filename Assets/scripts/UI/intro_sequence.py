import pygame as pg
import time
from Assets.settings import *
import math
import os
import sys
from Assets.scripts.Util.font_manager import resource_path

class IntroSequence:

    def __init__(self, game):
        self.game = game
        self.active = False
        self.start_time = 0

        self.black_screen_duration = 2.0
        self.blur_duration = 2.5
        self.total_duration = self.black_screen_duration + self.blur_duration

        self.music_fade_duration = 8.0

        self.crash_sound_started = False
        self.high_pitch_sound_started = False
        self.high_pitch_fade_started = False
        self.music_started = False

        self.screen = game.screen
        self.screen_width, self.screen_height = self.screen.get_size()

        self.black_overlay = pg.Surface((self.screen_width, self.screen_height))
        self.black_overlay.fill((0, 0, 0))

        self.pulse_frequency = 0.8
        self.pulse_amplitude = 1.0

    def start(self):
        self.active = True
        self.start_time = time.time()

        self.crash_sound_started = False
        self.high_pitch_sound_started = False
        self.high_pitch_fade_started = False
        self.music_started = False

        self.game.sound.stop_music()
        self.game.sound.stop_sfx('intro_crash')
        self.game.sound.stop_sfx('intro_high_pitch')

    def update(self):
        if not self.active:
            return

        elapsed = time.time() - self.start_time
        transition_point = self.black_screen_duration - 0.5

        if not self.crash_sound_started:
            self.crash_sound_started = True
            self.game.sound.play_sfx('intro_crash', fade_ms=80)

        if not self.high_pitch_sound_started and elapsed >= transition_point:
            self.high_pitch_sound_started = True
            self.game.sound.play_sfx('intro_high_pitch', fade_ms=120)

        high_pitch_fade_start = self.total_duration - 1.5
        if (
            self.high_pitch_sound_started
            and not self.high_pitch_fade_started
            and elapsed >= high_pitch_fade_start
        ):
            self.high_pitch_fade_started = True
            self.game.sound.fadeout_sfx('intro_high_pitch', 1500)

        if elapsed >= self.total_duration:
            self._end_sequence()

    def _end_sequence(self):
        self.active = False

        self.game.sound.stop_sfx('intro_crash')
        self.game.sound.stop_sfx('intro_high_pitch')

        if not self.music_started:
            self.music_started = True
            self.start_music_with_fade()

        pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
        pg.mouse.get_rel()

        if self.game.level_manager.current_level == 1:
            self.game.disorienting_effects.start()

    def draw(self):
        if not self.active:
            return

        elapsed = time.time() - self.start_time

        if elapsed < self.black_screen_duration:
            self.screen.blit(self.black_overlay, (0, 0))
            return

        blur_elapsed = elapsed - self.black_screen_duration
        blur_progress = min(blur_elapsed / self.blur_duration, 1.0)

        current_screen = self.screen.copy()

        blur_intensity = max(0.0, 1.0 - blur_progress)
        self._apply_blur(current_screen, blur_intensity)

        pulse_intensity = self._calculate_pulse(blur_elapsed, blur_progress)
        self._apply_pulse(pulse_intensity)

    def _apply_blur(self, surface, intensity):
        if intensity <= 0:
            return

        scale_factor = max(0.1, 1.0 - (intensity * 0.5))

        small_width = max(1, int(self.screen_width * scale_factor))
        small_height = max(1, int(self.screen_height * scale_factor))

        small_surface = pg.transform.scale(surface, (small_width, small_height))
        blurred = pg.transform.scale(small_surface, (self.screen_width, self.screen_height))

        self.screen.blit(blurred, (0, 0))
    

    def _calculate_pulse(self, elapsed, progress):
        max_pulse = self.pulse_amplitude * (1.0 - (progress * 0.3))
        pulse = math.sin(elapsed * self.pulse_frequency * 2 * math.pi) * max_pulse
        return max(0.0, pulse + (max_pulse * 0.5))

    def _apply_pulse(self, intensity):
        if intensity <= 0:
            return

        pulse_overlay = pg.Surface((self.screen_width, self.screen_height), pg.SRCALPHA)
        pulse_overlay.fill((0, 0, 0, int(intensity * 150)))
        self.screen.blit(pulse_overlay, (0, 0))

        
    def start_music_with_fade(self):
        level = self.game.level_manager.current_level

        started = self.game.sound.play_music(level=level, loops=-1)
        if started:
            pg.mixer.music.set_volume(0.0)
            self.game.sound.fade_music_to_current_target(self.music_fade_duration)
