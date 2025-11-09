# main.py
"""
Fichier principal de Flappy Bird
Point d'entrée de l'application
"""

import tkinter as tk
import time

from constants import (
    WIDTH, HEIGHT, FPS_MS, BLINK_MS, 
    BIRD_SPRITE, BIRD_CRASH_SPRITE, MODES, PIPE_WIDTH
)

from assets_manager import AssetsManager
from game_state import GameState
from physics import PhysicsEngine
from pipes_manager import PipesManager
from renderer import Renderer
from replay_manager import ReplayManager

import serial
import serial.tools.list_ports
saute = True


class FlappyBirdApp(tk.Tk):
    "Application principale Flappy Bird"
    
    def __init__(self):
        super().__init__()
        self.title("FLAPIC-BIRD")
        
        # Configuration de la fenêtre
        self._setup_window()
        
        # Canvas principal
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.render_screen())
        
        # Initialisation des composants
        self.assets = AssetsManager()
        self.state = GameState()
        self.physics = PhysicsEngine()
        self.pipes_manager = PipesManager(self.canvas, self.assets, self.state)
        self.renderer = Renderer(self.canvas, self.assets, self.state)
        
        # Initialisation de la série
        self.serial_port = None
        self.serial_connected = False
        self._init_serial()

        # Chargement des assets
        self._load_all_assets()
        
        # Binding des touches
        self._setup_key_bindings()
        
        # Démarrage des boucles
        self.render_screen()
        self.after(FPS_MS, self.game_loop)
        self.after(BLINK_MS, self.blink_loop)

        self.replay = ReplayManager()

    
    # ================== Série ==================
    def _init_serial(self):
        try:
            self.serial_port = serial.Serial('COM5' , 38400, timeout=0.1)
            self.serial_connected = True
            print("Connexion série établie.")
            # Démarre la lecture en continu
            command = "a"
            self.serial_port.write(command.encode("utf-8")) # envoi initial pour test
            self.after(50, self._read_serial)   
        except Exception as e:
            print(f"Erreur de connexion série: {e}")
            self.serial_connected = False

    def _read_serial(self):
        global saute
        if not self.serial_connected or self.serial_port is None:
            return
        try:
            buffer = ""
            if self.serial_port and self.serial_port.in_waiting > 0:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    text = data.decode('utf-8', errors='ignore')
                    buffer += text
                    
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if self.state.state_name == "MENU":
                            if line and "j" in line.lower():
                                self.handle_space()
                            elif line and "h" in line.lower():
                                # changer de mode
                                next_mode_index = (MODES.index(self.state.selected_mode) + 1) % len(MODES)
                                self.set_mode(MODES[next_mode_index])
                            elif line and "best_score" in line.lower():
                                score = line.split(':')[1]
                                for i, part in enumerate(score.split('-')):
                                    mode = MODES[i]
                                    self.state.best_scores[mode] = int(part)

                        elif self.state.state_name == "PLAYING":
                            if self.state.selected_mode == "Button":    
                                if line and "f" in line.lower():
                                    self.handle_space()
                            if self.state.selected_mode == "Infrared":
                                if line and "i" in line.lower():
                                    self.handle_space()
                            elif self.state.selected_mode == "Digit_Encoder":
                                if line and "v" in line.lower():
                                    self.handle_space()
                            elif self.state.selected_mode == "Ultrasound":
                                if line and "u" in line.lower():
                                    num = line.split(':')[1]
                                    num = int(num.split(' ')[1]) // 119
                                    print("num =", num)
                                    if(num< 10):
                                        if saute:
                                            self.handle_space()
                                        saute =False
                                    else:
                                        saute = True
                            if line and "h" in line.lower():
                                self.return_to_menu()
                                               
                        elif self.state.state_name == "GAME_OVER":
                            if line and "h" in line.lower():
                                self.return_to_menu()
                            if line and "j" in line.lower():
                                self.handle_replay()
                        
                        if  line == "b":
                            self.toggle_info()

                        print(f"Reçu série: {line}")

            if self.state.state_name == "PLAYING":
                # Write angle to serial based on bird_y
                command = f"v:{self.state.vy}-{self.state.bird_y}\n"
                if self.serial_connected and self.serial_port:
                    self.serial_port.write(command.encode("utf-8"))
                    print(f"Envoyé série: {command.strip()}")
      
            
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

    def _setup_window(self):
        "Configure la fenêtre principale"
        try:
            self.attributes("-fullscreen", True)
        except Exception:
            self.state("zoomed")
        self.resizable(True, True)
    
    def _load_all_assets(self):
        "Charge tous les assets du jeu"
        self.assets.load_bird_sprite(BIRD_SPRITE)
        self.assets.load_bird_crash_sprite(BIRD_CRASH_SPRITE)
        self.assets.load_background()
        self.assets.preload_pipe_textures()
    
    def _setup_key_bindings(self):
        "Configure tous les bindings clavier"
        # Contrôles généraux
        self.bind_all("<Key-a>", lambda e: self.return_to_menu())
        self.bind_all("<Key-A>", lambda e: self.return_to_menu())

        self.bind_all("<Escape>", lambda e: self.destroy())        
        
        self.bind_all("<MouseWheel>", self.on_mouse_wheel)

        # Info overlay
        self.bind_all("<i>", lambda e: self.toggle_info())
        self.bind_all("<I>", lambda e: self.toggle_info())

        self.bind_all("<Key-r>", lambda e: self.handle_replay())
        self.bind_all("<Key-R>", lambda e: self.handle_replay())

        # Sélection de mode
        self.bind_all("<Key-1>", lambda e: self.set_mode("Button"))
        self.bind_all("<Key-2>", lambda e: self.set_mode("Infrared"))
        self.bind_all("<Key-3>", lambda e: self.set_mode("Digit_Encoder"))
        self.bind_all("<Key-4>", lambda e: self.set_mode("Ultrasound"))
        
        # Gameplay (Button mode)
        self.bind_all("<space>", lambda e: self.handle_space())
    
    # ==================== Actions utilisateur ====================
    def toggle_info(self):
        "Affiche/cache l'overlay d'information"
        if self.state.overlay_active:
            self.state.hide_info()
            # Reset du timer pour éviter un gros dt après la pause
            self.pipes_manager.timer.start()
            # Effacer les éléments déjà dessinés de l’overlay
            self.canvas.delete("info_overlay")
        else:
            self.state.show_info()
            self.pipes_manager.timer.pause()
        
        self.render_screen()

    
    def return_to_menu(self):
        if self.state.overlay_active:
            return
        "Retourne au menu"
        if self.state.state_name in ("PLAYING", "GAME_OVER"):
            self.change_state("MENU")
    
    def set_mode(self, mode_name: str):
        "Change le mode de jeu"
        if self.state.overlay_active: 
            return
        if self.state.state_name == "MENU":
            if self.state.set_mode(mode_name):
                self.renderer.render_menu()
    
    def handle_space(self):
        "Gère l'appui sur espace"
        if self.state.overlay_active:
            return
        
        # Démarrer le jeu depuis le menu
        if self.state.state_name == "MENU":
            self.change_state("PLAYING")
        
        # Gérer le saut pendant le jeu
        elif self.state.state_name == "PLAYING":
            if self.state.selected_mode in ["Button", "Infrared", "Digit_Encoder", "Ultrasound"]:
                self.flap()
    
        # Retry depuis Game Over
        elif self.state.state_name == "GAME_OVER":
            self.change_state("PLAYING")
    
    def flap(self):
        "Fait sauter l'oiseau"
        self.state.vy = self.physics.apply_flap()
    
    def on_mouse_wheel(self, e):
        # Active uniquement en jeu + mode Ultrasound + pas d'overlay
        if self.state.state_name != "PLAYING" or self.state.selected_mode != "Ultrasound":
            return
        if self.state.overlay_active:
            return

        direction = -1 if e.delta > 0 else 1  # -1 = vers le haut (y diminue), +1 = vers le bas
        self._apply_wheel(direction)

    def _apply_wheel(self, direction):
        # Pas de déplacement par "cran" de molette
        STEP = 30
        self.state.bird_y += direction * STEP

        # Clamp pour ne pas sortir de l'écran
        h = self.canvas.winfo_height() or HEIGHT
        from constants import BIRD_RADIUS
        top = BIRD_RADIUS
        bot = h - BIRD_RADIUS
        if self.state.bird_y < top:
            self.state.bird_y = top
        elif self.state.bird_y > bot:
            self.state.bird_y = bot

    def handle_replay(self):
        "Gère le démarrage du replay"
        if self.state.overlay_active:
            return
        
        # Depuis le menu ou game over
        if self.state.state_name in ("MENU", "GAME_OVER"):
            if self.replay.has_replay():
                self.start_replay_playback()
            else:
                print("[REPLAY] Aucun replay disponible")

    def start_replay_playback(self):
        "Démarre la lecture du replay"
        if self.replay.start_playback():
            self.state.set_state("REPLAY")
            self.reset_replay_display()
            self.render_screen()

    def reset_replay_display(self):
        "Prépare l'affichage pour le replay"
        self.canvas.delete("all")
        h = self.canvas.winfo_height() or HEIGHT
        self.state.bird_y = h // 2
        self.state.vy = 0
        self.state.score = 0
        self.state.pipes = []
        self.state.pipe_imgs = []
        
        # Réinitialiser le timer
        self.state.last_tick = time.time()
        
        # Réinitialiser les images de replay
        if hasattr(self, '_replay_pipe_imgs'):
            self._replay_pipe_imgs.clear()


    # ==================== Gestion des états ====================
    def change_state(self, new_state: str):
        "Change l'état du jeu"
        old_state = self.state.state_name
        
        if not self.state.set_state(new_state):
            return        
        # Arrêter le replay si on quitte REPLAY
        if old_state == "REPLAY":
            self.replay.stop_playback()
            self.renderer.clear_playfield()
        
        # Nettoyage en quittant PLAYING
        if old_state == "PLAYING" and new_state in ("GAME_OVER", "MENU"):
            self.replay.stop_recording()
            self.renderer.clear_playfield()
        
        # Réinitialiser l'animation du menu
        if new_state == "MENU":
            self.state.menu_animation_offset = 0
            command = "a"
            if self.serial_connected and self.serial_port:
                self.serial_port.write(command.encode("utf-8"))
        
        if new_state == "GAME_OVER":
            command = "g"
            if self.serial_connected and self.serial_port:
                self.serial_port.write(command.encode("utf-8"))
                # Filet de sécurité : re-pousser le best final du mode courant
           
        
        # Initialisation en entrant dans PLAYING
        if new_state == "PLAYING":
            self.reset_gameplay()
            self.replay.start_recording()
            if self.state.selected_mode == "Quit":
                self.destroy()
            elif self.state.selected_mode == "Button":
                command = "b"
                if self.serial_connected and self.serial_port:
                    self.serial_port.write(command.encode("utf-8"))
            elif self.state.selected_mode == "Infrared":
                command = "i"
                if self.serial_connected and self.serial_port:
                    self.serial_port.write(command.encode("utf-8"))
            elif self.state.selected_mode == "Ultrasound":
                command = "u"
                if self.serial_connected and self.serial_port:
                    self.serial_port.write(command.encode("utf-8"))
            elif self.state.selected_mode == "Digit_Encoder":
                command = "p"
                if self.serial_connected and self.serial_port:
                    self.serial_port.write(command.encode("utf-8"))
        
        self.render_screen()


    def reset_gameplay(self):
        "Réinitialise le gameplay"
        print("[DEBUG] reset_gameplay appelé")
        self.state.reset_gameplay_vars()
        
        # Nettoyage du canvas
        self.canvas.delete("all")
        
        # Position initiale de l'oiseau
        h = self.canvas.winfo_height() or HEIGHT
        self.state.bird_y = h // 2
        
        # Focus pour que les touches fonctionnent
        try:
            self.focus_force()
        except Exception:
            pass
        
        # Spawn du premier tuyau
        self.pipes_manager.spawn_pipe_pair(initial=True)
        self.pipes_manager.mark_pipe_spawn()
    
    # ==================== Update gameplay ====================
    def update_button_mode(self, dt):
        "Met à jour la physique en mode Button"
        # Gravité
        self.state.vy = self.physics.apply_gravity(self.state.vy)
        self.state.bird_y += self.state.vy
        
        # Collision avec les bords
        h = self.canvas.winfo_height() or HEIGHT
        if self.physics.check_bounds_collision(self.state.bird_y, h):
            self.change_state("GAME_OVER")
            return False
        
        # Spawn de tuyaux
        if self.pipes_manager.should_spawn_new_pipe():
            self.pipes_manager.spawn_pipe_pair()
            self.pipes_manager.mark_pipe_spawn()
        
        # Déplacement des tuyaux
        score_add = self.pipes_manager.move_pipes()
        if score_add:
            command = "s"
            if self.serial_connected and self.serial_port:
                self.serial_port.write(command.encode("utf-8"))



        # NOUVEAU - Enregistrer la frame AVEC les coordonnées des tuyaux
        if self.replay.is_recording:
            self.replay.record_frame(
                self.state.bird_y,
                self.state.vy,
                self.state.pipes,
                self.state.score,
                self.canvas
            )
        
        # Collision avec les tuyaux
        if self.physics.check_pipe_collision(
            self.state.bird_y, self.state.pipes, self.canvas
        ):
            self.change_state("GAME_OVER")
            return False
        
        return True
    
    def update_replay_mode(self, dt):
        "Met à jour le mode replay"
        # Vérifier si le replay est terminé
        if self.replay.is_replay_finished():
            self.change_state("MENU")
            return False
        
        # Récupérer la prochaine frame
        frame = self.replay.get_next_frame()
        if frame is None:
            self.change_state("MENU")
            return False
        
        # Appliquer l'état de la frame
        self.state.bird_y = frame['bird_y']
        self.state.vy = frame['vy']
        self.state.score = frame['score']
        
        # Redessiner les tuyaux à partir des données enregistrées
        self._draw_replay_pipes(frame['pipes'])
        
        return True

    def _draw_replay_pipes(self, pipes_data):
        "Dessine les tuyaux pendant le replay"
        # Nettoyer les anciens tuyaux
        self.canvas.delete("replay_pipe")
        self.canvas.delete("replay_pipe_img")
        
        w = self.canvas.winfo_width() or WIDTH
        h = self.canvas.winfo_height() or HEIGHT
        
        # Récupérer les textures
        pil_top, pil_bot = self.assets.get_pipe_textures(self.state.selected_mode)
        
        for pipe_info in pipes_data:
            # Récupérer les coordonnées depuis le pipe_info
            x = pipe_info.get('x', 0)
            top_h = pipe_info.get('top_h', 0)
            bot_y = pipe_info.get('bot_y', 0)
            pipe_width = pipe_info.get('width', PIPE_WIDTH)
            
            # Dessiner les rectangles
            self.canvas.create_rectangle(
                x, 0, x + pipe_width, top_h,
                fill="black",
                tags=("replay_pipe",)
            )
            self.canvas.create_rectangle(
                x, bot_y, x + pipe_width, h,
                fill="black",
                tags=("replay_pipe",)
            )
            
            # Dessiner les textures
            if pil_top:
                from PIL import ImageTk
                top_tk = ImageTk.PhotoImage(pil_top)
                self.canvas.create_image(
                    x, top_h, image=top_tk, anchor="sw",
                    tags=("replay_pipe_img",)
                )
                # Garder une référence pour éviter le garbage collection
                if not hasattr(self, '_replay_pipe_imgs'):
                    self._replay_pipe_imgs = []
                self._replay_pipe_imgs.append(top_tk)
            
            if pil_bot:
                from PIL import ImageTk
                bot_tk = ImageTk.PhotoImage(pil_bot)
                self.canvas.create_image(
                    x, bot_y, image=bot_tk, anchor="nw",
                    tags=("replay_pipe_img",)
                )
                if not hasattr(self, '_replay_pipe_imgs'):
                    self._replay_pipe_imgs = []
                self._replay_pipe_imgs.append(bot_tk)
        
        # Mettre l'oiseau au-dessus
        self.canvas.tag_raise("bird_img")
        self.canvas.tag_raise("hud")
            
    # ==================== Rendu ====================
    def render_screen(self):
        "Affiche l'écran en fonction de l'état"
        w = self.canvas.winfo_width() or WIDTH
        h = self.canvas.winfo_height() or HEIGHT
        
        if self.state.state_name == "MENU":
            self.canvas.delete("all")  # Nettoyer TOUT
            self.renderer.draw_menu_background()
            self.renderer.draw_title(w, h)
            self.renderer.render_menu()
            self.renderer.draw_footer(w, h)
        
        elif self.state.state_name == "PLAYING":
            # Ne PAS effacer "all" pendant le jeu, juste le HUD
            self.canvas.delete("hud")
            self.renderer.draw_play_background()
            self.renderer.draw_bird()
            self.renderer.update_score_hud()
            
        elif self.state.state_name == "REPLAY":
            self.canvas.delete("hud")
            self.renderer.draw_play_background()
            self.renderer.draw_bird()
            self.renderer.update_replay_hud()
        
        elif self.state.state_name == "GAME_OVER":
            self.canvas.delete("all")  # Nettoyer TOUT
            self.renderer.render_game_over()
        
        # Overlay par-dessus si actif
        if self.state.overlay_active and self.state.overlay_type == "INFO":
            self.renderer.render_info_overlay()
        else:
            self.canvas.delete("info_overlay")
                
    # ==================== Boucles ====================
    
    def game_loop(self):
        "Boucle principale du jeu"
        now = time.time()
        dt = now - self.state.last_tick
        self.state.last_tick = now

        # Si overlay actif, on freeze la logique de jeu
        if self.state.overlay_active:
            self.after(FPS_MS, self.game_loop)
            return
        
        # Animation continue du menu
        if self.state.state_name == "MENU":
            self.state.menu_animation_offset += 1
            if self.state.menu_animation_offset % 5 == 0:
                self.render_screen()
        
        # Animation continue du game over
        elif self.state.state_name == "GAME_OVER":
            self.state.menu_animation_offset += 1
            if self.state.menu_animation_offset % 3 == 0:
                self.render_screen()
        
        # NOUVEAU - Gestion du mode REPLAY
        elif self.state.state_name == "REPLAY":
            # Avancer 2x plus vite (effet x2)
            for _ in range(2):
                if not self.update_replay_mode(dt):
                    self.after(FPS_MS, self.game_loop)
                    return
            
            # Rendu
            self.renderer.draw_play_background()
            self.renderer.draw_bird()
            self.renderer.update_replay_hud()
        
        elif self.state.state_name == "PLAYING":            
            if self.state.selected_mode == "Button":
                # Mise à jour de la physique
                if not self.update_button_mode(dt):
                    self.after(FPS_MS, self.game_loop)
                    return
                
                # Rendu
                self.renderer.draw_play_background()
                self.renderer.update_score_hud()
                self.renderer.draw_bird()

            elif self.state.selected_mode == "Infrared":
                if not self.update_button_mode(dt):
                    self.after(FPS_MS, self.game_loop)
                    return
                
                self.renderer.draw_play_background()
                self.renderer.update_score_hud()
                self.renderer.draw_bird()

            elif self.state.selected_mode == "Digit_Encoder":
                if not self.update_button_mode(dt):
                    self.after(FPS_MS, self.game_loop)
                    return
                
                self.renderer.draw_play_background()
                self.renderer.update_score_hud()
                self.renderer.draw_bird()

            elif self.state.selected_mode == "Ultrasound": 
                if not self.update_button_mode(dt):
                    self.after(FPS_MS, self.game_loop)
                    return
                
                self.renderer.draw_play_background()
                self.renderer.update_score_hud()
                self.renderer.draw_bird()
        
        self.after(FPS_MS, self.game_loop)


    def blink_loop(self):
        "Boucle de clignotement du texte du menu "
        blink_targets = []

        # Clignotement du "Press X to start" dans le MENU
        if self.state.state_name == "MENU":
            blink_targets.append("press_start")
        
        # Clignotement du "Press I to close" dans l'overlay INFO
        if self.state.overlay_active and self.state.overlay_type == "INFO":
            blink_targets.append("info_close")

        if blink_targets:
            self.state.blink_on = not self.state.blink_on
            for tag in blink_targets:
                self.renderer.set_tag_visible(tag, self.state.blink_on)

        self.after(BLINK_MS, self.blink_loop)


# ==================== Point d'entrée ====================
if __name__ == "__main__":
    app = FlappyBirdApp()
    app.mainloop()
