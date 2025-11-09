# pipes_manager.py
"""
Gestion des tuyaux (spawn, déplacement, suppression)
"""

import random
import time
from PIL import ImageTk
from constants import (
    WIDTH, HEIGHT, PIPE_WIDTH, PIPE_GAP_BASE, PIPE_GAP_MIN,
    PIPE_GAP_JITTER, PIPE_CENTER_MIN_FRAC, PIPE_CENTER_MAX_FRAC,
    PIPE_CENTER_DELTA_MINF, PIPE_SPEED_MAX, BIRD_X
)


class PipesManager:
    "Classe gérant les tuyaux"
    
    def __init__(self, canvas, assets_manager, game_state):
        self.canvas = canvas
        self.assets = assets_manager
        self.state = game_state
    
    def calculate_dynamic_gap(self) -> int:
        "Calcule le gap dynamique en fonction du score"
        base = max(PIPE_GAP_MIN, self.state.pipe_gap - self.state.score * 2)
        jitter = random.randint(-PIPE_GAP_JITTER, PIPE_GAP_JITTER)
        return max(PIPE_GAP_MIN, base + jitter)
    
    def spawn_pipe_pair(self, initial=False):
        "Crée une paire de tuyaux"
        w = self.canvas.winfo_width() or WIDTH
        h = self.canvas.winfo_height() or HEIGHT
        
        # Calcul du gap et du centre
        gap = self.calculate_dynamic_gap()
        
        min_c = int(h * PIPE_CENTER_MIN_FRAC)
        max_c = int(h * PIPE_CENTER_MAX_FRAC)
        min_delta = int(h * PIPE_CENTER_DELTA_MINF)
        
        if self.state.last_gap_center is None:
            gap_center = random.randint(min_c, max_c)
        else:
            if random.random() < 0.5:
                gap_center = random.randint(
                    min_c, max(self.state.last_gap_center - min_delta, min_c)
                )
            else:
                gap_center = random.randint(
                    min(self.state.last_gap_center + min_delta, max_c), max_c
                )
            
            if abs(gap_center - self.state.last_gap_center) < min_delta:
                for _ in range(8):
                    candidate = random.randint(min_c, max_c)
                    if abs(candidate - self.state.last_gap_center) >= min_delta:
                        gap_center = candidate
                        break
        
        self.state.last_gap_center = gap_center
        
        top_h = max(40, gap_center - gap // 2)
        bot_y = gap_center + gap // 2
        
        # Position X
        x = (w + PIPE_WIDTH) if not initial else (w + 30)
        
        # Création des rectangles (hitboxes)
        top_rect = self.canvas.create_rectangle(
            x, 0, x + PIPE_WIDTH, top_h, fill="black", tags=("pipe",)
        )
        bot_rect = self.canvas.create_rectangle(
            x, bot_y, x + PIPE_WIDTH, h, fill="black", tags=("pipe",)
        )
        
        # Création des sprites a placer sur les rectangles
        pil_top, pil_bot = self.assets.get_pipe_textures(self.state.selected_mode)
        
        top_img_id = bot_img_id = None
        top_tk = bot_tk = None
        
        if pil_top is not None:
            top_tk = ImageTk.PhotoImage(pil_top)
            top_img_id = self.canvas.create_image(
                x, top_h, image=top_tk, anchor="sw", tags=("pipe_img",)
            )
        
        if pil_bot is not None:
            bot_tk = ImageTk.PhotoImage(pil_bot)
            bot_img_id = self.canvas.create_image(
                x, bot_y, image=bot_tk, anchor="nw", tags=("pipe_img",)
            )
        
        # Enregistrement
        self.state.pipes.append((top_rect, bot_rect, False))
        self.state.pipe_imgs.append((top_img_id, bot_img_id, top_tk, bot_tk))
    
    def move_pipes(self):
        "Déplace tous les tuyaux et gère le scoring"
        return_val = 0
        remove_indices = []
        dx = -self.state.pipe_speed
        
        for i, (top, bot, passed) in enumerate(self.state.pipes):
            # Déplacer les rectangles
            self.canvas.move(top, dx, 0)
            self.canvas.move(bot, dx, 0)
            
            # Déplacer les images
            if i < len(self.state.pipe_imgs):
                top_img_id, bot_img_id, _, _ = self.state.pipe_imgs[i]
                if top_img_id:
                    self.canvas.move(top_img_id, dx, 0)
                if bot_img_id:
                    self.canvas.move(bot_img_id, dx, 0)
            
            # Coordonnées du tuyau
            coords = self.canvas.coords(top)
            if not coords or len(coords) < 4:  # PROTECTION CONTRE LES ERREURS
                remove_indices.append(i)
                continue
                
            x1, y1, x2, y2 = coords
            
            # Suppression si hors écran
            if x2 < 0:
                remove_indices.append(i)
                continue
            
            # Comptage du score
            if not passed and x2 < BIRD_X:
                self.state.pipes[i] = (top, bot, True)
                self.state.increment_score()
                self.state.pipe_speed = min(
                    PIPE_SPEED_MAX, self.state.pipe_speed + 0.05
                )
                return_val = 1
        
        # Suppression des tuyaux hors écran
        for idx in reversed(remove_indices):
            if idx < len(self.state.pipes):
                t, b, _ = self.state.pipes.pop(idx)
                self.canvas.delete(t)
                self.canvas.delete(b)
                
                if idx < len(self.state.pipe_imgs):
                    top_img_id, bot_img_id, _, _ = self.state.pipe_imgs.pop(idx)
                    if top_img_id:
                        self.canvas.delete(top_img_id)
                    if bot_img_id:
                        self.canvas.delete(bot_img_id)

        return return_val

    def should_spawn_new_pipe(self) -> bool:
        "Vérifie s'il faut spawner un nouveau tuyau"
        elapsed_ms = (time.time() - self.state.last_pipe_spawn) * 1000.0
        return elapsed_ms >= self.state.spawn_every_ms
    
    def mark_pipe_spawn(self):
        "Marque qu'un tuyau vient d'être spawné"
        self.state.last_pipe_spawn = time.time()