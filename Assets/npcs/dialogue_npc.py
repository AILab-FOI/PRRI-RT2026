"""
Dialogue NPC class for the game.
"""

import pygame as pg
from Assets.settings import *
from Assets.npcs.base_npc import StaticNPC
from Assets.scripts.Util.font_manager import load_custom_font


class DialogueNPC(StaticNPC):
    """NPC that can be interacted with for dialogue"""
    def __init__(self, game, path=None, pos=(10.5, 5.5),
                 scale=0.6, shift=0.38, animation_time=180, dialogue_id=None, interaction_radius=1.5):
        if path is None:
            path = 'resources/sprites/npc/dialogue_npc/0.png'

        super().__init__(game, path, pos, scale, shift, animation_time)

        self.is_friendly = True
        self.dialogue_id = dialogue_id or "marvin_intro"
        self.interaction_radius = interaction_radius
        self.can_interact = True
        self.interaction_cooldown = 1000
        self.last_interaction_time = 0
        self.interaction_indicator_visible = False
        self.indicator_font = load_custom_font(16)

    def update(self):
        super().update()
        if hasattr(self.game, 'dialogue_manager') and self.game.dialogue_manager.dialogue_active:
            self.interaction_indicator_visible = False

    def start_dialogue(self):
        if hasattr(self.game, 'dialogue_manager') and not self.game.dialogue_manager.dialogue_active:
            self.last_interaction_time = pg.time.get_ticks()
            self.game.dialogue_manager.start_dialogue(self.dialogue_id, self)

    def draw_interaction_indicator(self):
        if hasattr(self.game, 'intro_sequence') and self.game.intro_sequence.active:
            return

        if not self.interaction_indicator_visible:
            return

        screen_x = self.screen_x
        screen_y = HALF_HEIGHT - 100
        margin_y = int(HEIGHT * UI_MARGIN_PERCENT_Y)

        text = self.indicator_font.render("Press E to talk", True, (255, 255, 255))
        text_rect = text.get_rect(center=(screen_x, screen_y - 25 - margin_y))

        bg_rect = text_rect.inflate(20, 10)
        bg_surface = pg.Surface((bg_rect.width, bg_rect.height), pg.SRCALPHA)
        bg_surface.fill((0, 0, 0, 180))

        self.game.screen.blit(bg_surface, bg_rect)
        self.game.screen.blit(text, text_rect)

    def run_logic(self):
        """Logic for dialogue NPCs - check distance to player and show interaction indicator"""
        super().run_logic()

        player_dist = self.get_distance_to_player()
        self.interaction_indicator_visible = player_dist <= self.interaction_radius

        if self.interaction_indicator_visible and hasattr(self.game, 'dialogue_manager') and not self.game.dialogue_manager.dialogue_active:
            self.draw_interaction_indicator()


def create_dialogue_npcs(game, npc_data):
    """Create dialogue NPCs from level data"""
    npcs = []
    for data in npc_data:
        npc = DialogueNPC(
            game=game,
            pos=data.get('pos', (10.5, 5.5)),
            dialogue_id=data.get('dialogue_id', 'marvin_intro'),
            path=data.get('path', 'resources/sprites/npc/dialogue_npc/0.png'),
            scale=data.get('scale', 0.6),
            shift=data.get('shift', 0.38),
            animation_time=data.get('animation_time', 180),
            interaction_radius=data.get('interaction_radius', 1)
        )
        npcs.append(npc)
        game.object_handler.add_npc(npc)
    return npcs
