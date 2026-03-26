import pygame as pg
from Assets.settings import *
import json
import os
from Assets.scripts.Util.font_manager import load_custom_font, resource_path


class DialogueManager:
    def __init__(self, game):
        self.game = game
        self.dialogues = {}
        self.current_dialogue = None
        self.current_npc = None
        self.current_line_index = 0
        self.dialogue_active = False
        self.last_key_press_time = 0
        self.current_sound = None
        self.sound_playing = False

        self.font = load_custom_font(20)
        self.title_font = load_custom_font(24)
        self.speaker_font = load_custom_font(22)
        self.dialogue_box_height = 200
        self.dialogue_box_padding = 20
        self.line_spacing = 30

        self.speaker_colors = {
            'Marvin': (100, 100, 255),
            'Arthur': (255, 180, 50),
            'Officer': (50, 230, 50)
        }
        self.default_speaker_color = (200, 200, 200)

        self.load_dialogues()

    def load_dialogues(self):
        dialogue_dir = resource_path('resources/dialogues')
        try:
            for filename in os.listdir(dialogue_dir):
                if filename.endswith('.json'):
                    dialogue_id = filename[:-5]
                    file_path = os.path.join(dialogue_dir, filename)
                    try:
                        with open(file_path, 'r') as f:
                            self.dialogues[dialogue_id] = json.load(f)
                    except Exception:
                        pass
        except Exception:
            pass

    def start_dialogue(self, dialogue_id, npc):
        if dialogue_id in self.dialogues:
            self.game.player.dialogue_mode = True
            pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
            pg.mouse.get_rel()

            self.current_dialogue = self.dialogues[dialogue_id]
            self.current_npc = npc
            self.current_line_index = 0
            self.dialogue_active = True

            self.game.sound.duck_music()
            self.play_dialogue_sound()

            return True
        else:
            return False

    def play_dialogue_sound(self):
        if self.current_sound:
            self.current_sound.stop()

        dialogue_id = self.get_current_dialogue_id()

        current_speaker = None
        if "speakers" in self.current_dialogue and self.current_line_index < len(self.current_dialogue["speakers"]):
            current_speaker = self.current_dialogue["speakers"][self.current_line_index]

        self.current_sound = self.game.sound.get_dialogue_sound(dialogue_id, self.current_line_index, current_speaker)

        if self.current_sound:
            self.current_sound.play()
            self.sound_playing = True
        else:
            self.sound_playing = False

    def get_current_dialogue_id(self):
        for dialogue_id, dialogue in self.dialogues.items():
            if dialogue == self.current_dialogue:
                return dialogue_id
        return "unknown"

    def next_line(self):
        if not self.dialogue_active:
            return

        self.current_line_index += 1
        if self.current_line_index >= len(self.current_dialogue["lines"]):
            self.end_dialogue()
            return True
        else:
            self.play_dialogue_sound()
        return False

    def end_dialogue(self):
        self.dialogue_active = False
        self.current_dialogue = None
        self.current_npc = None
        self.current_line_index = 0

        if self.current_sound and self.sound_playing:
            self.current_sound.stop()
            self.sound_playing = False
            self.current_sound = None

        self.game.sound.unduck_music()

        pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
        pg.mouse.get_rel()
        self.game.player.dialogue_mode = False

    def handle_key_press(self):
        if not self.dialogue_active:
            return

        current_time = pg.time.get_ticks()
        if current_time - self.last_key_press_time > 300:
            self.last_key_press_time = current_time
            if self.current_line_index == len(self.current_dialogue["lines"]) - 1:
                self.end_dialogue()
            else:
                self.next_line()

    def update(self):
        if self.dialogue_active and self.sound_playing and self.current_sound:
            if not pg.mixer.get_busy():
                self.sound_playing = False

    def draw(self):
        if (hasattr(self.game, 'intro_sequence') and self.game.intro_sequence.active or
            not self.dialogue_active or not self.current_dialogue):
            return

        screen = self.game.screen
        margin_x = int(WIDTH * UI_MARGIN_PERCENT_X)
        margin_y = int(HEIGHT * UI_MARGIN_PERCENT_Y)

        box_width = WIDTH - (margin_x * 4)
        box_height = self.dialogue_box_height
        box_x = (WIDTH - box_width) // 2
        box_y = HEIGHT - box_height - margin_y - 30

        dialogue_surface = pg.Surface((box_width, box_height), pg.SRCALPHA)
        dialogue_surface.fill((0, 0, 0, 200))
        screen.blit(dialogue_surface, (box_x, box_y))
        pg.draw.rect(screen, (255, 255, 255), (box_x, box_y, box_width, box_height), 2)

        current_speaker = None
        speaker_color = self.default_speaker_color

        if "speakers" in self.current_dialogue and self.current_line_index < len(self.current_dialogue["speakers"]):
            current_speaker = self.current_dialogue["speakers"][self.current_line_index]
            speaker_color = self.speaker_colors.get(current_speaker, self.default_speaker_color)

        if current_speaker:
            speaker_text = self.speaker_font.render(current_speaker, True, (0, 0, 0))
            speaker_bg_width = speaker_text.get_width() + 30
            speaker_bg_height = speaker_text.get_height() + 12
            speaker_bg_x = box_x + self.dialogue_box_padding
            speaker_bg_y = box_y - speaker_bg_height + 2

            speaker_bg = pg.Surface((speaker_bg_width, speaker_bg_height))
            speaker_bg.fill(speaker_color)

            pg.draw.rect(screen, (0, 0, 0), (speaker_bg_x-2, speaker_bg_y-2, speaker_bg_width+4, speaker_bg_height+4))
            screen.blit(speaker_bg, (speaker_bg_x, speaker_bg_y))

            text_x = speaker_bg_x + (speaker_bg_width - speaker_text.get_width()) // 2
            text_y = speaker_bg_y + (speaker_bg_height - speaker_text.get_height()) // 2
            screen.blit(speaker_text, (text_x, text_y))

        if self.current_line_index < len(self.current_dialogue["lines"]):
            line = self.current_dialogue["lines"][self.current_line_index]
            max_width = box_width - 2 * self.dialogue_box_padding

            words = line.split(' ')
            lines = []
            current_line = ""

            for word in words:
                test_line = current_line + word + " "
                if self.font.size(test_line)[0] > max_width:
                    lines.append(current_line)
                    current_line = word + " "
                else:
                    current_line = test_line

            if current_line:
                lines.append(current_line)

            for i, line in enumerate(lines):
                text_surface = self.font.render(line, True, (255, 255, 255))
                y_pos = box_y + self.dialogue_box_padding + 40 + i * self.line_spacing
                screen.blit(text_surface, (box_x + self.dialogue_box_padding, y_pos))

        is_last_line = self.current_line_index == len(self.current_dialogue["lines"]) - 1
        prompt_text = self.font.render(
            "Press E to exit dialogue..." if is_last_line else "Press E to continue...",
            True, (200, 200, 200)
        )
        prompt_x = box_x + box_width - prompt_text.get_width() - self.dialogue_box_padding
        prompt_y = box_y + box_height - prompt_text.get_height() - self.dialogue_box_padding
        screen.blit(prompt_text, (prompt_x, prompt_y))
