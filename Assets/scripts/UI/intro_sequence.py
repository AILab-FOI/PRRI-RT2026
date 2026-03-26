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
        self.black_screen_duration = 2
        self.blur_duration = 2.5
        self.total_duration = self.black_screen_duration + self.blur_duration

        self.high_pitch_delay = self.black_screen_duration
        self.music_delay = self.total_duration + 1.0
        self.music_fade_duration = 8.0
        self.original_music_volume = 0.3

        try:
            crash_sound_path = resource_path('resources/sound/crash.wav')
            high_pitch_sound_path = resource_path('resources/sound/high_pitch.wav')
            self.crash_sound = pg.mixer.Sound(crash_sound_path)
            self.high_pitch_sound = pg.mixer.Sound(high_pitch_sound_path)
            self.sounds_loaded = True
        except Exception as e:
            self.sounds_loaded = False

        self.screen = game.screen
        self.screen_width, self.screen_height = self.screen.get_size()
        self.black_overlay = pg.Surface((self.screen_width, self.screen_height))
        self.black_overlay.fill((0, 0, 0))

        self.blur_surface = pg.Surface((self.screen_width, self.screen_height), pg.SRCALPHA)
        self.pulse_frequency = 0.8
        self.pulse_amplitude = 1.0

    def start(self):
        self.active = True
        self.start_time = time.time()

        self.crash_sound_started = False
        self.high_pitch_sound_started = False
        self.music_started = False

        self.original_music_volume = pg.mixer.music.get_volume()
        pg.mixer.music.stop()

    def update(self):
        if not self.active:
            return

        elapsed = time.time() - self.start_time

        if not self.crash_sound_started and self.sounds_loaded:
            self.crash_sound_started = True
            self.crash_sound.set_volume(0.5)
            self.crash_sound.play()

        transition_point = self.black_screen_duration - 0.5
        if self.crash_sound_started and elapsed >= transition_point and elapsed < self.black_screen_duration:
            progress = (elapsed - transition_point) / (self.black_screen_duration - transition_point)
            volume = 0.5 - (progress * 0.4)
            self.crash_sound.set_volume(max(0.1, volume))

        if not self.high_pitch_sound_started and elapsed >= transition_point and self.sounds_loaded:
            self.high_pitch_sound_started = True
            self.high_pitch_sound.set_volume(0.1)
            self.high_pitch_sound.play()

        if self.high_pitch_sound_started and elapsed < self.black_screen_duration + 1.0:
            if elapsed < self.black_screen_duration:
                progress = (elapsed - transition_point) / (self.black_screen_duration - transition_point)
                volume = 0.1 + (progress * 0.4)
            else:
                progress = (elapsed - self.black_screen_duration) / 1.0
                volume = 0.5 + (progress * 0.5)

            self.high_pitch_sound.set_volume(min(1.0, volume))

        high_pitch_fade_start = self.total_duration - 1.5

        if self.high_pitch_sound_started and elapsed >= high_pitch_fade_start and elapsed < self.total_duration:
            fade_progress = (elapsed - high_pitch_fade_start) / 1.5
            volume = 1.0 - fade_progress
            self.high_pitch_sound.set_volume(max(0.0, volume))

        if elapsed >= self.total_duration:
            self._end_sequence()
            return

    def _end_sequence(self):
        self.active = False

        if self.sounds_loaded:
            self.crash_sound.stop()
            self.high_pitch_sound.stop()

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

        blur_intensity = max(0, 1.0 - blur_progress)
        self._apply_blur(current_screen, blur_intensity)

        pulse_intensity = self._calculate_pulse(blur_elapsed, blur_progress)
        self._apply_pulse(pulse_intensity)

    def _apply_blur(self, surface, intensity):
        if intensity <= 0:
            return

        blur_size = int(intensity * 10)
        if blur_size <= 0:
            return

        scale_factor = max(0.1, 1.0 - (intensity * 0.5))
        small_surface = pg.transform.scale(
            surface,
            (int(self.screen_width * scale_factor),
             int(self.screen_height * scale_factor))
        )

        blurred = pg.transform.scale(
            small_surface,
            (self.screen_width, self.screen_height)
        )

        self.screen.blit(blurred, (0, 0))

    def _calculate_pulse(self, elapsed, progress):
        max_pulse = self.pulse_amplitude * (1.0 - (progress * 0.3))
        pulse = math.sin(elapsed * self.pulse_frequency * 2 * math.pi) * max_pulse
        return max(0, pulse + (max_pulse * 0.5))

    def _apply_pulse(self, intensity):
        if intensity <= 0:
            return

        pulse_overlay = pg.Surface((self.screen_width, self.screen_height), pg.SRCALPHA)
        pulse_overlay.fill((0, 0, 0, int(intensity * 150)))
        self.screen.blit(pulse_overlay, (0, 0))

    def start_music_with_fade(self):
        pg.mixer.music.set_volume(0.0)
        pg.mixer.music.play(-1)
        self.fade_start_time = time.time()
        self.fading_music = True

    def update_music_fade(self):
        if not hasattr(self, 'fading_music') or not self.fading_music:
            return

        elapsed = time.time() - self.fade_start_time
        fade_progress = min(1.0, elapsed / self.music_fade_duration)

        if fade_progress < 0.5:
            curve_progress = fade_progress * fade_progress * 2
        else:
            quadratic = fade_progress * fade_progress * 2
            linear = fade_progress
            blend_factor = (fade_progress - 0.5) * 2
            curve_progress = quadratic * (1 - blend_factor) + linear * blend_factor

        current_volume = curve_progress * self.original_music_volume
        pg.mixer.music.set_volume(current_volume)

        if fade_progress >= 1.0:
            self.fading_music = False
