# replay_manager.py
"""
Gestion du système de replay
"""

from constants import MAX_REPLAY_FRAMES, REPLAY_SPEED


class ReplayManager:
    "Gère l'enregistrement et la lecture des replays"
    
    def __init__(self):
        self.frames = []  # Liste des frames enregistrées
        self.current_index = 0
        self.is_recording = False
        self.is_playing = False
        self.replay_speed = REPLAY_SPEED
    
    def start_recording(self):
        "Démarre l'enregistrement d'un replay"
        self.frames = []
        self.is_recording = True
        self.is_playing = False
        print("[REPLAY] Enregistrement démarré")
    
    def stop_recording(self):
        "Arrête l'enregistrement"
        self.is_recording = False
        print(f"[REPLAY] Enregistrement arrêté - {len(self.frames)} frames")
    
    def record_frame(self, bird_y, vy, pipes_data, score, canvas):
        "Enregistre une frame de gameplay"
        if not self.is_recording:
            return
        
        # Limite mémoire
        if len(self.frames) >= MAX_REPLAY_FRAMES:
            return
        
        # Enregistrer l'état de la frame avec les positions des tuyaux
        frame = {
            'bird_y': bird_y,
            'vy': vy,
            'pipes': self._copy_pipes_data(pipes_data, canvas),
            'score': score
        }
        self.frames.append(frame)
    
    def _copy_pipes_data(self, pipes_data, canvas):
        "Copie les données des tuyaux avec leurs positions"
        pipes_copy = []
        for pipe_info in pipes_data:
            # pipe_info = (top_rect_id, bot_rect_id, passed)
            top_id = pipe_info[0]
            bot_id = pipe_info[1]
            passed = pipe_info[2] if len(pipe_info) > 2 else False
            
            # Récupérer les coordonnées des rectangles
            try:
                top_coords = canvas.coords(top_id)  # [x1, y1, x2, y2]
                bot_coords = canvas.coords(bot_id)
                
                if top_coords and bot_coords:
                    pipes_copy.append({
                        'x': top_coords[0],
                        'top_h': top_coords[3],  # hauteur du tuyau du haut
                        'bot_y': bot_coords[1],  # position Y du tuyau du bas
                        'width': top_coords[2] - top_coords[0],
                        'passed': passed
                    })
            except Exception as e:
                print(f"[REPLAY] Erreur lors de la copie des coords: {e}")
                continue
        
        return pipes_copy
    
    def start_playback(self):
        "Démarre la lecture d'un replay"
        if len(self.frames) == 0:
            print("[REPLAY] Aucun replay disponible")
            return False
        
        self.current_index = 0
        self.is_playing = True
        self.is_recording = False
        print(f"[REPLAY] Lecture démarrée - {len(self.frames)} frames")
        return True
    
    def stop_playback(self):
        "Arrête la lecture du replay"
        self.is_playing = False
        self.current_index = 0
        print("[REPLAY] Lecture arrêtée")
    
    def get_next_frame(self):
        "Récupère la prochaine frame du replay"
        if not self.is_playing or self.current_index >= len(self.frames):
            return None
        
        frame = self.frames[self.current_index]
        self.current_index += 1
        return frame
    
    def is_replay_finished(self):
        "Vérifie si le replay est terminé"""
        return self.is_playing and self.current_index >= len(self.frames)
    
    def has_replay(self):
        "Vérifie si un replay est disponible"
        return len(self.frames) > 0
    
    def clear_replay(self):
        "Efface le replay en mémoire"
        self.frames = []
        self.current_index = 0
        self.is_recording = False
        self.is_playing = False
        print("[REPLAY] Replay effacé")
    
    def get_progress(self):
        "Retourne le pourcentage de progression du replay"
        if len(self.frames) == 0:
            return 0
        return (self.current_index / len(self.frames)) * 100