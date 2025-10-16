import serial
import time

pic = serial.Serial('COM8', 9600)  # Adjust 'COM3' to your port

try:
    while True:
        command = input("Entrez une commande à envoyer au PIC (par exemple, 'START', 'STOP'): ")
        pic.write(command.encode('utf-8'))
        print("Commande envoyée:", command)
        time.sleep(1)  # Attendre un peu avant de lire la réponse
        if pic.in_waiting > 0:
            data = pic.readline().decode('utf-8').strip()
            print("Données reçues:", data)   

except KeyboardInterrupt:
    print("Arrêt du programme.")

except Exception as e:
    print("Erreur:", e) 