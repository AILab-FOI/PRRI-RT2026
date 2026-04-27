import pygame as pg
import os
import sys


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class Sound:
    def __init__(self, game):
        self.game = game
        
        if not pg.mixer.init():
            pg.mixer.init()
        
        self.path = 'resources/sound'

        # Slider state: keep UI-friendly percentages here.
        self.sfx_slider_percent = 35
        self.music_slider_percent = 35

        # Master caps so 100% is still sane.
        self.sfx_master_max = 0.18
        self.music_master_max = 0.28

        # Curves so low slider values are more usable.
        self.sfx_curve_power = 2.2
        self.music_curve_power = 2.0

        self.sfx_volume = self._slider_to_sfx_volume(self.sfx_slider_percent)
        self.music_volume = self._slider_to_music_volume(self.music_slider_percent)

        self.normal_music_volume = self.music_volume
        self.ducking_factor = 0.25
        self.is_ducking = False

        self.volume_factors = {
            # Weapon sounds
            'pistolj': 0.45,
            'smg': 0.28,
            'plasmagun': 0.35,
            'weapon_pickup': 0.35,

            # Player sounds
            'igrac_damage': 0.35,
            'player_dash': 0.25,

            # Game state sounds
            'victory': 0.40,
            'defeat': 0.32,

            # Generic NPC sounds
            'npc_pain': 0.30,
            'npc_death': 0.45,
            'npc_attack': 0.30,

            # Enemy-specific sounds
            'napad_stakor': 0.35,
            'stakor_smrt': 0.45,

            'toster_attack': 0.30,
            'toster_death': 0.45,
            'toster_damage': 0.30,

            'parazit_attack': 0.35,
            'parazit_death': 0.45,
            'parazit_damage': 0.30,

            'jazavac_attack': 0.30,
            'jazavac_death': 0.45,
            'jazavac_damage': 0.30,

            'madrac_attack': 0.35,
            'madrac_death': 0.45,
            'madrac_damage': 0.30,

            'boss_attack': 0.40,
            'boss_death': 0.55,
            'boss_damage': 0.35,

            # Interaction sounds
            'terminal_beep': 0.25,
            'door_open': 0.30,

            # Powerup sounds
            'powerup_pickup': 0.35,
            'powerup_active': 0.25,
            'powerup_end': 0.25,

            # Menu sounds
            'menu_hover': 0.12,
            'menu_click': 0.18,

            # Dialogue sounds
            'dialogue_line': 0.22,

            # Misc
            'footstep': 0.10,
            'heal': 0.25,

            # Intro sequence sounds
            'intro_crash': 0.30,
            'intro_high_pitch': 0.18,
        }

        self.sound_files = {
            # Weapon sounds
            'pistolj': 'Pistolj.wav',
            'smg': 'Puska.wav',
            'plasmagun': 'plasmaGun.wav',
            'weapon_pickup': 'podizanje_oruzja.wav',

            # Player sounds
            'igrac_damage': 'Igrac_damage.wav',
            'player_dash': 'Dash.wav',

            # Generic NPC sounds
            'npc_pain': 'npc_pain.wav',
            'npc_death': 'npc_death.wav',
            'npc_attack': 'npc_attack.wav',

            # Enemy-specific sounds
            'napad_stakor': 'stakor_napad.mp3',
            'stakor_smrt': 'stakor_smrt.mp3',

            'toster_attack': 'toster_napad.wav',
            'toster_death': 'toster_smrt.mp3',
            'toster_damage': 'toster_damage.wav',

            'parazit_attack': 'parazit_napad.mp3',
            'parazit_death': 'parazit_smrt.wav',
            'parazit_damage': 'parazit_damage.mp3',

            'jazavac_attack': 'jazavac_napad.wav',
            'jazavac_death': 'jazavac_smrt.wav',
            'jazavac_damage': 'jazavac_damage.wav',

            'madrac_attack': 'madrac_napad.wav',
            'madrac_death': 'madrac_smrt.wav',
            'madrac_damage': 'madrac_damage.wav',

            'boss_attack': 'boss_napad.wav',
            'boss_death': 'boss_smrt.wav',
            'boss_damage': 'boss_damage.wav',

            # Interaction sounds
            'terminal_beep': 'terminal.wav',
            'door_open': 'vrata.wav',

            # Powerup sounds
            'powerup_pickup': 'powerup_pickup.wav',
            'powerup_active': 'powerup1_trajanje.wav',
            'powerup_end': 'powerup_gasenje.wav',

            # Menu sounds
            'menu_hover': 'menu_hover.mp3',
            'menu_click': 'menu_klik.wav',

            # Game state sounds
            'victory': 'pobjeda.mp3',
            'defeat': 'poraz.mp3',

            # Misc
            'footstep': 'walking_v2.mp3',
            'heal': 'healcan1.mp3',

            # Intro sequence
            'intro_crash': 'crash.wav',
            'intro_high_pitch': 'high_pitch.wav',
        }

        self.background_music = {
            1: 'Pozadinska1.mp3',
            2: 'Pozadinska2.wav',
            3: 'Pozadinska3.mp3',
            4: 'Pozadinska4.wav',
            5: 'Pozadinska5.wav'
        }

        self.sounds = {}
        self.dialogue_sounds = {}
        self.current_music_level = None

        self.music_fade_active = False
        self.music_fade_start_time = 0
        self.music_fade_duration_ms = 0
        self.music_fade_start_volume = 0.0
        self.music_fade_target_volume = 0.0

        self._load_all_sounds()
        self._apply_all_sfx_volumes()
        pg.mixer.music.set_volume(self._get_current_music_volume())
        
    #INTERNAL FUNCTIONS
    
    def _full_sound_path(self, filename):
        return resource_path(os.path.join(self.path, filename))

    def _slider_to_sfx_volume(self, slider_percent):
        x = max(0.0, min(1.0, slider_percent / 100.0))
        return (x ** self.sfx_curve_power) * self.sfx_master_max

    def _slider_to_music_volume(self, slider_percent):
        x = max(0.0, min(1.0, slider_percent / 100.0))
        return (x ** self.music_curve_power) * self.music_master_max

    def _load_sound_file(self, filename):
        try:
            return pg.mixer.Sound(self._full_sound_path(filename))
        except Exception:
            return None

    def _load_all_sounds(self):
        for sound_name, filename in self.sound_files.items():
            self.sounds[sound_name] = self._load_sound_file(filename)

        # Backwards compatibility with old attribute-style access.
        for sound_name, sound in self.sounds.items():
            setattr(self, sound_name, sound)

    def _apply_all_sfx_volumes(self):
        for sound_name, sound in self.sounds.items():
            if sound is not None:
                base_factor = self.volume_factors.get(sound_name, 1.0)
                sound.set_volume(base_factor * self.sfx_volume)

        for _, sound in self.dialogue_sounds.items():
            if sound is not None:
                sound.set_volume(self.volume_factors['dialogue_line'] * self.sfx_volume)

    def _get_current_music_volume(self):
        if self.is_ducking:
            return self.normal_music_volume * self.ducking_factor
        return self.normal_music_volume
    
    
    # PUBLIC FUNCTIONS TO CALL
    
    def set_sfx_slider(self, percent):
        self.sfx_slider_percent = max(0, min(100, int(percent)))
        self.sfx_volume = self._slider_to_sfx_volume(self.sfx_slider_percent)
        self._apply_all_sfx_volumes()

    def set_music_slider(self, percent):
        self.music_slider_percent = max(0, min(100, int(percent)))
        self.music_volume = self._slider_to_music_volume(self.music_slider_percent)
        self.normal_music_volume = self.music_volume
        pg.mixer.music.set_volume(self._get_current_music_volume())

    # Optional compatibility with code that still directly sets float values.
    def set_sfx_volume(self, value):
        value = max(0.0, min(1.0, float(value)))
        self.sfx_volume = value
        self._apply_all_sfx_volumes()

    def set_music_volume(self, value):
        value = max(0.0, min(1.0, float(value)))
        self.music_volume = value
        self.normal_music_volume = value
        pg.mixer.music.set_volume(self._get_current_music_volume())

    def update_sfx_volume(self):
        self._apply_all_sfx_volumes()

    def update_music_volume(self):
        pg.mixer.music.set_volume(self._get_current_music_volume())
        
        # ------------------------------------------------------------------
    # SFX API
    # ------------------------------------------------------------------

    def get_sound(self, sound_name):
        return self.sounds.get(sound_name)

    def play_sfx(self, sound_name, loops=0, maxtime=0, fade_ms=0):
        sound = self.sounds.get(sound_name)
        if sound is None:
            return None
        return sound.play(loops=loops, maxtime=maxtime, fade_ms=fade_ms)

    def stop_sfx(self, sound_name):
        sound = self.sounds.get(sound_name)
        if sound is not None:
            sound.stop()

    def fadeout_sfx(self, sound_name, time_ms):
        sound = self.sounds.get(sound_name)
        if sound is not None:
            sound.fadeout(time_ms)

    def stop_all_sfx(self):
        pg.mixer.stop()

    def fadeout_all_sfx(self, time_ms):
        pg.mixer.fadeout(time_ms)

    # ------------------------------------------------------------------
    # Music API
    # ------------------------------------------------------------------

    def load_music_for_level(self, level):
        if level not in self.background_music:
            return False

        try:
            music_path = self._full_sound_path(self.background_music[level])
            pg.mixer.music.load(music_path)
            self.current_music_level = level

            # Pygame resets volume when new music is loaded, so reapply it.
            pg.mixer.music.set_volume(self._get_current_music_volume())
            return True
        except Exception:
            return False

    def play_music(self, level=None, loops=-1, start=0.0, fade_ms=0):
        if level is not None:
            loaded = self.load_music_for_level(level)
            if not loaded:
                return False

        pg.mixer.music.set_volume(self._get_current_music_volume())
        pg.mixer.music.play(loops=loops, start=start, fade_ms=fade_ms)
        return True

    def stop_music(self):
        pg.mixer.music.stop()
        self.music_fade_active = False

    def pause_music(self):
        pg.mixer.music.pause()

    def unpause_music(self):
        pg.mixer.music.unpause()

    def fadeout_music(self, time_ms):
        pg.mixer.music.fadeout(time_ms)
        self.music_fade_active = False

    def duck_music(self):
        self.is_ducking = True
        pg.mixer.music.set_volume(self._get_current_music_volume())

    def unduck_music(self):
        self.is_ducking = False
        pg.mixer.music.set_volume(self._get_current_music_volume())

    def fade_music_to(self, target_volume, duration_seconds):
        self.music_fade_active = True
        self.music_fade_start_time = pg.time.get_ticks()
        self.music_fade_duration_ms = max(1, int(duration_seconds * 1000))
        self.music_fade_start_volume = pg.mixer.music.get_volume()
        self.music_fade_target_volume = max(0.0, min(1.0, target_volume))

    def fade_music_to_current_target(self, duration_seconds):
        self.fade_music_to(self._get_current_music_volume(), duration_seconds)

    def change_music_for_level(self, level, fade_ms=0):
        if level not in self.background_music:
            return

        change_music = level != self.current_music_level

        if not pg.mixer.music.get_busy():
            change_music = True

        if change_music:
            self.play_music(level=level, loops=-1, fade_ms=fade_ms)

    # ------------------------------------------------------------------
    # Dialogue API
    # ------------------------------------------------------------------

    def get_dialogue_sound(self, dialogue_id, line_index, speaker=None):
        sound_key = f"{dialogue_id}_{line_index}"

        if sound_key in self.dialogue_sounds:
            return self.dialogue_sounds[sound_key]

        for ext in ['mp3', 'wav', 'ogg']:
            relative_path = os.path.join('dialogues', dialogue_id, f'{line_index}.{ext}')
            sound = self._load_sound_file(relative_path)
            if sound is not None:
                sound.set_volume(self.volume_factors['dialogue_line'] * self.sfx_volume)
                self.dialogue_sounds[sound_key] = sound
                return sound

        return None

    # ------------------------------------------------------------------
    # Frame update
    # ------------------------------------------------------------------

    def update(self):
        if self.music_fade_active:
            now = pg.time.get_ticks()
            elapsed = now - self.music_fade_start_time
            progress = min(1.0, elapsed / self.music_fade_duration_ms)

            new_volume = (
                self.music_fade_start_volume +
                (self.music_fade_target_volume - self.music_fade_start_volume) * progress
            )
            pg.mixer.music.set_volume(new_volume)

            if progress >= 1.0:
                self.music_fade_active = False
                pg.mixer.music.set_volume(self.music_fade_target_volume)