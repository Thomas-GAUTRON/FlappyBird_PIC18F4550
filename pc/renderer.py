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
    GAMEOVER_HIGHLIGHT_COLOR, MENU_ANIMATION_SPEED,
    INFO_CONTROLS, INFO_PANEL_BG, INFO_PANEL_BORDER,
    INFO_TITLE_FONT, INFO_CONTROL_FONT, INFO_KEY_LPT_COLOR, INFO_KEY_PIC_COLOR,
    INFO_DESC_COLOR, INFO_CLOSE_FONT
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
        
        # Instructions "Press 🟡 to start"
        hint_y = top_y + len(MODES) * gap_y - 50
        
        self.canvas.create_text(
            w // 2, hint_y + gap_y+30,
            text="Press 🟡 to start",
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



    def update_replay_hud(self):
        "Affiche le HUD pendant le replay"
        w = self.canvas.winfo_width() or WIDTH
        
        # Indicateur REPLAY en haut à gauche
        items_replay = self.canvas.find_withtag("replay_indicator")
        if items_replay:
            self.canvas.itemconfigure(
                items_replay[0],
                text="🎬 REPLAY x2",
                font=("VT323", 40, "bold"),
                fill="#FF4444"
            )
            self.canvas.coords(items_replay[0], 20, 30)
        else:
            self.canvas.create_text(
                20, 30,
                text="🎬 REPLAY",
                font=("VT323", 40, "bold"),
                fill="#FF4444",
                anchor="nw",
                tags=("replay_indicator", "hud")
            )
        
        # Score du replay au centre
        items_score = self.canvas.find_withtag("replay_score")
        if items_score:
            self.canvas.itemconfigure(
                items_score[0],
                text=f"Score : {self.state.score}",
                font=SCORE_FONT,
                fill=SCORE_COLOR
            )
            self.canvas.coords(items_score[0], w // 2, 50)
        else:
            self.canvas.create_text(
                w // 2, 50,
                text=f"Score : {self.state.score}",
                font=SCORE_FONT,
                fill=SCORE_COLOR,
                tags=("replay_score", "hud")
            )
        
        # Remonter tous les éléments HUD au-dessus
        self.canvas.tag_raise("hud")

    
    # ==================== Game Over ====================
    
    def render_game_over(self):
        "Écran Game Over – grand panneau, mode courant, liste des best centrée"
        w = self.canvas.winfo_width() or WIDTH
        h = self.canvas.winfo_height() or HEIGHT

        self.canvas.delete("all")

        # Fond assombri
        self.canvas.create_rectangle(0, 0, w, h, fill=GAMEOVER_BG_COLOR, stipple="gray50", tags=("gameover_bg",))

        # === Panneau central plus grand ===
        panel_width  = 820
        panel_height = 620
        panel_x1 = w // 2 - panel_width  // 2
        panel_y1 = h // 2 - panel_height // 2 - 20
        panel_x2 = w // 2 + panel_width  // 2
        panel_y2 = h // 2 + panel_height // 2 - 20

        # Ombre
        self.canvas.create_rectangle(panel_x1+10, panel_y1+10, panel_x2+10, panel_y2+10,
        fill="#000000", outline="", tags=("panel_shadow",))
        # Panneau
        self.canvas.create_rectangle(panel_x1, panel_y1, panel_x2, panel_y2,
        fill="#1a1a1a", outline=GAMEOVER_TITLE_COLOR, width=3, tags=("panel",))

        # Coins déco
        for (cx, cy) in [(panel_x1, panel_y1), (panel_x2, panel_y1), (panel_x1, panel_y2), (panel_x2, panel_y2)]:
            self.canvas.create_rectangle(cx-12, cy-12, cx+12, cy+12, fill=GAMEOVER_TITLE_COLOR, outline="", tags=("corner",))

        # Oiseau crash
        dead_img = getattr(self.assets, "bird_crash_tk", None) or getattr(self.assets, "bird_tk", None)
        bird_y = panel_y1 + 90
        if dead_img:
            self.canvas.create_image(w // 2, bird_y, image=dead_img, anchor="center", tags=("dead_bird",))

        # Titre
        title_y = bird_y + 90
        self.canvas.create_text(w // 2 + 3, title_y + 3, text="GAME OVER", font=GAMEOVER_TITLE_FONT,
        fill="#000000", tags=("title_shadow",))
        self.canvas.create_text(w // 2, title_y, text="GAME OVER", font=GAMEOVER_TITLE_FONT,
        fill=GAMEOVER_TITLE_COLOR, tags=("title",))

        # Séparateur
        line_y = title_y + 55
        self.canvas.create_line(w // 2 - 300, line_y, w // 2 + 300, line_y,
        fill=GAMEOVER_HIGHLIGHT_COLOR, width=2, tags=("separator",))

        # === MODE COURANT puis SCORE ===
        info_y = line_y + 38
        self.canvas.create_text(w // 2, info_y, text=f"MODE : {self.state.selected_mode}",
        font=GAMEOVER_SUBTITLE_FONT, fill=GAMEOVER_TEXT_COLOR, tags=("mode_label",))

        score_y = info_y + 48
        self.canvas.create_text(w // 2, score_y, text="SCORE", font=GAMEOVER_SUBTITLE_FONT,
        fill=GAMEOVER_TEXT_COLOR, tags=("score_label",))
        self.canvas.create_text(w // 2, score_y + 46, text=str(self.state.score),
        font=GAMEOVER_SCORE_FONT, fill=GAMEOVER_HIGHLIGHT_COLOR, tags=("score_value",))

        # NEW BEST 
        best_block_y = score_y + 120
        is_new_best = self.state.score >= self.state.best_scores[self.state.selected_mode] and self.state.score > 0
        if is_new_best:
            self.canvas.create_text(w // 2, best_block_y - 34, text="★ NEW BEST! ★",
            font=(GAMEOVER_SUBTITLE_FONT[0], GAMEOVER_SUBTITLE_FONT[1], "bold"),
            fill=GAMEOVER_HIGHLIGHT_COLOR, tags=("new_best",))

        # === Best multiper-mode centré ===
        self.canvas.create_text(w // 2, best_block_y, text="- BEST SCORE -",
        font=GAMEOVER_SUBTITLE_FONT, fill=GAMEOVER_TEXT_COLOR, tags=("best_header",))

        list_start_y = best_block_y + 42
        line_gap = 36
        x_gap = 30  # espace autour de l’axe central

        modes_no_quit = [m for m in MODES if m != "Quit"]
        for i, m in enumerate(modes_no_quit):
            y = list_start_y + i * line_gap
            val = (getattr(self.state, "best_scores", {}) or {}).get(m, 0)

            # Libellé gauche (ancré à droite du centre)
            self.canvas.create_text(w // 2 - x_gap, y, text=m + " :", font=("VT323", 28),
            fill=GAMEOVER_TEXT_COLOR, anchor="e", tags=("best_list",))
            # Valeur à droite (ancrée à gauche du centre)
            self.canvas.create_text(w // 2 + x_gap, y, text=str(val), font=("VT323", 28, "bold"),
            fill=GAMEOVER_HIGHLIGHT_COLOR if m == self.state.selected_mode else "#AAAAAA",
            anchor="w", tags=("best_list",))

        # Instruction (sous le panneau)
        if self.state.blink_on:
            self.canvas.create_text(w // 2, panel_y2 + 60, text="Press 🟢 to return to menu",
            font=GAMEOVER_SUBTITLE_FONT, fill=GAMEOVER_TEXT_COLOR, tags=("instructions",))

    # ==================== Info Overlay ====================
    
    def render_info_overlay(self):
        "Affiche l'overlay d'information contextuel"
        w = self.canvas.winfo_width() or WIDTH
        h = self.canvas.winfo_height() or HEIGHT
        
        # Fond semi-transparent
        self.canvas.create_rectangle(
            0, 0, w, h,
            fill="black",
            stipple="gray50",
            tags=("info_overlay",)
        )
        
        # Récupération des contrôles selon le contexte
        previous = self.state.previous_state
        
        if previous == "PLAYING":
            mode = self.state.selected_mode
            info_data = INFO_CONTROLS["PLAYING"][mode]
        else:
            info_data = INFO_CONTROLS[previous]
        
        title = info_data["title"]
        controls = info_data["controls"]
        
        # Dimensions du panneau
        panel_width = 1000
        panel_height = 100 + len(controls) * 60 + 100  # Dynamique selon nb de contrôles
        panel_x1 = w // 2 - panel_width // 2
        panel_y1 = h // 2 - panel_height // 2
        panel_x2 = w // 2 + panel_width // 2
        panel_y2 = h // 2 + panel_height // 2
        
        # Ombre du panneau
        shadow_offset = 10
        self.canvas.create_rectangle(
            panel_x1 + shadow_offset, panel_y1 + shadow_offset,
            panel_x2 + shadow_offset, panel_y2 + shadow_offset,
            fill="#000000",
            outline="",
            tags=("info_overlay",)
        )
        
        # Panneau principal
        self.canvas.create_rectangle(
            panel_x1, panel_y1, panel_x2, panel_y2,
            fill=INFO_PANEL_BG,
            outline=INFO_PANEL_BORDER,
            width=4,
            tags=("info_overlay",)
        )
        
        # Titre
        title_y = panel_y1 + 60
        self.canvas.create_text(
            w // 2, title_y,
            text=title,
            font=INFO_TITLE_FONT,
            fill=INFO_KEY_LPT_COLOR,
            tags=("info_overlay",)
        )
        
        # Ligne de séparation
        line_y = title_y + 50
        self.canvas.create_line(
            panel_x1 + 50, line_y,
            panel_x2 - 50, line_y,
            fill=INFO_PANEL_BORDER,
            width=2,
            tags=("info_overlay",)
        )
        
        # Liste des contrôles
        controls_start_y = line_y + 50
        for i, (key_lpt, key_pic, description) in enumerate(controls):
            y = controls_start_y + i * 60
            
            # Touche PC (à gauche)
            self.canvas.create_text(
                w // 2 + 100, y,
                text=f"[{key_lpt}]",
                font=INFO_CONTROL_FONT,
                fill=INFO_KEY_LPT_COLOR,
                anchor="e",
                tags=("info_overlay",)
            )
            # Touche PIC(à gauche)
            self.canvas.create_text(
                w // 2 + 110, y,
                text=f"[{key_pic}]",
                font=INFO_CONTROL_FONT,
                fill=INFO_KEY_PIC_COLOR,
                anchor="w",
                tags=("info_overlay",)
            )        
            # Description (à droite)
            self.canvas.create_text(
                w // 2 - 450, y,
                text=description,
                font=INFO_CONTROL_FONT,
                fill=INFO_DESC_COLOR,
                anchor="w",
                tags=("info_overlay",)
            )
        
        # Message de fermeture (clignotant)
        close_y = panel_y2 - 40
        if self.state.blink_on:
            self.canvas.create_text(
                w // 2, close_y,
                text="Press 🔵 to close",
                font=INFO_CLOSE_FONT,
                fill=INFO_KEY_LPT_COLOR,
                tags=("info_overlay", "info_close"),
            )
        
        # S'assurer que l'overlay est au-dessus de tout
        self.canvas.tag_raise("info_overlay")
    
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
