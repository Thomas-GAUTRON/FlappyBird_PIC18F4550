# renderer.py
"""
Gestion du rendu graphique (menus, bird, HUD)
"""

import math
from constants import (
    WIDTH, HEIGHT, BIRD_X, BIRD_RADIUS, MODES,
    MENU_COLOR, TITLE_FONT, MENU_FONT, FOOTER_FONT,
    SCORE_FONT, SCORE_COLOR, BEST_FONT, BEST_COLOR,
    GAMEOVER_TITLE_FONT, GAMEOVER_SUBTITLE_FONT, GAMEOVER_SCORE_FONT,
    GAMEOVER_BG_COLOR, GAMEOVER_TITLE_COLOR, GAMEOVER_TEXT_COLOR,
    GAMEOVER_HIGHLIGHT_COLOR, MENU_ANIMATION_SPEED
)


class Renderer:
    "Classe gérant le rendu graphique"
    
    def __init__(self, canvas, assets_manager, game_state):
        self.canvas = canvas
        self.assets = assets_manager
        self.state = game_state
    
    # ==================== Backgrounds ====================
    
    def draw_menu_background(self):
        "Dessine le fond d'écran du menu"
        w = self.canvas.winfo_width() or WIDTH
        h = self.canvas.winfo_height() or HEIGHT
        
        bg_img = self.assets.get_background_image("menu", w, h)
        if bg_img:
            self.canvas.delete("menu_bg")
            self.canvas.create_image(
                0, 0, image=bg_img, anchor="nw", tags=("menu_bg",)
            )
            self.canvas.tag_lower("menu_bg")
    
    def draw_play_background(self):
        "Dessine le fond d'écran de jeu"
        w = self.canvas.winfo_width() or WIDTH
        h = self.canvas.winfo_height() or HEIGHT
        
        bg_img = self.assets.get_background_image("play", w, h)
        if bg_img:
            self.canvas.delete("play_bg")
            self.canvas.create_image(
                0, 0, image=bg_img, anchor="nw", tags=("play_bg",)
            )
            self.canvas.tag_lower("play_bg")
    
    # ==================== Menu ====================
    
    def draw_title(self, w, h):
        "Dessine le titre du jeu avec effet d'animation du menu"
        # Animation flottante (sinus)
        self.state.menu_animation_offset += MENU_ANIMATION_SPEED
        y_offset = math.sin(self.state.menu_animation_offset * 0.05) * 10
        
        title_y = int(h * 0.18) + y_offset
        
        # Ombre du titre
        self.canvas.create_text(
            w // 2 + 4, title_y + 4,
            text="FLARRY-BIRD",
            font=TITLE_FONT,
            fill="#000000",
            tags=("title_shadow",)
        )
        
        # Titre principal
        self.canvas.create_text(
            w // 2, title_y,
            text="FLARRY-BIRD",
            font=TITLE_FONT,
            fill=MENU_COLOR,
            tags=("title",)
        )
    
    def draw_footer(self, w, h):
        "Dessine le pied de page du menu"
        self.canvas.create_text(
            w // 2, h - 40,
            text="FLAPPY-BIRD PROJECT - PIOUPIOUTEAM",
            font=FOOTER_FONT,
            fill=MENU_COLOR
        )
    
    def render_menu(self):
        "Affiche le menu principal avec effets visuels"
        w = self.canvas.winfo_width() or WIDTH
        h = self.canvas.winfo_height() or HEIGHT
        
        top_y = int(h * 0.38)
        gap_y = 70
        
        # Nettoyage
        for i in range(len(MODES)):
            self.canvas.delete(f"menu_item_{i}")
            self.canvas.delete(f"menu_box_{i}")
        self.canvas.delete("menu_box_all")
        self.canvas.delete("press_start")
        self.canvas.delete("best_menu")
        self.canvas.delete("controls")
        
        # Affichage du meilleur score en haut à droite
        self.canvas.create_text(
            w - 20, 20,
            text=f"BEST: {self.state.best_score}",
            font=BEST_FONT,
            fill=MENU_COLOR,
            anchor="ne",
            tags=("best_menu",)
        )
        
        # Items de menu
        for i, name in enumerate(MODES):
            y = top_y + i * gap_y
            tag_text = f"menu_item_{i}"
            is_sel = (i == self.state.selected_idx)
            
            # Texte du mode
            style = (MENU_FONT[0], MENU_FONT[1], "bold") if is_sel else (MENU_FONT[0], MENU_FONT[1], "normal")
            color = MENU_COLOR if is_sel else "#CCCCCC"
            
    
            self.canvas.create_text(
                w // 2, y,
                text=f"{name}",
                font=style,
                fill=color,
                tags=tag_text
            )
        
        # Instructions "Press X to start"
        hint_y = top_y + len(MODES) * gap_y - 50
        
        self.canvas.create_text(
            w // 2, hint_y + gap_y+30,
            text="Press X to start",
            font=MENU_FONT,
            fill=MENU_COLOR,
            tags=("press_start",)
        )
        
        self.state.blink_on = True
        self.set_tag_visible("press_start", True)
    
    # ==================== Bird ====================
    
    def draw_bird(self):
        "Dessine l'oiseau"
        x = BIRD_X
        y = int(self.state.bird_y)
        r = BIRD_RADIUS
        
        # Nettoyage
        for t in ("bird_img", "bird_hit"):
            for it in self.canvas.find_withtag(t):
                self.canvas.delete(it)
        
        # Sprite (visuel)
        if self.assets.bird_tk:
            self.canvas.create_image(
                x, y, image=self.assets.bird_tk, anchor="center", tags=("bird_img",)
            )
        else:
            # Fallback si sprite absent
            self.canvas.create_oval(
                x - r, y - r, x + r, y + r, fill="black", tags=("bird_img",)
            )
        
        # Hitbox (cercle invisible)
        self.canvas.create_oval(
            x - r, y - r, x + r, y + r,
            outline="", fill="", width=0,
            tags=("bird_hit",)
        )
    
    # ==================== HUD ====================
    
    def update_score_hud(self):
        "Met à jour l'affichage du score"
        w = self.canvas.winfo_width() or WIDTH
        
        items = self.canvas.find_withtag("score_hud")
        if items:
            self.canvas.itemconfigure(
                items[0], 
                text=f"Score : {self.state.score}", 
                font=SCORE_FONT, 
                fill=SCORE_COLOR
            )
            self.canvas.coords(items[0], w // 2, 50)
        else:
            self.canvas.create_text(
                w // 2, 50,
                text=f"Score : {self.state.score}",
                font=SCORE_FONT,
                fill=SCORE_COLOR,
                tags=("score_hud",)
            )
        
        self.canvas.tag_raise("score_hud")
    
    def update_best_hud(self):
        "Met à jour l'affichage du meilleur score"
        w = self.canvas.winfo_width() or WIDTH
        
        items = self.canvas.find_withtag("best_hud")
        if items:
            self.canvas.itemconfigure(
                items[0], 
                text=f"Best : {self.state.best_score}", 
                font=BEST_FONT, 
                fill=BEST_COLOR
            )
            self.canvas.coords(items[0], w - 10, 18)
        else:
            self.canvas.create_text(
                w - 10, 18,
                text=f"Best : {self.state.best_score}",
                anchor="ne",
                font=BEST_FONT,
                fill=BEST_COLOR,
                tags=("best_hud",)
            )
        
        self.canvas.tag_raise("best_hud")
        self.canvas.tag_raise("score_hud")
    
    # ==================== Game Over ====================
    
    def render_game_over(self):
        "Affiche l'écran de game over amélioré avec animations"
        w = self.canvas.winfo_width() or WIDTH
        h = self.canvas.winfo_height() or HEIGHT
        
        self.canvas.delete("all")
        
        # Fond semi-transparent (obscurci)
        self.canvas.create_rectangle(
            0, 0, w, h,
            fill=GAMEOVER_BG_COLOR,
            stipple="gray50",
            tags=("gameover_bg",)
        )
        
        # Panneau central (plus haut pour l'image)
        panel_width = 600
        panel_height = 500  # augmenté pour inclure l'image
        panel_x1 = w // 2 - panel_width // 2
        panel_y1 = h // 2 - panel_height // 2 - 30  # monté un peu
        panel_x2 = w // 2 + panel_width // 2
        panel_y2 = h // 2 + panel_height // 2 - 30
        
        # Ombre du panneau
        shadow_offset = 8
        self.canvas.create_rectangle(
            panel_x1 + shadow_offset, panel_y1 + shadow_offset,
            panel_x2 + shadow_offset, panel_y2 + shadow_offset,
            fill="#000000",
            outline="",
            tags=("panel_shadow",)
        )
        
        # Panneau principal
        self.canvas.create_rectangle(
            panel_x1, panel_y1, panel_x2, panel_y2,
            fill="#1a1a1a",
            outline=GAMEOVER_TITLE_COLOR,
            width=3,
            tags=("panel",)
        )
        
        # Décoration coins (sur les coins du rectangle)
        corner_size = 12
        corners = [
            (panel_x1, panel_y1),     # haut-gauche
            (panel_x2, panel_y1),     # haut-droite
            (panel_x1, panel_y2),     # bas-gauche
            (panel_x2, panel_y2)      # bas-droite
        ]
        for cx, cy in corners:
            self.canvas.create_rectangle(
                cx - corner_size, cy - corner_size,
                cx + corner_size, cy + corner_size,
                fill=GAMEOVER_TITLE_COLOR,
                outline="",
                tags=("corner",)
            )
        
        # Image du bird crashé
        bird_y = panel_y1 + 100
        dead_img = getattr(self.assets, "bird_crash_tk", None) or getattr(self.assets, "bird_tk", None)
        if dead_img:
            self.canvas.create_image(
                w // 2, bird_y,
                image=dead_img,
                anchor="center",
                tags=("dead_bird",)
            )
        
        # Titre "GAME OVER" avec effet
        title_y = bird_y + 90
        
        # Ombre du titre
        self.canvas.create_text(
            w // 2 + 3, title_y + 3,
            text="GAME OVER",
            font=GAMEOVER_TITLE_FONT,
            fill="#000000",
            tags=("title_shadow",)
        )
        
        # Titre
        self.canvas.create_text(
            w // 2, title_y,
            text="GAME OVER",
            font=GAMEOVER_TITLE_FONT,
            fill=GAMEOVER_TITLE_COLOR,
            tags=("title",)
        )
        
        # Ligne de séparation
        line_y = title_y + 60
        self.canvas.create_line(
            w // 2 - 200, line_y,
            w // 2 + 200, line_y,
            fill=GAMEOVER_HIGHLIGHT_COLOR,
            width=2,
            tags=("separator",)
        )
        
        # Scores avec mise en forme
        score_y = line_y + 50
        
        # Score actuel
        self.canvas.create_text(
            w // 2, score_y,
            text="SCORE",
            font=GAMEOVER_SUBTITLE_FONT,
            fill=GAMEOVER_TEXT_COLOR,
            tags=("score_label",)
        )
        
        self.canvas.create_text(
            w // 2, score_y + 45,
            text=str(self.state.score),
            font=GAMEOVER_SCORE_FONT,
            fill=GAMEOVER_HIGHLIGHT_COLOR,
            tags=("score_value",)
        )
        
        # Meilleur score
        best_y = score_y + 110
        
        # Afficher "NEW BEST!" si c'est un record
        is_new_best = self.state.score >= self.state.best_score and self.state.score > 0
        
        if is_new_best:
            
            self.canvas.create_text(
                w // 2, best_y - 30,
                text="★ NEW BEST! ★",
                font=(GAMEOVER_SUBTITLE_FONT[0], GAMEOVER_SUBTITLE_FONT[1], "bold"),
                fill=GAMEOVER_HIGHLIGHT_COLOR,
                tags=("new_best",)
            )
            
            # Étoiles décoratives qui clignotent
            if int(self.state.menu_animation_offset / 10) % 2 == 0:
                for star_x in [w // 2 - 150, w // 2 + 150]:
                    self.canvas.create_text(
                        star_x, best_y - 30,
                        text="★",
                        font=("VT323", 40),
                        fill=GAMEOVER_HIGHLIGHT_COLOR,
                        tags=("star",)
                    )
        
        self.canvas.create_text(
            w // 2, best_y,
            text="BEST",
            font=GAMEOVER_SUBTITLE_FONT,
            fill=GAMEOVER_TEXT_COLOR,
            tags=("best_label",)
        )
        
        self.canvas.create_text(
            w // 2, best_y + 45,
            text=str(self.state.best_score),
            font=GAMEOVER_SCORE_FONT,
            fill="#AAAAAA",
            tags=("best_value",)
        )
        
        # Instructions avec clignotement (PLUS BAS)
        instructions_y = panel_y2 + 60  # En dessous du panneau
        
        if self.state.blink_on:
            self.canvas.create_text(
                w // 2, instructions_y,
                text="Press ENTER to return to menu",
                font=GAMEOVER_SUBTITLE_FONT,
                fill=GAMEOVER_TEXT_COLOR,
                tags=("instructions",)
            )
    
    def render_placeholder_mode(self):
        "Affiche un message pour les modes non développés"
        self.canvas.delete("all")
        
        w = self.canvas.winfo_width() or WIDTH
        h = self.canvas.winfo_height() or HEIGHT
        
        bg_img = self.assets.get_background_image("play", w, h)
        if bg_img:
            self.canvas.delete("play_bg")
            self.canvas.create_image(
                0, 0, image=bg_img, anchor="nw", tags=("play_bg",)
            )
            self.canvas.tag_lower("play_bg")
        
        # Texte principal
        self.canvas.create_text(
            w // 2, 200,
            text="EN COURS DE REALISATION",
            font=MENU_FONT,
            fill=MENU_COLOR,
            tags=("ph_title",)
        )
        # Texte qui clignotte -> on lui donne un tag
        self.canvas.create_text(
            w // 2, 300,
            text="Press ENTER → MENU",
            font=MENU_FONT,
            fill=MENU_COLOR,
            tags=("ph_enter",)
        )

        # Appliquer l'état de blink courant pour l'initialisation
        self.set_tag_visible("ph_enter", self.state.blink_on)

    
    # ==================== Utilitaires ====================
    
    def set_tag_visible(self, tag, visible: bool):
        "Rend un tag visible ou invisible"
        for item in self.canvas.find_withtag(tag):
            self.canvas.itemconfigure(item, state=("normal" if visible else "hidden"))
    
    def clear_playfield(self):
        "Nettoie le terrain de jeu"
        for tag in ("bird", "bird_img", "bird_hit", "pipe", "pipe_img", "hud", "score_hud", "best_hud"):
            for it in self.canvas.find_withtag(tag):
                self.canvas.delete(it)
        self.state.pipe_imgs.clear()
