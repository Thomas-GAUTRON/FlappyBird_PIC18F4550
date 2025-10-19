# assets_manager.py
"""
Gestion du chargement et du traitement des assets (images, sprites)
"""

import os
from PIL import Image, ImageTk
from constants import BIRD_RADIUS, MODE_PIPE_SKINS


class AssetsManager:
    "Classe responsable du chargement et de la gestion des assets"
    
    def __init__(self):
        self._bird_src = None
        self._bird_tk = None

        self._bird_crash_src = None
        self._bird_crash_tk = None
        
        self._bg_src = None
        self._bg_tk = None
        self._bg_size = None
        
        self._pipe_tex_cache = {}
    
    @staticmethod
    def get_asset_path(name: str) -> str:
        "Retourne le chemin complet vers un asset"
        return os.path.join(os.path.dirname(__file__), "assets", name)
    
    @staticmethod
    def colorkey_rgba(img, key=(255, 0, 255), tol=40):
        "Remplace la couleur 'key' par de la transparence (rendre les rectangles et l oval invisible)"
        img = img.convert("RGBA")
        px = img.load()
        w, h = img.size
        kr, kg, kb = key
        
        for y in range(h):
            for x in range(w):
                r, g, b, a = px[x, y]
                if abs(r - kr) <= tol and abs(g - kg) <= tol and abs(b - kb) <= tol:
                    px[x, y] = (r, g, b, 0)  # alpha = 0
        return img
    
    def load_bird_sprite(self, sprite_name: str):
        "Charge le sprite de l'oiseau"
        try:
            img = Image.open(self.get_asset_path(sprite_name)).convert("RGBA")
            img = self.colorkey_rgba(img, key=(255, 0, 255), tol=40)
            
            size = BIRD_RADIUS * 2
            img = img.resize((size, size), Image.LANCZOS)
            self._bird_src = img
            self._bird_tk = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"[BIRD] Impossible de charger le sprite: {e}")
            self._bird_src = None
            self._bird_tk = None

    def load_bird_crash_sprite(self, sprite_name: str):
        "Charge le sprite de l'oiseau crashé pour le game over"
        try:
            img = Image.open(self.get_asset_path(sprite_name)).convert("RGBA")
            img = self.colorkey_rgba(img, key=(255, 0, 255), tol=40)
            size = BIRD_RADIUS * 2
            img = img.resize((size, size), Image.LANCZOS)
            self._bird_crash_src = img
            self._bird_crash_tk = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"[BIRD-CRASH] Impossible de charger le sprite: {e}")
            self._bird_crash_src = None
            self._bird_crash_tk = None
    
    def load_background(self):
        "Charge le fond d'écran"
        try:
            self._bg_src = Image.open(
                self.get_asset_path("background.png")
            ).convert("RGB")
        except Exception as e:
            print(f"[MENU BG] Impossible de charger l'image: {e}")
            self._bg_src = None
    
    def get_background_image(self, bg_type: str, width: int, height: int):
        "Retourne l'image de fond redimensionnée"
       
        src = self._bg_src
        if getattr(self, "_bg_size", None) != (width, height):
            if src:
                img = src.resize((width, height), Image.LANCZOS)
                self._bg_tk = ImageTk.PhotoImage(img)
                self._bg_size = (width, height)
        return self._bg_tk

    
    def preload_pipe_textures(self):
        "Charge les textures de tuyaux pour tous les modes"
        for mode, (top_rel, bot_rel) in MODE_PIPE_SKINS.items():
            top_img = bot_img = None
            
            try:
                top_img = Image.open(self.get_asset_path(top_rel)).convert("RGBA")
                top_img = self.colorkey_rgba(top_img, key=(255, 0, 255), tol=40)
            except Exception as e:
                print(f"[PIPE] Load top failed for {mode}: {e}")
            
            try:
                bot_img = Image.open(self.get_asset_path(bot_rel)).convert("RGBA")
                bot_img = self.colorkey_rgba(bot_img, key=(255, 0, 255), tol=40)
            except Exception as e:
                print(f"[PIPE] Load bottom failed for {mode}: {e}")
            
            self._pipe_tex_cache[mode] = (top_img, bot_img)
    
    def get_pipe_textures(self, mode: str):
        "Retourne les textures de tuyaux en fonction du mode"
        tpl = self._pipe_tex_cache.get(mode)
        if tpl and all(tpl):
            return tpl
        
        # Fallback sur le mode Button
        tpl = self._pipe_tex_cache.get("Button")
        if tpl and all(tpl):
            return tpl
        
        return (None, None)
    
    @staticmethod
    def resize_pipe_texture(src_img, w, h, flip_vertical=False):
        "Redimensionne une texture de tuyau"
        if src_img is None or w <= 0 or h <= 0:
            return None
        
        img = src_img.transpose(Image.FLIP_TOP_BOTTOM) if flip_vertical else src_img
        img = img.resize((int(w), int(h)), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    
    @property
    def bird_tk(self):
        "Retourne l'image Tk de l'oiseau"
        return self._bird_tk
    
    @property
    def bird_crash_tk(self):
        return self._bird_crash_tk
