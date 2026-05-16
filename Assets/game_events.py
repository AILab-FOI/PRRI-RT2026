import pygame as pg
import sys

class GameEvents:
    def __init__(self, game):
        self.game = game

    def process_events(self):
        """Process all game events"""
        self.game.global_trigger = False
        for event in pg.event.get():
            if hasattr(self.game.level_transition, 'transition_state') and \
               self.game.level_transition.transition_state is not None:
                if self.game.level_transition.handle_event(event):
                    continue

            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE and not self.game.interaction.input_active:
                return True

            elif event.type == self.game.global_event:
                self.game.global_trigger = True

            elif event.type == pg.USEREVENT:
                self.game.intro_sequence.start_music_with_fade()


            if event.type == pg.KEYDOWN:
                self.handle_keydown(event.key)

            if event.type == pg.MOUSEWHEEL:
                self.handle_weapon_switch(event)
            
            #elif event.type == pg.KEYDOWN and event.key == pg.K_e:
            #    self._handle_e_key_press()

            elif event.type == pg.USEREVENT + 10:
                if hasattr(self.game, '_pending_intro_dialogue'):
                    self.game.dialogue_manager.start_auto_dialogue(
                        self.game._pending_intro_dialogue
                    )
                    del self.game._pending_intro_dialogue

            self.game.player.single_fire_event(event)
            self.game.interaction.handle_key_event(event)

            

        return False

    def _handle_e_key_press(self):
        """Handle E key press for dialogue and interaction"""
        if self.game.dialogue_manager.dialogue_active:
            self.game.dialogue_manager.handle_key_press()
        else:
            for npc in self.game.object_handler.npc_list:
                if hasattr(npc, 'is_friendly') and npc.is_friendly and hasattr(npc, 'interaction_indicator_visible'):
                    if npc.interaction_indicator_visible:
                        npc.start_dialogue()
                        break
    
    def handle_keydown(self,key):
         match key:
            case pg.K_TAB:
               if self.game.dialogue_manager.dialogue_active:
                  self.game.dialogue_manager.end_dialogue()
            case pg.K_r:
                self.game.player.reload_weapon()
            case pg.K_e:
                self._handle_e_key_press()
            case pg.K_q:
                self.game.player.try_heal()
            case pg.K_1:
                self.game.player.equip_weapon_by_index(0)
            case pg.K_2:
                self.game.player.equip_weapon_by_index(1)
            case pg.K_3:
                self.game.player.equip_weapon_by_index(2)
            case pg.K_4:
                self.game.player.equip_weapon_by_index(3)
        
            case _:
                pass
    
    def handle_weapon_switch(self, event):
        if event.y > 0:
            self.game.player.prev_weapon()   # scroll up
        elif event.y < 0:
            self.game.player.next_weapon()   # scroll down

