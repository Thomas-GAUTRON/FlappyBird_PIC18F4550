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

# -- Thème Info Overlay --
INFO_PANEL_BG = "#1a1a1a"
INFO_PANEL_BORDER = "#FFD700"
INFO_TITLE_FONT = ("VT323", 60, "bold")
INFO_CONTROL_FONT = ("VT323", 35)
INFO_KEY_LPT_COLOR = "#FFD700"
INFO_KEY_PIC_COLOR = "#FF4444"
INFO_DESC_COLOR = "#FFFFFF"
INFO_CLOSE_FONT = ("VT323", 25)

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

# -- Contrôles Info --
INFO_CONTROLS = {
    "MENU": {
        "title": "CONTROLS - MENU",
        "controls": [
            ("1", "Potentiometer", "Button Mode"),
            ("2", "Potentiometer", "Infrared Mode"),
            ("3", "Potentiometer", "Potentiometer Mode"),
            ("4", "Potentiometer", "Ultrasound Mode"),
            ("SPACE", "Button 1", "Start Game"),
            ("I", "Button 2", "Toggle Info"),
            ("ESC", "Button 3", "Quit Game"),
        ]
    },
    "PLAYING": {
        "Button": {
            "title": "CONTROLS - BUTTON MODE",
            "controls": [
                ("SPACE", "Button 1", "Flap / Jump"),
                ("A", "Button 4", "Return to Menu"),
                ("I", "Button 2", "Show Info (Pause)"),
                ("ESC", "Button 3", "Quit Game")
            ]
        },
        "Infrared": {
            "title": "CONTROLS - INFRARED MODE",
            "controls": [
                ("SPACE", "Infrared Sensor", "Control Bird"),
                ("A", "Button 4", "Return to Menu"),
                ("I", "Button 2", "Show Info (Pause)"),
                ("ESC", "Button 3", "Quit Game")
            ]
        },
        "Potentiometer": {
            "title": "CONTROLS - POTENTIOMETER MODE",
            "controls": [
                ("_", "Digital Encoder", "Control Height"),
                ("A", "Button 4", "Return to Menu"),
                ("I", "Button 2", "Show Info (Pause)"),
                ("ESC", "Button 3", "Quit Game")
            ]
        },
        "Ultrasound": {
            "title": "CONTROLS - ULTRASOUND MODE",
            "controls": [
                ("_", "Ultrasound Sensor", "Control Height"),
                ("A", "Button 4", "Return to Menu"),
                ("I", "Button 2", "Show Info (Pause)"),
                ("ESC", "Button 3", "Quit Game")
            ]
        }
    },
    "GAME_OVER": {
        "title": "GAME OVER - OPTIONS",
        "controls": [
            ("SPACE", "Button 1", "Retry Same Mode"),
            ("A", "Button 4", "Return to Menu"),
            ("I", "Button 2", "Toggle Info"),
            ("ESC", "Button 3", "Quit Game")
        ]
    }
}
