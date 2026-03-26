import pygame as pg
import math
import time
from settings import *

class DisorientingEffects:
    def __init__(self, game):
        self.game = game
        self.active = False
        self.start_time = 0
        self.duration = 60.0

        # Distortion effect parameters
        self.distortion_intensity = 0
        self.max_distortion = 0.55
        self.distortion_speed = 0.001
        self.distortion_direction = 1

        # Tilt effect parameters
        self.tilt_angle = 0
        self.max_tilt = 0.15
        self.tilt_speed = 0.0006
        self.tilt_direction = 1

        # Flash effect parameters
        self.flash_intensity = 0
        self.flash_timer = 0
        self.flash_interval = 3.5
        self.flash_duration = 2.5

        # Create surfaces for effects
        self.screen = game.screen
        self.screen_width, self.screen_height = self.screen.get_size()
        self.effect_surface = pg.Surface((self.screen_width, self.screen_height), pg.SRCALPHA)

        # Pulse parameters
        self.pulse_frequency = 0.9
        self.pulse_amplitude = 0.5
        self.pulse_offset = 0

        # Blur effect parameters
        self.blur_intensity = 0
        self.max_blur = 1.0
        self.blur_speed = 0.002
        self.blur_direction = 1
        self.blur_surface = pg.Surface((self.screen_width, self.screen_height))

        # Double vision effect parameters
        self.double_vision_offset = 0
        self.max_double_vision = 50
        self.double_vision_speed = 0.3

    def start(self):
        """Start the disorienting effects"""
        if self.game.level_manager.current_level != 1:
            return

        self.active = True
        self.start_time = time.time()

    def update(self):
        """Update the disorienting effects"""
        if not self.active:
            return

        elapsed = time.time() - self.start_time
        if elapsed >= self.duration:
            self.end_effects()
            return

        # Calculate intensity based on time with decay
        time_factor = 1.0 - (elapsed / self.duration)
        quadratic = time_factor * time_factor
        cubic = time_factor * time_factor * time_factor
        base_intensity = cubic * 0.7 + quadratic * 0.3
        intensity_factor = base_intensity * 0.9 + 0.1

        # Update all effects
        self._update_distortion(intensity_factor)
        self._update_tilt(intensity_factor)
        self._update_flash(elapsed, intensity_factor)
        self._update_pulse(elapsed, intensity_factor)
        self._update_blur(intensity_factor)
        self._update_double_vision(elapsed, intensity_factor)

    def _update_distortion(self, intensity):
        """Update the distortion effect"""
        adjusted_max = self.max_distortion * ((intensity * intensity * 0.6) + (intensity * 0.4))

        if self.distortion_intensity >= adjusted_max:
            self.distortion_direction = -1
        elif self.distortion_intensity <= 0:
            self.distortion_direction = 1

        adjusted_speed = self.distortion_speed * 1.3 * intensity
        self.distortion_intensity += adjusted_speed * self.distortion_direction * intensity
        self.distortion_intensity = min(adjusted_max, self.distortion_intensity)

    def _update_tilt(self, intensity):
        """Update the tilt effect"""
        adjusted_max_tilt = self.max_tilt * ((intensity * intensity * 0.6) + (intensity * 0.4))

        if self.tilt_angle >= adjusted_max_tilt:
            self.tilt_direction = -1
        elif self.tilt_angle <= -adjusted_max_tilt:
            self.tilt_direction = 1

        adjusted_speed = self.tilt_speed * 1.3 * intensity
        self.tilt_angle += adjusted_speed * self.tilt_direction * intensity

    def _update_flash(self, elapsed, intensity):
        """Update the flash effect"""
        flash_intensity_factor = (intensity * intensity * 0.6) + (intensity * 0.4)
        adjusted_interval = self.flash_interval * (2.5 - intensity * 1.5)

        # Check if it's time for a flash
        if elapsed - self.flash_timer >= adjusted_interval:
            self.flash_timer = elapsed
            self.flash_intensity = flash_intensity_factor

        # Decrease flash intensity over time
        if self.flash_intensity > 0:
            time_since_flash = elapsed - self.flash_timer
            adjusted_duration = self.flash_duration * flash_intensity_factor

            if time_since_flash < adjusted_duration:
                progress = time_since_flash / adjusted_duration
                self.flash_intensity = flash_intensity_factor * (1.0 - (progress * 1.2))
                self.flash_intensity = max(0, self.flash_intensity)
            else:
                self.flash_intensity = 0

    def _update_pulse(self, elapsed, intensity):
        """Update the pulse effect"""
        adjusted_amplitude = self.pulse_amplitude * intensity
        self.pulse_offset = math.sin(elapsed * self.pulse_frequency * 2 * math.pi) * adjusted_amplitude

    def draw(self):
        """Draw the disorienting effects"""
        if not self.active:
            return

        # Apply effects in order of visual layering
        if self.blur_intensity > 0.1:
            self._apply_blur()

        if abs(self.double_vision_offset) > 1:
            self._apply_double_vision()

        if self.distortion_intensity > 0:
            self._apply_distortion()

        if self.flash_intensity > 0:
            self._apply_flash()

    def _apply_distortion(self):
        """Apply a wavy distortion effect to the screen"""
        screen_copy = self.screen.copy()
        self.screen.fill((0, 0, 0))

        for y in range(0, self.screen_height, 2):
            wave_offset = int(math.sin(y * 0.09 + time.time() * 2.0) * 30 * self.distortion_intensity)
            self.screen.blit(screen_copy, (wave_offset, y), (0, y, self.screen_width, 2))

    def _apply_flash(self):
        """Apply a flash effect to the screen"""
        flash_surface = pg.Surface((self.screen_width, self.screen_height), pg.SRCALPHA)
        flash_surface.fill((255, 255, 255, int(180 * self.flash_intensity)))
        self.screen.blit(flash_surface, (0, 0))

    def _apply_blur(self):
        """Apply a blur effect to simulate dizziness"""
        screen_copy = self.screen.copy()

        blur_size = int(self.blur_intensity * 10)
        if blur_size < 1:
            return

        # Create blur by scaling down and back up
        scale_factor = max(0.1, 1.0 - (self.blur_intensity * 0.5))
        small_surface = pg.transform.scale(
            screen_copy,
            (int(self.screen_width * scale_factor),
             int(self.screen_height * scale_factor))
        )

        blurred = pg.transform.scale(
            small_surface,
            (self.screen_width, self.screen_height)
        )

        self.screen.blit(blurred, (0, 0))

    def _apply_double_vision(self):
        """Apply a double vision effect to simulate dizziness"""
        screen_copy = self.screen.copy()

        offset_x = int(self.double_vision_offset)
        if abs(offset_x) < 1:
            return

        ghost_surface = pg.Surface((self.screen_width, self.screen_height), pg.SRCALPHA)
        ghost_surface.blit(screen_copy, (0, 0))
        ghost_surface.set_alpha(128)  # 50% opacity

        self.screen.blit(ghost_surface, (offset_x, 0))

    def _update_blur(self, intensity):
        """Update the blur effect"""
        blur_intensity_factor = (intensity * intensity * 0.6) + (intensity * 0.4)
        adjusted_max = self.max_blur * blur_intensity_factor

        if self.blur_intensity >= adjusted_max:
            self.blur_direction = -1
        elif self.blur_intensity <= 0.15 * blur_intensity_factor:
            self.blur_direction = 1

        adjusted_speed = self.blur_speed * 1.3 * blur_intensity_factor
        self.blur_intensity += adjusted_speed * self.blur_direction * blur_intensity_factor
        self.blur_intensity = max(0.15 * blur_intensity_factor, min(adjusted_max, self.blur_intensity))

    def _update_double_vision(self, elapsed, intensity):
        """Update the double vision effect"""
        double_vision_factor = (intensity * intensity * 0.6) + (intensity * 0.4)
        adjusted_max = self.max_double_vision * double_vision_factor
        self.double_vision_offset = math.sin(elapsed * self.double_vision_speed) * adjusted_max

    def end_effects(self):
        """End the disorienting effects"""
        self.active = False
