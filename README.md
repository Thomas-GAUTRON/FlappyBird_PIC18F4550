# Projet Flappy Bird PIC18F4550
Membre du projet:
 - BEAUGEANT Clément 
 - CHAUDEMANCHE Nicolas
 - COLIN Malo
 - GAUTRON Thomas 


##  Description du projet
Flappic-Bird est une réimplémentation du jeu **Flappy Bird** sur une carte de développement **EasyPIC v7**. Le jeu utilise plusieurs capteurs pour contrôler le mouvement de l’oiseau et affiche l’interface graphique via une communication UART entre la carte et un PC.

### Objectifs
- Implémenter les mécaniques de base du jeu (gravité, saut, détection de collisions).
- Comparer la précision et le temps de réponse de différents capteurs :
  - Encodeur numérique
  - Bouton poussoir
  - Capteur à ultrasons (HC-SR04)
  - Capteur infrarouge (IR Distance Click)
- Développer une interface graphique en Python
- Enregistrer les meilleurs scores en EEPROM.
- Mode "replay" pour revivre la dernière partie.

## Fonctionnalités
- **4 modes de contrôle** (encodeur, bouton, ultrasons, IR).
- **Menu interactif** (Jouer, Instructions, Replay).
- **Affichage du score** sur des affichages 7-segments et un buzzer.
- **Communication USB** entre la carte EasyPIC et le PC.
- **Mode replay** pour visualiser la dernière partie en accéléré.
- **Aspect ratio** étudié pour optimiser l’apprentissage d’un algorithme génétique (NEAT).


## 🛠 Matériel requis
- **Carte EasyPIC v7** ([manuel](https://download.mikroe.com/documents/full-featured-boards/easy/easypic-v7/easypic-v7-manual-v104c.pdf))
- **Capteurs** :
  - Encodeur numérique
  - Bouton poussoir
  - HC-SR04 (ultrasons)
  - IR Distance Click ([lien](https://www.mikroe.com/ir-distance-click))
- **Affichage** :
  - GLCD (pour l’angle de l’oiseau)
  - 7-segments (pour le score)
- **Buzzer** pour les effets sonores.
- **PC** pour l’interface graphique (Python).
