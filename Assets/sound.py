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
    def load_sound(self, filename, volume_factor=1.0):
        try:
            sound_path = resource_path(os.path.join(self.path, filename))
            sound = pg.mixer.Sound(sound_path)
            sound.set_volume(volume_factor * self.sfx_volume)
            return sound
        except Exception:
            return None

    def __init__(self, game):
        self.game = game
        pg.mixer.init()
        self.path = 'resources/sound'

        self.music_volume = 0.0
        self.sfx_volume = 0.15

        self.normal_music_volume = 0.0
        self.ducking_music_volume = 0.03
        self.is_ducking = False

        self.volume_factors = {
            # Weapon sounds
            'pistolj': 0.7,
            'smg': 0.4,
            'plasmagun': 0.6,
            'weapon_pickup': 0.7,

            # Player sounds
            'igrac_damage': 0.7,
            'player_dash': 0.5,

            # Game state sounds
            'victory': 0.5,
            'defeat': 0.4,

            # Generic NPC sounds
            'npc_pain': 0.5,
            'npc_death': 0.9,
            'npc_attack': 0.5,

            # Enemy-specific sounds
            'napad_stakor': 0.6,
            'stakor_smrt': 0.9,

            'toster_attack': 0.5,
            'toster_death': 0.9,
            'toster_damage': 0.5,

            'parazit_attack': 0.6,
            'parazit_death': 0.9,
            'parazit_damage': 0.5,

            'jazavac_attack': 0.5,
            'jazavac_death': 0.9,
            'jazavac_damage': 0.5,

            'madrac_attack': 0.6,
            'madrac_death': 0.9,
            'madrac_damage': 0.5,

            'boss_attack': 0.7,
            'boss_death': 1.0,
            'boss_damage': 0.6,

            # Interaction sounds
            'terminal_beep': 0.7,
            'door_open': 0.7,

            # Powerup sounds
            'powerup_pickup': 0.7,
            'powerup_active': 0.7,
            'powerup_end': 0.6,

            # Menu sounds
            'menu_hover': 0.3,
            'menu_click': 0.4,

            # Dialogue sounds
            'dialogue_line': 0.4,

            #hodanje
            'footstep': 0.25,
            'heal': 0.7,
        }

        self.pistolj = self.load_sound('Pistolj.wav', self.volume_factors['pistolj'])
        self.smg = self.load_sound('Puska.wav', self.volume_factors['smg'])
        self.plasmagun = self.load_sound('plasmaGun.wav', self.volume_factors['plasmagun'])
        self.weapon_pickup = self.load_sound('podizanje_oruzja.wav', self.volume_factors['weapon_pickup'])

        self.igrac_damage = self.load_sound('Igrac_damage.wav', self.volume_factors['igrac_damage'])
        self.player_dash = self.load_sound('Dash.wav', self.volume_factors['player_dash'])

        self.npc_pain = self.load_sound('npc_pain.wav', self.volume_factors['npc_pain'])
        self.npc_death = self.load_sound('npc_death.wav', self.volume_factors['npc_death'])
        self.npc_attack = self.load_sound('npc_attack.wav', self.volume_factors['npc_attack'])

        self.napad_stakor = self.load_sound('stakor_napad.mp3', self.volume_factors['napad_stakor'])
        self.stakor_smrt = self.load_sound('stakor_smrt.mp3', self.volume_factors['stakor_smrt'])

        self.toster_attack = self.load_sound('toster_napad.wav', self.volume_factors['toster_attack'])
        self.toster_death = self.load_sound('toster_smrt.mp3', self.volume_factors['toster_death'])
        self.toster_damage = self.load_sound('toster_damage.wav', self.volume_factors['toster_damage'])

        self.parazit_attack = self.load_sound('parazit_napad.mp3', self.volume_factors['parazit_attack'])
        self.parazit_death = self.load_sound('parazit_smrt.wav', self.volume_factors['parazit_death'])
        self.parazit_damage = self.load_sound('parazit_damage.mp3', self.volume_factors['parazit_damage'])

        self.jazavac_attack = self.load_sound('jazavac_napad.wav', self.volume_factors['jazavac_attack'])
        self.jazavac_death = self.load_sound('jazavac_smrt.wav', self.volume_factors['jazavac_death'])
        self.jazavac_damage = self.load_sound('jazavac_damage.wav', self.volume_factors['jazavac_damage'])

        self.madrac_attack = self.load_sound('madrac_napad.wav', self.volume_factors['madrac_attack'])
        self.madrac_death = self.load_sound('madrac_smrt.wav', self.volume_factors['madrac_death'])
        self.madrac_damage = self.load_sound('madrac_damage.wav', self.volume_factors['madrac_damage'])

        self.boss_attack = self.load_sound('boss_napad.wav', self.volume_factors['boss_attack'])
        self.boss_death = self.load_sound('boss_smrt.wav', self.volume_factors['boss_death'])
        self.boss_damage = self.load_sound('boss_damage.wav', self.volume_factors['boss_damage'])

        self.terminal_beep = self.load_sound('terminal.wav', self.volume_factors['terminal_beep'])
        self.door_open = self.load_sound('vrata.wav', self.volume_factors['door_open'])

        self.powerup_pickup = self.load_sound('powerup_pickup.wav', self.volume_factors['powerup_pickup'])
        self.powerup_active = self.load_sound('powerup1_trajanje.wav', self.volume_factors['powerup_active'])
        self.powerup_end = self.load_sound('powerup_gasenje.wav', self.volume_factors['powerup_end'])

        self.menu_hover = self.load_sound('menu_hover.mp3', self.volume_factors['menu_hover'])
        self.menu_click = self.load_sound('menu_klik.wav', self.volume_factors['menu_click'])

        self.victory = self.load_sound('pobjeda.mp3', self.volume_factors['victory'])
        self.defeat = self.load_sound('poraz.mp3', self.volume_factors['defeat'])

        self.footstep=self.load_sound('walking_v2.mp3', self.volume_factors['footstep'])#hodanje
        self.heal=self.load_sound('healcan1.mp3', self.volume_factors['heal'])#heal item



        self.dialogue_sounds = {}

        self.background_music = {
            1: 'Pozadinska1.mp3',
            2: 'Pozadinska2.wav',
            3: 'Pozadinska3.mp3',
            4: 'Pozadinska4.wav',
            5: 'Pozadinska5.wav'
        }

        self.current_music_level = 1
        music_path = resource_path(os.path.join(self.path, self.background_music[1]))
        pg.mixer.music.load(music_path)
        pg.mixer.music.set_volume(self.music_volume)



    def get_dialogue_sound(self, dialogue_id, line_index, speaker=None):
        sound_key = f"{dialogue_id}_{line_index}"

        if sound_key in self.dialogue_sounds:
            return self.dialogue_sounds[sound_key]

        if (dialogue_id == "marvin_intro" or dialogue_id == "level2_puzzle" or dialogue_id == "marvin_ending") and speaker:
            try:
                speaker_count = 0

                import json
                import os
                dialogue_path = resource_path(os.path.join('resources', 'dialogues', f"{dialogue_id}.json"))
                with open(dialogue_path, 'r') as f:
                    dialogue_data = json.load(f)

                for i in range(line_index + 1):
                    if i < len(dialogue_data["speakers"]) and dialogue_data["speakers"][i] == speaker:
                        speaker_count += 1

                prefix = ""
                if dialogue_id == "marvin_intro":
                    prefix = "Intro_"
                elif dialogue_id == "level2_puzzle":
                    prefix = "Puzzle_"
                elif dialogue_id == "marvin_ending":
                    prefix = "Ending_"
                else:
                    return None

                if speaker == "Arthur":
                    sound_path = f"{prefix}Arthur{speaker_count}.mp3"
                elif speaker == "Marvin":
                    sound_path = f"{prefix}Marvin{speaker_count}.mp3"
                else:
                    return None

                sound = self.load_sound(sound_path, self.volume_factors['dialogue_line'])
                if sound:
                    self.dialogue_sounds[sound_key] = sound
                return sound
            except Exception:
                return None

        try:
            sound_path = f"dialogues/{dialogue_id}/{line_index}.wav"
            sound = self.load_sound(sound_path, self.volume_factors['dialogue_line'])
            if sound:
                self.dialogue_sounds[sound_key] = sound
            return sound
        except Exception:
            return None

    def update_sfx_volume(self):
        sounds = {
            'pistolj': self.pistolj,
            'smg': self.smg,
            'plasmagun': self.plasmagun,
            'weapon_pickup': self.weapon_pickup,
            'igrac_damage': self.igrac_damage,
            'player_dash': self.player_dash,
            'npc_pain': self.npc_pain,
            'npc_death': self.npc_death,
            'npc_attack': self.npc_attack,
            'napad_stakor': self.napad_stakor,
            'stakor_smrt': self.stakor_smrt,
            'toster_attack': self.toster_attack,
            'toster_death': self.toster_death,
            'toster_damage': self.toster_damage,
            'parazit_attack': self.parazit_attack,
            'parazit_death': self.parazit_death,
            'parazit_damage': self.parazit_damage,
            'jazavac_attack': self.jazavac_attack,
            'jazavac_death': self.jazavac_death,
            'jazavac_damage': self.jazavac_damage,
            'madrac_attack': self.madrac_attack,
            'madrac_death': self.madrac_death,
            'madrac_damage': self.madrac_damage,
            'boss_attack': self.boss_attack,
            'boss_death': self.boss_death,
            'boss_damage': self.boss_damage,
            'terminal_beep': self.terminal_beep,
            'door_open': self.door_open,
            'powerup_pickup': self.powerup_pickup,
            'powerup_active': self.powerup_active,
            'powerup_end': self.powerup_end,
            'menu_hover': self.menu_hover,
            'menu_click': self.menu_click,
            'victory': self.victory,
            'defeat': self.defeat,
            'footstep': self.footstep,
            'heal': self.heal
        }

        for sound_name, sound in sounds.items():
            sound.set_volume(self.volume_factors[sound_name] * self.sfx_volume)

        for sound_key, sound in self.dialogue_sounds.items():
            sound.set_volume(self.volume_factors['dialogue_line'] * self.sfx_volume)

    def update_music_volume(self):
        if self.is_ducking:
            pg.mixer.music.set_volume(self.ducking_music_volume)
        else:
            pg.mixer.music.set_volume(self.normal_music_volume)

    def duck_music(self):
        if not self.is_ducking:
            self.is_ducking = True
            pg.mixer.music.set_volume(self.ducking_music_volume)

    def unduck_music(self):
        if self.is_ducking:
            self.is_ducking = False
            pg.mixer.music.set_volume(self.normal_music_volume)

    def change_music_for_level(self, level):
        if level in self.background_music:
            change_music = level != self.current_music_level

            if not pg.mixer.music.get_busy():
                change_music = True

            if change_music:
                pg.mixer.music.stop()
                music_path = resource_path(os.path.join(self.path, self.background_music[level]))
                pg.mixer.music.load(music_path)

                if self.is_ducking:
                    pg.mixer.music.set_volume(self.ducking_music_volume)
                else:
                    pg.mixer.music.set_volume(self.normal_music_volume)

                pg.mixer.music.play(-1)
                self.current_music_level = level