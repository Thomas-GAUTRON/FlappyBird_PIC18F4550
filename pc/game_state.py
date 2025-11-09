# game_state.py
"""
Gestion de l'état du jeu et des scores
"""

import time
from constants import (
    MODES, DEFAULT_MODE, BESTSCORE_FILE,
    PIPE_GAP_BASE, PIPE_SPEED_BASE, PIPE_SPAWN_EVERY_MS
)


class GameState:
    "Classe gérant l'état du jeu"
    
    def __init__(self):
        # État général
        self.state_name = "MENU"  # MENU | PLAYING | GAME_OVER
        self.menu_animation_offset = 0  #animations du menu
        self.selected_idx = MODES.index(DEFAULT_MODE)
        self.selected_mode = DEFAULT_MODE
        
        # Overlay system
        self.overlay_active = False
        self.overlay_type = None  # "INFO" | None
        self.previous_state = None
        
        # Interface
        self.blink_on = True
        
        # Gameplay
        self.reset_gameplay_vars()
        
        # Scores
        self.score = 0
        # best par mode (hors "Quit")
        self.best_scores = {m: 0 for m in MODES if m != "Quit"}
        # raccourci pour le HUD actuel
        self.best_score = 0
        self._sync_current_mode_best()
        self.just_new_best = False


        # Replay
        self.replay_recording = []  # Liste des frames enregistrées
        self.replay_mode = False
        self.replay_index = 0
        self.replay_speed = 2.0  # Vitesse x2

        # Dans reset_gameplay_vars():
        if not self.replay_mode:  # Ne pas effacer si on est en replay
            self.replay_recording = []
        self.replay_index = 0
    
    def reset_gameplay_vars(self):
        "Réinitialise les variables de gameplay"
        self.last_tick = time.time()
        self.bird_y = 270
        self.vy = 0.0
        
        self.last_gap_center = None
        self.pipes = []
        self.pipe_imgs = []
        self.last_pipe_spawn = time.time()
        
        self.score = 0
        
        # Paramètres dynamiques
        self.pipe_gap = PIPE_GAP_BASE
        self.pipe_speed = PIPE_SPEED_BASE
        self.spawn_every_ms = PIPE_SPAWN_EVERY_MS

    def _sync_current_mode_best(self):
        "Met à jour self.best_score depuis le mode sélectionné."
        if self.selected_mode in self.best_scores:
            self.best_score = self.best_scores[self.selected_mode]
        else:
            self.best_score = 0
    
    def set_state(self, new_state: str):
        if new_state == self.state_name:
            return False
        self.state_name = new_state
        return True
    
    def set_mode(self, mode_name: str):
        if mode_name in MODES:
            self.selected_mode = mode_name
            self.selected_idx = MODES.index(mode_name)
            self._sync_current_mode_best()  
            return True
        return False
    
    def show_info(self):
        "Affiche l'overlay d'information"
        self.previous_state = self.state_name
        self.overlay_active = True
        self.overlay_type = "INFO"
    
    def hide_info(self):
        "Cache l'overlay d'information"
        self.overlay_active = False
        self.overlay_type = None
        # previous_state reste intact pour le prochain affichage
    
    def increment_score(self):
        "Incrémente le score + met à jour le best en direct"
        self.score += 1
        self.just_new_best = False
        cur = self.best_scores.get(self.selected_mode, 0)
        if self.score > cur:
            self.best_scores[self.selected_mode] = self.score
            self.best_score = self.score
            self.just_new_best = True

