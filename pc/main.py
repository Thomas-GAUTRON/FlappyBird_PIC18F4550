import tkinter as tk
import time
import random
import serial

BESTSCORE_FILE = "bestscore.txt"


# -------------------- Constantes --------------------
WIDTH, HEIGHT = 960, 540
FPS_MS   = 16
BLINK_MS = 500

MODES = ["Button", "Potentiometer", "Infrared", "Ultrasound"]
DEFAULT_MODE = "Button"

# Jeu (physique)
BIRD_X       = 220
BIRD_SIZE    = 26
GRAVITY      = 0.45
FLAP_IMPULSE = -8.0
MAX_VY       = 12.0

# Tuyaux (rectangles pour collisions/score)
PIPE_WIDTH          = 80
PIPE_GAP_BASE       = 210   # gap vertical de départ (un peu plus large)
PIPE_GAP_MIN        = 170   # gap minimum au fil du score
PIPE_SPEED_BASE     = 3.0   # vitesse de départ
PIPE_SPEED_MAX      = 5.0   # limite supérieure
PIPE_SPAWN_EVERY_MS = 2200  # espacement horizontal (un peu plus long)
PIPE_GAP_JITTER     = 20    # +/- variation instantanée du gap à chaque spawn

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FLAPIC-BIRD")

        # Configuration série
        self.serial_port = None
        self.serial_connected = False
        self._init_serial()

        # Fenêtre
        try:
            self.attributes("-fullscreen", True)
        except Exception:
            self.state("zoomed")
        self.resizable(True, True)

        # --- États & sélection ---
        self.state_name    = "MENU"   # MENU | PLAYING | GAME_OVER
        self.selected_idx  = MODES.index(DEFAULT_MODE)
        self.selected_mode = DEFAULT_MODE
        self.blink_on      = True

        # --- Canvas ---
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.render_screen())

        # --- Binds généraux ---
        self.bind_all("<Key-x>", lambda e: self._do_start())   # Start
        self.bind_all("<Return>", self._on_enter)               # Retour menu
        self.bind_all("<Key-m>", lambda e: self.destroy())      # Quitter
        self.bind_all("<F11>",    self._toggle_fullscreen)

        # Choix direct de mode
        self.bind_all("<Key-c>", lambda e: self._set_mode("Button"))
        self.bind_all("<Key-v>", lambda e: self._set_mode("Potentiometer"))
        self.bind_all("<Key-b>", lambda e: self._set_mode("Infrared"))
        self.bind_all("<Key-n>", lambda e: self._set_mode("Ultrasound"))

        # Input gameplay (uniquement Button)
        # self.bind_all("<space>", self._on_space)

        # --- Variables gameplay ---
        self.last_tick         = time.time()
        self.bird_y            = HEIGHT // 2
        self.vy                = 0.0
        self.bird_id           = None

        self.pipes             = []      # [(top_id, bot_id, passed_flag)]
        self.last_pipe_spawn   = time.time()
        self.score             = 0
        self.best_score = self._load_best()


        # paramètres dynamiques (évoluent avec le score)
        self.pipe_gap          = PIPE_GAP_BASE
        self.pipe_speed        = PIPE_SPEED_BASE
        self.spawn_every_ms    = PIPE_SPAWN_EVERY_MS



        # --- Boucles ---
        self.render_screen()
        self.after(FPS_MS, self.loop)
        self.after(BLINK_MS, self._blink)

    # ================== Série ==================
    def _init_serial(self):
        try:
            # Remplace 'COM3' par le port série de ton périphérique
            # et 9600 par le baudrate utilisé
            self.serial_port = serial.Serial('COM8', 38400, timeout=0.1)
            self.serial_connected = True
            print("Connexion série établie.")
            # Démarre la lecture en continu
            self.after(50, self._read_serial)
        except Exception as e:
            print(f"Erreur de connexion série: {e}")
            self.serial_connected = False

    def _read_serial(self):
        if not self.serial_connected or self.serial_port is None:
            return
        try:
            buffer = ""
            if self.serial_port and self.serial_port.in_waiting > 0:
                    print("data available")
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    text = data.decode('utf-8', errors='ignore')
                    buffer += text
                    
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        self._flap()
                        print(f"Reçu série: {line}")
            
        except Exception as e:
            print(f"Erreur de lecture série: {e}")
        finally:
            self.after(50, self._read_serial)  # Relance la lecture

    def _close_serial(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print("Connexion série fermée.")

    def destroy(self):
        self._close_serial()
        super().destroy()

    # ================== États ==================
    def _set_state(self, new_state: str):
        if new_state == self.state_name:
            return

        # si on passe de PLAYING -> GAME_OVER, on met à jour le best
        if self.state_name == "PLAYING" and new_state == "GAME_OVER":
            if self.score > getattr(self, "best_score", 0):
                self.best_score = self.score
                self._save_best()

        # en quittant PLAYING, on nettoie le terrain (évite le carré figé)
        if self.state_name == "PLAYING" and new_state in ("GAME_OVER", "MENU"):
            self._clear_playfield()

        self.state_name = new_state
        if new_state == "PLAYING":  
            self._reset_gameplay()
        self.render_screen()


    # Nettoyage ciblé du terrain (bird/pipes/HUD)
    def _clear_playfield(self):
        for tag in ("bird", "pipe", "hud"):
            for it in self.canvas.find_withtag(tag):
                self.canvas.delete(it)

    def _load_best(self):
        try:
            with open(BESTSCORE_FILE, "r", encoding="utf-8") as f:
                return int(f.read().strip())
        except Exception:
            return 0

    def _save_best(self):
        try:
            with open(BESTSCORE_FILE, "w", encoding="utf-8") as f:
                f.write(str(self.best_score))
        except Exception:
            pass

    # ================== Sélection menu ==================
    def _set_mode(self, mode_name: str):
        if self.state_name != "MENU":
            return
        if mode_name in MODES:
            self.selected_mode = mode_name
            self.selected_idx  = MODES.index(mode_name)
            self.render_menu()

    # ================== Actions ==================
    def _do_start(self):
        if self.state_name == "MENU":
            self._set_state("PLAYING")

    def _on_enter(self, _e=None):
        # Revenir au MENU depuis PLAYING ou GAME_OVER
        if self.state_name in ("PLAYING", "GAME_OVER"):
            self._set_state("MENU")

    def _toggle_fullscreen(self, _e=None):
        try:
            self.attributes("-fullscreen", not self.attributes("-fullscreen"))
        except Exception:
            pass

    # ================== Entrées gameplay ==================
    def _on_space(self, _e=None):
        # SPACE actif uniquement en PLAYING + Button
        if self.state_name == "PLAYING" and self.selected_mode == "Button":
            self._flap()

    # ================== Gameplay (Button) ==================
    def _reset_gameplay(self):
        # Reset temps/physique
        self.last_tick       = time.time()
        self.vy              = 0.0

        # Reset dessin & données
        self.canvas.delete("all")
        self.pipes.clear()
        self.score = 0
        self.best_score = self._load_best()


        # place l'oiseau au centre de la hauteur actuelle
        self.bird_y          = (self.canvas.winfo_height() or HEIGHT) // 2

        # reset dynamiques
        self.pipe_gap     = PIPE_GAP_BASE
        self.pipe_speed   = PIPE_SPEED_BASE
        self.spawn_every_ms = PIPE_SPAWN_EVERY_MS

        # focus pour que SPACE refonctionne après un run
        try:
            self.focus_force()
        except Exception:
            pass

        # --- Début rapide mais 2e tuyau bien espacé ---
        # 1) On spawn un premier tuyau proche
        self._spawn_pipe_pair(initial=True)
        # 2) Puis on repart sur l'intervalle complet (évite le 2e trop collé)
        self.last_pipe_spawn = time.time()

    def _flap(self):
        self.vy = FLAP_IMPULSE

    def _update_playing_button(self, dt):
        # Gravité + clamp
        self.vy = max(-MAX_VY, min(MAX_VY, self.vy + GRAVITY))
        self.bird_y += self.vy

        # Collisions plafond/sol -> GAME OVER
        h   = self.canvas.winfo_height() or HEIGHT
        top = BIRD_SIZE // 2
        bot = h - BIRD_SIZE // 2
        if self.bird_y <= top or self.bird_y >= bot:
            self._set_state("GAME_OVER")

    # ----- Tuyaux -----
    def _current_gap(self):
        # gap dynamique (diminue doucement avec le score), avec un petit jitter
        base = max(PIPE_GAP_MIN, self.pipe_gap - self.score * 2)
        jitter = random.randint(-PIPE_GAP_JITTER, PIPE_GAP_JITTER)
        return max(PIPE_GAP_MIN, base + jitter)

    def _spawn_pipe_pair(self, initial=False):
        """Crée une paire de tuyaux. initial=True les place plus près pour un début rapide."""
        w = self.canvas.winfo_width()  or WIDTH
        h = self.canvas.winfo_height() or HEIGHT

        gap = self._current_gap()
        gap_center = int(h * random.uniform(0.35, 0.65))
        top_h = max(40, gap_center - gap // 2)
        bot_y = gap_center + gap // 2

        # Si initial, on les met juste hors écran pour qu'ils arrivent vite
        x = (w + PIPE_WIDTH) if not initial else (w + 30)

        top = self.canvas.create_rectangle(x, 0, x + PIPE_WIDTH, top_h,
                                           fill="black", tags=("pipe",))
        bot = self.canvas.create_rectangle(x, bot_y, x + PIPE_WIDTH, h,
                                           fill="black", tags=("pipe",))
        self.pipes.append((top, bot, False))  # False = pas compté au score

    def _move_pipes(self):
        remove = []
        for i, (top, bot, passed) in enumerate(self.pipes):
            self.canvas.move(top, -self.pipe_speed, 0)
            self.canvas.move(bot, -self.pipe_speed, 0)
            x1, y1, x2, y2 = self.canvas.coords(top)
            if x2 < 0:
                remove.append(i)
            if not passed and x2 < BIRD_X:
                self.pipes[i] = (top, bot, True)
                self.score += 1
                # petite montée en difficulté
                self.pipe_speed = min(PIPE_SPEED_MAX, self.pipe_speed + 0.05)
        for idx in reversed(remove):
            t, b, _ = self.pipes[idx]
            self.canvas.delete(t); self.canvas.delete(b)
            self.pipes.pop(idx)

    def _collides_with_pipes(self):
        bx1 = BIRD_X - BIRD_SIZE//2
        by1 = int(self.bird_y) - BIRD_SIZE//2
        bx2 = BIRD_X + BIRD_SIZE//2
        by2 = int(self.bird_y) + BIRD_SIZE//2

        def overlap(a, b):
            ax1, ay1, ax2, ay2 = a
            bx1, by1, bx2, by2 = b
            return not (ax2 < bx1 or ax1 > bx2 or ay2 < by1 or ay1 > by2)

        for (top, bot, _) in self.pipes:
            if overlap((bx1, by1, bx2, by2), self.canvas.coords(top)) or \
               overlap((bx1, by1, bx2, by2), self.canvas.coords(bot)):
                return True
        return False

    # ================== Rendu ==================
    def render_screen(self):
        self.canvas.delete("hud")  # nettoie juste le HUD
        w = self.canvas.winfo_width()  or WIDTH
        h = self.canvas.winfo_height() or HEIGHT

        if self.state_name == "MENU":
            self.canvas.delete("all")
            self._draw_title(w, h)
            self.render_menu()
            self._draw_footer(w, h)

        elif self.state_name == "PLAYING":
            if self.selected_mode == "Button":
                # Bird + HUD (2 lignes)
                self._draw_bird()
                self.canvas.create_text(w - 10, 10, anchor="ne",
                                        text=f"Score: {self.score}",
                                        font=("Arial", 12),
                                        tags=("hud",))
                self.canvas.create_text(w - 10, 28, anchor="ne",
                                        text=f"Best:  {self.best_score}",
                                        font=("Arial", 12),
                                        tags=("hud",))
            else:
                self.canvas.delete("all")
                self.canvas.create_text(w//2, h//2 - 10,
                                        text=f"Mode {self.selected_mode} : en cours de réalisation",
                                        font=("Arial", 20, "bold"))
                self.canvas.create_text(w//2, h//2 + 30,
                                        text="Press ENTER → MENU",
                                        font=("Arial", 14))



        elif self.state_name == "GAME_OVER":
            self.canvas.delete("all")
            self.canvas.create_text(w//2, h//2 - 10, text="GAME OVER",
                                    font=("Arial", 32, "bold"))
            self.canvas.create_text(w//2, h//2 + 30, text="Press ENTER → MENU",
                                    font=("Arial", 14))
            self.canvas.create_text(w - 10, 10, anchor="ne",
                        text=f"Score: {self.score}   Best: {self.best_score}",
                        font=("Arial", 12), tags=("hud",))


    def _draw_title(self, w, h):
        self.canvas.create_text(w//2, int(h*0.18),
                                text="FLAPIC-BIRD",
                                font=("Arial", 36, "bold"))
        self.press_tag = "press_start"
        self.canvas.create_text(w//2, int(h*0.28),
                                text="Press X to start",
                                font=("Arial", 18),
                                tags=self.press_tag)

    def _draw_footer(self, w, h):
        self.canvas.create_text(w//2, h - 60,
            text="X=Start • C=Button • V=Pot • B=IR • N=Ultrasound • ENTER=Menu • M=Exit",
            font=("Arial", 12))
        self.canvas.create_text(w//2, h - 35,
            text="F11: Fullscreen",
            font=("Arial", 11))

    def render_menu(self):
        w = self.canvas.winfo_width()  or WIDTH
        h = self.canvas.winfo_height() or HEIGHT

        top_y = int(h*0.38)
        gap_y = 56
        pad_x = 18
        pad_y = 10

        # Nettoyage items de menu précédents
        for i in range(len(MODES)):
            self.canvas.delete(f"menu_item_{i}")
            self.canvas.delete(f"menu_box_{i}")

        # Items + encadrement du sélectionné
        for i, name in enumerate(MODES):
            y   = top_y + i*gap_y
            tag = f"menu_item_{i}"
            style = ("Arial", 20, "bold") if i == self.selected_idx else ("Arial", 20, "normal")
            text_id = self.canvas.create_text(w//2, y, text=name, font=style, tags=tag)
            if i == self.selected_idx:
                x1, y1, x2, y2 = self.canvas.bbox(text_id)
                x1 -= pad_x; x2 += pad_x; y1 -= pad_y; y2 += pad_y
                self.canvas.create_rectangle(x1, y1, x2, y2,
                                             outline="black", width=3,
                                             tags=f"menu_box_{i}")

        # Reset du blink
        self.blink_on = True
        self._set_tag_visible("press_start", True)

    def _draw_bird(self):
        # Carré représentant l’oiseau (tag "bird" pour redraw ciblé)
        x = BIRD_X
        y = int(self.bird_y)
        x1, y1 = x - BIRD_SIZE//2, y - BIRD_SIZE//2
        x2, y2 = x + BIRD_SIZE//2, y + BIRD_SIZE//2
        for it in self.canvas.find_withtag("bird"):
            self.canvas.delete(it)
        self.bird_id = self.canvas.create_rectangle(x1, y1, x2, y2,
                                                    fill="black", tags=("bird",))

    # ================== Utilitaires UI ==================
    def _set_tag_visible(self, tag, visible: bool):
        for item in self.canvas.find_withtag(tag):
            self.canvas.itemconfigure(item, state=("normal" if visible else "hidden"))

    # ================== Blink 1 Hz ==================
    def _blink(self):
        if self.state_name == "MENU":
            self.blink_on = not self.blink_on
            self._set_tag_visible("press_start", self.blink_on)
        self.after(BLINK_MS, self._blink)

    # ================== Boucle principale ==================
    def loop(self):
        now = time.time()
        dt  = now - self.last_tick
        self.last_tick = now

        if self.state_name == "PLAYING":
            if self.selected_mode == "Button":
                # Physique (peut déclencher GAME_OVER via sol/plafond)
                self._update_playing_button(dt)
                if self.state_name != "PLAYING":
                    # On vient de passer en GAME_OVER -> stop ce tick tout de suite
                    self.after(FPS_MS, self.loop)
                    return

                # Spawning périodique
                if (time.time() - self.last_pipe_spawn) * 1000.0 >= self.spawn_every_ms:
                    self._spawn_pipe_pair()
                    self.last_pipe_spawn = time.time()

                # Move + score + légère montée de vitesse
                self._move_pipes()

                # Collisions (tuyaux)
                if self._collides_with_pipes():
                    self._set_state("GAME_OVER")
                    self.after(FPS_MS, self.loop)
                    return

                # Redraw ciblé : bird + HUD (on garde les tuyaux)
                self._draw_bird()
                w = self.canvas.winfo_width() or WIDTH
                for it in self.canvas.find_withtag("hud"):
                    self.canvas.delete(it)
                self.canvas.create_text(w - 10, 10, anchor="ne",
                                        text=f"Score: {self.score}",
                                        font=("Arial", 12),
                                        tags=("hud",))
                self.canvas.create_text(w - 10, 28, anchor="ne",
                                        text=f"Best:  {self.best_score}",
                                        font=("Arial", 12),
                                        tags=("hud",))
                                
            else:
                # Placeholder modes non développés
                self.canvas.delete("all")
                w = self.canvas.winfo_width()  or WIDTH
                h = self.canvas.winfo_height() or HEIGHT
                self.canvas.create_text(w//2, h//2 - 10,
                                        text=f"Mode {self.selected_mode} : en cours de réalisation",
                                        font=("Arial", 20, "bold"))
                self.canvas.create_text(w//2, h//2 + 30,
                                        text="Press ENTER → MENU",
                                        font=("Arial", 14))

        self.after(FPS_MS, self.loop)

# -------------------- Main --------------------
if __name__ == "__main__":
    App().mainloop()
