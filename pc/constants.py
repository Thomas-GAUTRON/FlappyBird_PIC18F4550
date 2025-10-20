# constants.py
"""
Fichier contenant toutes les constantes du jeu Flappy Bird
"""

# -- Fenêtre --
WIDTH, HEIGHT = 1080, 920 # Taille écran
FPS_MS = 16 # 1000 ms / 16 = 60 FPS
BLINK_MS = 500 # Clignotement à 1 Hz (500ms visible + 500ms invisible)

# -- Fichiers --
BESTSCORE_FILE = "bestscore.txt" # Stockage meilleur score

# -- Thème Menu --
MENU_COLOR = "#FFD700"
TITLE_FONT = ("VT323", 100)
MENU_FONT = ("VT323", 50)
FOOTER_FONT = ("VT323", 20)

SCORE_COLOR = MENU_COLOR
SCORE_FONT = ("VT323", 48, "bold")

BEST_COLOR = MENU_COLOR
BEST_FONT = ("VT323", 22)

MENU_ITEM_COLOR = "#FFFFFF"
MENU_ITEM_SELECTED_COLOR = MENU_COLOR

# -- Thème Game Over --
GAMEOVER_TITLE_FONT = ("VT323", 80, "bold")
GAMEOVER_SUBTITLE_FONT = ("VT323", 30)
GAMEOVER_SCORE_FONT = ("VT323", 40, "bold")
GAMEOVER_BG_COLOR = "black"
GAMEOVER_TITLE_COLOR = "#FF4444"
GAMEOVER_TEXT_COLOR = "#FFFFFF"
GAMEOVER_HIGHLIGHT_COLOR = "#FFD700"

# -- Animations --
MENU_ANIMATION_SPEED = 2  # vitesse d'animation du menu

# -- Modes de jeu --
MODES = ["Button", "Infrared", "Potentiometer", "Ultrasound"]
DEFAULT_MODE = "Button"

# -- Oiseau --
BIRD_X = 220
BIRD_RADIUS = 70
BIRD_SPRITE = "flappy.png"
BIRD_CRASH_SPRITE = "flappy_crash.png"

# -- Physique --
GRAVITY = 1.5
FLAP_IMPULSE = -100.0
MAX_VY = 15.0

# -- Tuyaux --
PIPE_CENTER_MIN_FRAC = 0.40 
PIPE_CENTER_MAX_FRAC = 0.70
PIPE_CENTER_DELTA_MINF = 0.20

PIPE_WIDTH = 135
PIPE_GAP_BASE = 210
PIPE_GAP_MIN = 350
PIPE_SPEED_BASE = 20.0
PIPE_SPEED_MAX = 20.0
PIPE_SPAWN_EVERY_MS = 1200
PIPE_GAP_JITTER = 100

# -- Sprite des tuyaux --
MODE_PIPE_SKINS = {
    "Button": ("pipes/p_u_gry.png", "pipes/p_b_gry.png"),
    "Infrared": ("pipes/p_u_serda.png", "pipes/p_b_serda.png"),
    "Potentiometer": ("pipes/p_u_pouf.png", "pipes/p_b_pouf.png"),
    "Ultrasound": ("pipes/p_u_serp.png", "pipes/p_b_serp.png"),
}
