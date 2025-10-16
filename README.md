# Projet Flappy Bird PIC18F4550
Membre du projet:
 - BEAUGEANT Clément 
 - CHAUDEMANCHE Nicolas
 - COLIN Malo
 - GAUTRON Thomas 

## Description
Implémentation d'un jeu Flappy Bird sur un microcontrôleur PIC18F4550.

## Communication USB
- `pic18f/USB/` : Dossier contenant les code du PIC18F4550
	- `main.py` : Fichier python pour faire communiquer le pc et le PIC18F4550
	- `usbcdcdemo.X/` : Projet MPLAB/X contenant le code s'exécutant sur le PIC18F4550 pour faire fonctionné l'USB CDC.

La pile USB CDC utilisée dans ce dépôt provient du projet suivant : https://github.com/dilshan/pic18f4550-usb-cdc/tree/master
Ce code fournit une interface CDC (COM virtuel) entre le PIC et le PC. 
