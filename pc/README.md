🐦 FLAPPIC-BIRD - Documentation
Projet Flappy Bird pour microcontrôleur, développé par PIOUPIOUTEAM.
📁 Structure du projet
flappy-bird/

main.py                 # Point d'entrée de l'application
constants.py            # Toutes les constantes du jeu
assets_manager.py       # Gestion du chargement des assets
game_state.py           # Gestion de l'état du jeu et des scores
physics.py              # Moteur physique (gravité, collisions)
pipes_manager.py        # Gestion des tuyaux (spawn, déplacement)
renderer.py             # Rendu graphique (menus, bird, HUD)
assets                # Dossier des ressources


🎮 Architecture des modules
main.py
Classe principale FlappyBirdApp qui orchestre l'ensemble du jeu :

Initialisation de la fenêtre Tkinter
Création et coordination des autres modules
Gestion des boucles de jeu et de rendu
Binding des touches clavier

constants.py
Contient toutes les constantes configurables :

Dimensions de la fenêtre
Paramètres de physique (gravité, vitesse)
Configuration des tuyaux
Thème graphique (couleurs, polices)
Modes de jeu disponibles

assets_manager.py
Classe AssetsManager pour la gestion des ressources :

Chargement des images (Pillow)
Conversion en ImageTk pour Tkinter
Suppression des fonds colorés (colorkey)
Cache des textures de tuyaux
Redimensionnement automatique

game_state.py
Classe GameState pour l'état du jeu :

Gestion des états (MENU, PLAYING, GAME_OVER)
Sélection du mode de jeu
Variables de gameplay (position oiseau, vitesse, etc.)
Gestion des scores (actuel et meilleur)
Sauvegarde/chargement du meilleur score

physics.py
Classe PhysicsEngine pour la physique :

Application de la gravité
Impulsion du saut
Détection de collision cercle-rectangle
Vérification des collisions avec les bords

pipes_manager.py
Classe PipesManager pour les tuyaux :

Spawn de paires de tuyaux avec variation
Déplacement et suppression
Calcul dynamique du gap (difficulté progressive)
Gestion du scoring au passage

renderer.py
Classe Renderer pour le rendu :

Affichage des menus (titre, options, footer)
Dessin de l'oiseau et des sprites
Mise à jour du HUD (score, meilleur score)
Écrans de game over
Gestion de la visibilité des éléments

🎯 Modes de jeu

Button (Implémenté) : Contrôle avec la barre espace
Infrared (À venir) : Capteur infrarouge
Potentiometer (À venir) : Potentiomètre analogique
Ultrasound (À venir) : Capteur à ultrasons

⌨️ Contrôles
Menu

C : Mode Button
V : Mode Infrared
B : Mode Potentiometer
N : Mode Ultrasound
X : Démarrer le jeu
M : Quitter

En jeu (Mode Button)

ESPACE : Faire sauter l'oiseau
ENTER : Retour au menu


📝 Prochaines améliorations

 Implémenter les modes Infrared, Potentiometer, Ultrasound
 Ajouter des effets sonores
 Multiples niveaux de difficulté
 Interface de configuration
 Intégration avec le microcontrôleur

👥 Équipe
PIOUPIOUTEAM

Projet de microcontrôleur - Flappy Bird