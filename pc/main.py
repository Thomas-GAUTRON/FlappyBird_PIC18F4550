# main.py
"""
Fichier principal de Flappy Bird
Point d'entrée de l'application
"""

import tkinter as tk
import time

from constants import (
    WIDTH, HEIGHT, FPS_MS, BLINK_MS, 
    BIRD_SPRITE, BIRD_CRASH_SPRITE, MODES
)
from assets_manager import AssetsManager
from game_state import GameState
from physics import PhysicsEngine
from pipes_manager import PipesManager
from renderer import Renderer
import serial


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
    
     # ================== Série ==================
    def _init_serial(self):
        try:
            # Remplace 'COM3' par le port série de ton périphérique
            # et 9600 par le baudrate utilisé
            self.serial_port = serial.Serial('COM8', 38400, timeout=0.1)
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
                            if line and "f" in line.lower():
                                self.start_game()
                            elif line and "adc" in line.lower():
                                value = line.split(":")[-1].strip()
                                adc_value = int(value)
                                print(f"Valeur ADC reçue: {adc_value}")
                                pas = 255 // len(MODES)
                                mode_index = adc_value // pas
                                self.set_mode(MODES[mode_index])

                        elif self.state.state_name == "PLAYING":    
                            if  self.state.selected_mode == "Button":
                                if line and "f" in line.lower():
                                    self.handle_space()
                        
                        elif self.state.state_name == "GAME_OVER":
                            if line and "f" in line.lower():
                                self.return_to_menu()

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
        self.bind_all("<Key-x>", lambda e: self.start_game())
        self.bind_all("<Return>", lambda e: self.return_to_menu())
        self.bind_all("<Key-m>", lambda e: self.destroy())
        
        # Sélection de mode
        self.bind_all("<Key-c>", lambda e: self.set_mode("Button"))
        self.bind_all("<Key-v>", lambda e: self.set_mode("Infrared"))
        self.bind_all("<Key-b>", lambda e: self.set_mode("Potentiometer"))
        self.bind_all("<Key-n>", lambda e: self.set_mode("Ultrasound"))
        
        # Gameplay (Button mode)
        self.bind_all("<space>", lambda e: self.handle_space())
    
    # ==================== Actions utilisateur ====================
    
    def start_game(self):
        "Démarre le jeu"
        if self.state.state_name == "MENU":
            self.change_state("PLAYING")
    
    def return_to_menu(self):
        "Retourne au menu"
        if self.state.state_name in ("PLAYING", "GAME_OVER"):
            self.change_state("MENU")
    
    def set_mode(self, mode_name: str):
        "Change le mode de jeu"
        if self.state.state_name == "MENU":
            if self.state.set_mode(mode_name):
                self.renderer.render_menu()
    
    def handle_space(self):
        "Gère l'appui sur espace (saut)"
        if self.state.state_name == "PLAYING" and self.state.selected_mode == "Button":
            self.flap()
    
    def flap(self):
        "Fait sauter l'oiseau"
        self.state.vy = self.physics.apply_flap()
    
    # ==================== Gestion des états ====================
    
    def change_state(self, new_state: str):
        "Change l'état du jeu"
        old_state = self.state.state_name
        
        if not self.state.set_state(new_state):
            return  # Pas de changement
        
        # Nettoyage en quittant PLAYING
        if old_state == "PLAYING" and new_state in ("GAME_OVER", "MENU"):
            self.renderer.clear_playfield()
        # Réinitialiser l'animation du menu
        if new_state == "MENU":
            self.state.menu_animation_offset = 0
            command = "a"
            if self.serial_connected and self.serial_port:
                self.serial_port.write(command.encode("utf-8"))
                
        # Initialisation en entrant dans PLAYING
        if new_state == "PLAYING":
            self.reset_gameplay()
            if self.state.selected_mode == "Button":
                command = "b"
                if self.serial_connected and self.serial_port:
                    self.serial_port.write(command.encode("utf-8"))
        
        self.render_screen()
    
    def reset_gameplay(self):
        "Réinitialise le gameplay"
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

        
        # Collision avec les tuyaux
        if self.physics.check_pipe_collision(
            self.state.bird_y, self.state.pipes, self.canvas
        ):
            self.change_state("GAME_OVER")
            return False
        
        return True
    
    # ==================== Rendu ====================
    
    def render_screen(self):
        "Affiche l'écran en fonction de l'état"
        self.canvas.delete("hud")
        w = self.canvas.winfo_width() or WIDTH
        h = self.canvas.winfo_height() or HEIGHT
        
        if self.state.state_name == "MENU":
            self.canvas.delete("all")
            self.renderer.draw_menu_background()
            self.renderer.draw_title(w, h)
            self.renderer.render_menu()
            self.renderer.draw_footer(w, h)
        
        elif self.state.state_name == "PLAYING":
            if self.state.selected_mode == "Button":
                self.renderer.draw_bird()
                self.renderer.update_score_hud()
                self.renderer.update_best_hud()
            else:
                self.renderer.render_placeholder_mode()
        
        elif self.state.state_name == "GAME_OVER":
            self.renderer.render_game_over()
    
    # ==================== Boucles ====================
    
    def game_loop(self):
        "Boucle principale du jeu"
        now = time.time()
        dt = now - self.state.last_tick
        self.state.last_tick = now
        
        # Animation continue du menu
        if self.state.state_name == "MENU":
            self.state.menu_animation_offset += 1
            if self.state.menu_animation_offset % 5 == 0:
                self.render_screen()
        
        # Animation continue du game over
        if self.state.state_name == "GAME_OVER":
            self.state.menu_animation_offset += 1
            # Redessine pour les étoiles
            if self.state.menu_animation_offset % 3 == 0:
                self.render_screen()
        
        if self.state.state_name == "PLAYING":
            if self.state.selected_mode == "Button":
                # Mise à jour de la physique
                if not self.update_button_mode(dt):
                    # Game over détecté
                    self.after(FPS_MS, self.game_loop)
                    return
                
                # Rendu
                self.renderer.draw_play_background()
                self.renderer.update_score_hud()
                self.renderer.draw_bird()
            
            else:
                # Modes non implémentés
                self.renderer.render_placeholder_mode()
        
        self.after(FPS_MS, self.game_loop)
    
    def blink_loop(self):
        "Boucle de clignotement du texte du menu / placeholder"
        blink_targets = []

        # Clignotement du "Press X to start" dans le MENU
        if self.state.state_name == "MENU":
            blink_targets.append("press_start")

        # Clignotement du "Press ENTER → MENU" dans le placeholder (modes non implémentés)
        if self.state.state_name == "PLAYING" and self.state.selected_mode != "Button":
            blink_targets.append("ph_enter")

        if blink_targets:
            self.state.blink_on = not self.state.blink_on
            for tag in blink_targets:
                self.renderer.set_tag_visible(tag, self.state.blink_on)

        self.after(BLINK_MS, self.blink_loop)


# ==================== Point d'entrée ====================
if __name__ == "__main__":
    app = FlappyBirdApp()
    app.mainloop()