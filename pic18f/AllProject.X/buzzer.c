#include <xc.h>
#include <stdint.h>

//==============================================================
// CONFIGURATION BITS
//==============================================================
#pragma config FOSC = HS
#pragma config WDT = OFF
#pragma config MCLRE = ON
#pragma config DEBUG = OFF
#pragma config CPUDIV = OSC1_PLL2
#pragma config PBADEN = OFF

//==============================================================
// VARIABLES
//==============================================================
volatile uint8_t playSoundFlag = 0;  // Flag activé par le bouton
uint8_t noteIndex = 0;                // Index de la note actuelle

//==============================================================
// NOTES (périodes approximatives)
//==============================================================
#define NOTE_C5  160   // Do5, légèrement plus aigu que 170
#define NOTE_D5  143   // Ré5
#define NOTE_E5  127   // Mi5
#define NOTE_F5  120   // Fa5
#define NOTE_G5  107   // Sol5
#define NOTE_A5   95   // La5
#define NOTE_B4  180   // Si4, un peu plus grave
#define NOTE_B5   90   // Si5, plus aigu

#define DUREE_COURTE 30
#define DUREE_LONGUE 60

// Mélodie (début du thème principal d’Harry Potter)
const uint16_t melody[] = {
    NOTE_B4, NOTE_E5, NOTE_D5, NOTE_C5, NOTE_B4, NOTE_E5, NOTE_D5, NOTE_C5, NOTE_D5, NOTE_F5, NOTE_E5, NOTE_D5, NOTE_C5, NOTE_D5, NOTE_B4, NOTE_C5, NOTE_E5, NOTE_C5, NOTE_D5, NOTE_B4
};

const uint16_t durations[] = {
    DUREE_COURTE, DUREE_COURTE, DUREE_COURTE, DUREE_LONGUE,
    DUREE_COURTE, DUREE_COURTE, DUREE_COURTE, DUREE_LONGUE,
    DUREE_COURTE, DUREE_COURTE, DUREE_COURTE, DUREE_COURTE,
    DUREE_COURTE, DUREE_COURTE, DUREE_COURTE, DUREE_LONGUE,
    DUREE_COURTE, DUREE_COURTE, DUREE_COURTE, DUREE_LONGUE
};

#define MELODY_LENGTH (sizeof(melody)/sizeof(melody[0]))

//==============================================================
// PROTOTYPES
//==============================================================
void PLAY_NOTE(uint16_t period, uint16_t duration);
void DELAY(uint16_t count);

//==============================================================
// INTERRUPTION
//==============================================================
void __interrupt() ISR(void)
{
    if (INTCONbits.INT0IF)
    {
        playSoundFlag = 1;           // Active la note
        INTCONbits.INT0IF = 0;       // Clear flag
    }
}

//==============================================================
// PROGRAMME PRINCIPAL
//==============================================================
void main(void)
{
    // Configuration des ports
    ADCON1 = 0x0F;   // Tout en digital
    CMCON = 0x07;    // Désactive les comparateurs

    TRISE = 0x00;    // RE1 = sortie (buzzer)
    LATE  = 0x00;

    TRISBbits.TRISB0 = 1;  // RB0 = entrée (INT0)

    // Configuration interruption INT0
    INTCONbits.INT0IE = 1;  // Activer INT0
    INTCONbits.INT0IF = 0;  // Clear flag
    INTCONbits.GIE = 1;     // Activer interruptions globales

    while(1)
    {
        if(playSoundFlag)
        {
            // Joue la note actuelle
            PLAY_NOTE(melody[noteIndex], durations[noteIndex]);

            // Passe à la note suivante
            noteIndex++;
            if(noteIndex >= MELODY_LENGTH)
                noteIndex = 0;  // Reboucle sur le début

            playSoundFlag = 0;  // Attend le prochain appui
        }
        else
        {
            LATEbits.LATE1 = 0; // silence
        }
    }
}

//==============================================================
// Joue une note (signal carré) pendant "duration" ms
//==============================================================
void PLAY_NOTE(uint16_t period, uint16_t duration)
{
    uint16_t i, cycles = duration * 2;  // approximation simple

    for(i=0; i<cycles; i++)
    {
        LATEbits.LATE1 = 1;
        DELAY(period);
        LATEbits.LATE1 = 0;
        DELAY(period);
    }
}

//==============================================================
// DELAI simple
//==============================================================
void DELAY(uint16_t count)
{
    volatile uint16_t i;
    for(i=0; i<count; i++);
}