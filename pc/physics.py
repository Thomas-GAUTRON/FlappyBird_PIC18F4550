# physics.py
"""
Moteur physique du jeu (gravité, collisions, etc.)
"""

from constants import (
    GRAVITY, FLAP_IMPULSE, MAX_VY, BIRD_RADIUS, BIRD_X
)


class PhysicsEngine:
    "Classe gérant la physique du jeu"
    
    @staticmethod
    def apply_gravity(vy: float) -> float:
        "vélocité verticale"
        return max(-MAX_VY, min(MAX_VY, vy + GRAVITY))
    
    @staticmethod
    def apply_flap() -> float:
        "impulsion du saut"
        return FLAP_IMPULSE
    
    @staticmethod
    def check_bounds_collision(bird_y: float, height: int) -> bool:
        "Vérifie si l'oiseau touche le plafond ou le sol"
        top = BIRD_RADIUS
        bot = height - BIRD_RADIUS
        return bird_y <= top or bird_y >= bot
    
    @staticmethod
    def circle_rect_collision(cx, cy, r2, rx1, ry1, rx2, ry2) -> bool:
        "Détecte une collision entre un cercle et un rectangle (oiseau et tuyaux)"
        # Point le plus proche du centre sur le rectangle
        if cx < rx1:
            closest_x = rx1
        elif cx > rx2:
            closest_x = rx2
        else:
            closest_x = cx
        
        if cy < ry1:
            closest_y = ry1
        elif cy > ry2:
            closest_y = ry2
        else:
            closest_y = cy
        
        dx = cx - closest_x
        dy = cy - closest_y
        return (dx * dx + dy * dy) <= r2
    
    @staticmethod
    def check_pipe_collision(bird_y: float, pipes, canvas) -> bool:
        "Vérifie si l'oiseau entre en collision avec un tuyau"
        cx = BIRD_X
        cy = int(bird_y)
        r = BIRD_RADIUS
        r2 = r * r
        
        for (top, bot, _) in pipes:
            tx1, ty1, tx2, ty2 = canvas.coords(top)
            bx1, by1, bx2, by2 = canvas.coords(bot)
            
            if PhysicsEngine.circle_rect_collision(cx, cy, r2, tx1, ty1, tx2, ty2) or \
               PhysicsEngine.circle_rect_collision(cx, cy, r2, bx1, by1, bx2, by2):
                return True
        
        return False