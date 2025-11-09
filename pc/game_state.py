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
        self.best_score = self.load_best_score()

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
    
    def set_state(self, new_state: str):
        "Change l'état du jeu"
        if new_state == self.state_name:
            return False
        
        # Mise à jour du meilleur score
        if self.state_name == "PLAYING" and new_state == "GAME_OVER":
            if self.score > self.best_score:
                self.best_score = self.score
                self.save_best_score()
        
        self.state_name = new_state
        return True
    
    def set_mode(self, mode_name: str):
        "Change le mode de jeu"
        if mode_name in MODES:
            self.selected_mode = mode_name
            self.selected_idx = MODES.index(mode_name)
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
    
    def load_best_score(self):
        "Charge le meilleur score depuis le fichier"
        try:
            with open(BESTSCORE_FILE, "r", encoding="utf-8") as f:
                return int(f.read().strip())
        except Exception:
            return 0
    
    def save_best_score(self):
        "Sauvegarde le meilleur score dans le fichier"
        try:
            with open(BESTSCORE_FILE, "w", encoding="utf-8") as f:
                f.write(str(self.best_score))
        except Exception:
            pass
    
    def increment_score(self):
        "Incrémente le score"
        self.score += 1
