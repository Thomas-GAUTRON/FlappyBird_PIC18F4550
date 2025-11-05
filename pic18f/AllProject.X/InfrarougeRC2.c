#include <xc.h>

// Configuration bits
#pragma config WDT = OFF
#pragma config MCLRE = ON
#pragma config DEBUG = OFF
#pragma config FOSC = HS

void __interrupt(high_priority) HighISR(void);

void main(void)
{
    // --- Initialisation des ports ---
    PORTA = 0;
    PORTC = 0;
    PORTE = 0;

    LATA = 0;
    LATC = 0;
    LATE = 0;

    TRISA = 0b00000100;   // RA2 (AN2) en entrée analogique
    TRISC = 0b00000000;   // PORTC en sortie
    TRISE = 0b00000000;   // RE0-RE2 en sortie

    LATEbits.LATE1 = 1;   // Active le capteur (Enable = 1)

    // --- Désactivation des fonctions spéciales sur PORTC ---
    RCSTAbits.SPEN = 0;       // UART off
    SSPCON1bits.SSPEN = 0;    // SPI off
    CCP1CON = 0;              // CCP/PWM off
    ADCON1 = 0x0F;            // Tous les ports en numérique

    // --- Configuration de l'ADC ---
    ADCON1 = 0b00001101;  // AN2 analogique
    ADCON0 = 0b00001001;  // Canal AN2, ADC activé
    ADCON2 = 0b10101110;  // Justification droite

    // --- Activation des interruptions ---
    PIE1bits.ADIE = 1;
    INTCONbits.PEIE = 1;
    INTCONbits.GIE = 1;

    // --- Démarre la première conversion ---
    ADCON0bits.GO_DONE = 1;

    // --- Boucle principale infinie ---
    while (1)
    {
        // Rien ici
    }
}

// ------------------------------------------------------
// Routine d'interruption ADC
// ------------------------------------------------------
void __interrupt(high_priority) HighISR(void)
{
    if (PIR1bits.ADIF)
    {
        PIR1bits.ADIF = 0;  // Efface le flag d’interruption

        // Met directement le bit 0 de ADRESH sur RC2
        LATC = (ADRESH & 0x01) << 2;

        // Relance la conversion
        ADCON0bits.GO_DONE = 1;
    }
}
