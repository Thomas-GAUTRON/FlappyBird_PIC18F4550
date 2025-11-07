#include "sysconfig.h"
#include <xc.h>
#include "main.h"
#include "glcd.h"
#include "usb_cdc_lib.h"
#include "eeprom.h"
#include <stdio.h>

#define TRIGGER LATCbits.LATC7
#define ECHO PORTCbits.RC6
#define TRIG_TRIS TRISCbits.TRISC7
#define ECHO_TRIS TRISCbits.TRISC6

void __interrupt(high_priority) irq_handle_high(void);
void affiche_score(void);
void writeOnGlcd(void);
void PLAY_NOTE(uint16_t period, uint16_t duration);
void init_pins(void);
void init_timer1(void);
unsigned int mesurer_distance(void);

typedef enum
{
    MODE_NOTHING,
    FLAPPY_ACCUEIL,
    FLAPPY_BTN,
    FLAPPY_POTENTIOMETRE,
    FLAPPY_INFRA,
    FLAPPY_ULTRA
} E_mode;

uint8_t flap_event = 0;
uint8_t event_C0, event_C1;
uint8_t ADC_event = 0;
uint8_t num7seg = 0;
uint8_t type = 0;
uint8_t ADC_value;
uint8_t bon_infra;
int score = 1234;
uint8_t bs_but, bs_infra, bs_de, bs_us;
// uint8_t distance = 0, event_dist = 0;

E_mode current_mode = MODE_NOTHING;
volatile unsigned char timer_count = 0;

int main()
{
    PORTB = 0;
    PORTD = 0;
    TRISCbits.RC7 = 0;
    TRISCbits.RC6 = 0;

    glcd_Init(GLCD_ON);
    initUSBLib();
    CDCSetBaudRate(38400); // Configurer le baudrate USB CDC Ã  38400 bps
    // Configuration des ports, INT0, ADC et Timer1 (assembleur inline)
    bs_but = EEPROM_Read(100);
    bs_infra = EEPROM_Read(101);
    bs_de = EEPROM_Read(102);
    bs_us = EEPROM_Read(103);
    asm(
        "; Configuration des ports\n"
        "MOVLW 0xF8\n"
        "MOVWF TRISA\n"

        "; Configuration INT0\n"
        "BSF INTCON2, 7\n" /* Dï¿½sactiver pull-ups (RBPU = bit 7) */
        "BSF INTCON, 7\n"  /* Activer interruptions hautes (GIEH = bit 7) */
        "BCF INTCON, 1\n"  /* Effacer flag INT0 (INT0IF = bit 1) */
        "BSF INTCON, 4\n"  /* Activer INT0 (INT0IE = bit 4) */

        "; Configuration INT1\n"
        "BCF INTCON3, 0\n" /* Effacer flag INT1 (INT1IF = bit 0) */
        "BSF INTCON3, 4\n" /* Activer INT1 (INT1IE = bit 4) */

        "; Configuration INT2\n"
        "BCF INTCON3, 1\n" /* Effacer flag INT2 (INT2IF = bit 1) */
        "BSF INTCON3, 5\n" /* Activer INT2 (INT2IE = bit 5) */

        "; Configuration ADC\n"
        "BCF PIR1, 6\n" // Clear ADIF (ADIF = bit 6)
        "BSF PIE1, 6\n" // Enable ADC interrupt (ADIE = bit 6)
        "MOVLW 0x0D\n"  // CHS = 9 (bits 5..2 = 1001)
        "MOVWF ADCON0\n"
        "MOVLW 0x0F\n"
        "MOVWF ADCON1\n"
        "MOVLW 0x00\n" // ADFM = 0 (justifiÃ© Ã  gauche) et config par dÃ©faut
        "MOVWF ADCON2\n"
        "BSF ADCON0, 0\n" // ADON = bit 0 -> ADON = 1
    );
    CMCON = 0x07; // DÃ©sactive les comparateurs
    TRISE = 0x00; // RE1 = sortie (buzzer)
    PORTEbits.RE2 = 1;

    while (1)
    {
        if (ADCON0bits.GO == 0 && current_mode == FLAPPY_INFRA )
        {
            ADCON0bits.GO = 1;
        }
        type++;
        USBDeviceTasks();
        if (type == 0)
        {
            INTCONbits.INT0F = 0;
            INTCON3bits.INT1F = 0;
            INTCON3bits.INT2F = 0;

            INTCONbits.INT0E = 0;
            INTCON3bits.INT1E = 0;
            INTCON3bits.INT2E = 0;

            TRISBbits.TRISB0 = 0;
            TRISBbits.TRISB1 = 0;
            TRISBbits.TRISB2 = 0;

            PORTA = 0x0;
            writeOnGlcd();

            PORTBbits.RB0 = 0;
            PORTBbits.RB1 = 0;
            PORTBbits.RB2 = 0;
            LATBbits.LATB0 = 0;
            LATBbits.LATB1 = 0;
            LATBbits.LATB2 = 0;
            __delay_us(10);

            TRISBbits.TRISB0 = 1;
            TRISBbits.TRISB1 = 1;
            TRISBbits.TRISB2 = 1;

            INTCONbits.INT0F = 0;
            INTCON3bits.INT1F = 0;
            INTCON3bits.INT2F = 0;

            INTCONbits.INT0E = 1;
            INTCON3bits.INT1E = 1;
            INTCON3bits.INT2E = 1;
        }
        else
        {
            affiche_score();
        }

        if (isUSBReady())
        {
            // Changer de mode en fonction des commandes reÃ§ues
            memset(usbReadBuffer, 0, sizeof(usbReadBuffer));                       // R?initialise buffer de lecture
            int numBytesRead = getsUSBUSART(usbReadBuffer, sizeof(usbReadBuffer)); // Lit les donn?es re?ues
            if (numBytesRead > 0)
            {
                if (usbReadBuffer[0] == 'a')
                {
                    char buffer[30];
                    switch(current_mode){
                        case FLAPPY_BTN:
                            if(score > bs_but)
                            {
                                bs_but = score;
                                EEPROM_Write(100, score);
                            }
                            break;
                        case FLAPPY_INFRA:
                            if(score > bs_infra)
                            {
                                bs_infra = score;
                                EEPROM_Write(101, score);
                            }
                            break;
                        case FLAPPY_POTENTIOMETRE:
                            if(score > bs_de)
                            {
                                bs_de = score;
                                EEPROM_Write(102, score);
                            }
                            break;
                        case FLAPPY_ULTRA:
                            if(score > bs_us)
                            {
                                bs_us = score;
                                EEPROM_Write(103, score);
                            }
                            break;
                        default:
                            break;
                    }
                    
                    sprintf(buffer, "best_score:%d-%d-%d-%d\n", 
                            bs_but, bs_infra, bs_de, bs_us);
                    current_mode = FLAPPY_ACCUEIL;
                    score = 0;
                    putrsUSBUSART(buffer);
                }
                else if (usbReadBuffer[0] == 'b')
                {
                    current_mode = FLAPPY_BTN;
                    score = 0;
                    putrsUSBUSART("Button\n");
                }
                else if (usbReadBuffer[0] == 'p')
                {
                    current_mode = FLAPPY_POTENTIOMETRE;
                    score = 0;
                    putrsUSBUSART("Potentiometre\n");
                }
                else if (usbReadBuffer[0] == 'i')
                {
                    current_mode = FLAPPY_INFRA;
                    score = 0;
                    putrsUSBUSART("Infrarouge\n");
                }
                else if (usbReadBuffer[0] == 's')
                {
                    score += 1;
                    PLAY_NOTE(180, 30);
                    putrsUSBUSART("Score incrÃ©mentÃ©\n");
                }
                else
                {
                    current_mode = MODE_NOTHING;
                    putrsUSBUSART("Mode inconnu\n");
                }
            }

            if ((flap_event & 0x1) && (current_mode == FLAPPY_BTN || current_mode == FLAPPY_ACCUEIL))
            {
                putrsUSBUSART("f\n");
                asm(
                    "BCF _flap_event, 0\n");
            }
            if ((flap_event & 0x2) && (current_mode == FLAPPY_BTN || current_mode == FLAPPY_ACCUEIL))
            {
                putrsUSBUSART("b\n");
                asm(
                    "BCF _flap_event, 1\n");
            }
            if ((flap_event & 0x4) && (current_mode == FLAPPY_BTN || current_mode == FLAPPY_ACCUEIL))
            {
                putrsUSBUSART("h\n");
                asm(
                    "BCF _flap_event, 2\n");
            }
            
           /* if(current_mode == FLAPPY_ULTRA) {
                distance = mesurer_distance();
                if (distance < 6) {
                    if(event_dist)
                    {
                        putrsUSBUSART("u\n");
                    }
                    event_dist = 0;
                }
                else{
                    event_dist = 1;
                }
                    
            }*/

            if (PORTCbits.RC0 == 1)
            {
                if (event_C0)
                {
                    putrsUSBUSART("v\n");
                }
                event_C0 = 0;
            }
            else
            {
                event_C0 = 1;
            }

            if (PORTCbits.RC1 == 1)
            {
                if (event_C1)
                {
                    putrsUSBUSART("f\n");
                }
               event_C1 = 0;
            }
            else
            {
                event_C1 = 1;
            }

            if ((ADC_event & 0x2) && current_mode == FLAPPY_INFRA)
            {
                if (ADC_value > 50)
                    {
                        if(bon_infra == 1)
                        {
                            putrsUSBUSART("f\n");
                        }
             
                        bon_infra = 0;
                    }
                    else
                    {
                        bon_infra = 1;
                    }
         
   
                    ADC_event = 0;
                
            }
            CDCTxService();
        }
        else
        {
            PORTCbits.RC0 = 0; // LED OFF si USB pas prÃªt
        }
    }
}

int tab_int_to_7seg(int val)
{
    int tab[10] = {0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F};
    return tab[val];
}

void affiche_score()
{
    int buffer_score = score;
    if (num7seg == 0)
    {
        PORTD = 0x00;
        PORTA = 0x01;
        PORTD = tab_int_to_7seg(buffer_score % 10);
    }
    else if (num7seg == 1)
    {
        PORTD = 0x00;
        PORTA = 0x02;
        buffer_score /= 10;
        PORTD = tab_int_to_7seg(buffer_score % 10);
    }
    else if (num7seg == 2)
    {
        PORTD = 0x00;
        PORTA = 0x04;
        buffer_score /= 100;
        PORTD = tab_int_to_7seg(buffer_score % 10);
    }
    else if (num7seg == 3)
    {
        PORTD = 0x00;
        PORTA = 0x08;
        buffer_score /= 1000;
        PORTD = tab_int_to_7seg(buffer_score % 10);
    }
    num7seg = (num7seg + 1) % 3;
}

void writeOnGlcd()
{
    glcd_SetCursor(1, 0);
    glcd_WriteString("HELLO", 5, F8X8, GLCD_WHITE);
    //  glcd_DrawLine(0, 50, 127, 100, GLCD_WHITE);
}

void DELAY(uint16_t count)
{
    volatile uint16_t i;
    for (i = 0; i < count; i++)
        ;
}

void PLAY_NOTE(uint16_t period, uint16_t duration)
{
    uint16_t i, cycles = duration * 2; // approximation simple

    for (i = 0; i < cycles; i++)
    {
        LATEbits.LATE1 = 1;
        DELAY(period);
        LATEbits.LATE1 = 0;
        DELAY(period);
    }
}
/*
void init_pins(void) {
    TRIG_TRIS = 0;  // TRIGGER en sortie
    ECHO_TRIS = 1;  // ECHO en entrée
    TRIGGER = 0;
}

void init_timer1(void) {
    T1CON = 0x00;   // Timer1 désactivé, prescaler 1:1
    TMR1H = 0;
    TMR1L = 0;
}

unsigned int mesurer_distance(void) {
    unsigned int temps_us = 0;
    unsigned int distance = 0;
    
    // 1. Envoyer une impulsion de 10µs sur TRIGGER
    TRIGGER = 1;
    __delay_us(10);
    TRIGGER = 0;
    
    // 2. Attendre que ECHO passe à HIGH (timeout 30ms)
    unsigned int timeout = 0;
    while(ECHO == 0 && timeout < 3000) {
        __delay_us(10);
        timeout++;
    }
    
    if(timeout >= 3000) return 0; // Timeout, pas d'écho
    
    // 3. Démarrer le Timer1
    TMR1H = 0;
    TMR1L = 0;
    T1CONbits.TMR1ON = 1;
    
    // 4. Attendre que ECHO passe à LOW (timeout 30ms)
    timeout = 0;
    while(ECHO == 1 && timeout < 3000) {
        __delay_us(10);
        timeout++;
        if(TMR1H > 0xFF) break; // Overflow protection
    }
    
    // 5. Arrêter le Timer1
    T1CONbits.TMR1ON = 0;
    
    // 6. Lire la valeur du timer
    temps_us = (TMR1H << 8) | TMR1L;
    
    // 7. Calculer la distance
    // À 48MHz avec prescaler 1:1, chaque tick = 1/12 µs
    // temps_us représente le temps en ticks
    temps_us = temps_us / 12;  // Conversion en µs réels
    
    // Distance (cm) = temps(µs) / 58
    // (vitesse son = 340 m/s, aller-retour divisé par 2)
    distance = temps_us / 58;
    
    return distance;
}*/

void __interrupt(high_priority) irq_handle_high(void)
{
    // On ne traite l'USB que si c'est une interruption USB
    if (UIRbits.URSTIF || UIRbits.IDLEIF || UIRbits.ACTVIF || UIRbits.STALLIF || UIRbits.SOFIF || UIRbits.TRNIF)
    {
        processUSBTasks(); // GÃ¨re les Ã©vÃ©nements USB uniquement si nÃ©cessaire
    }

    // Interruption INT0 (via ASM pour flags)
    if (INTCONbits.INT0IF && INTCONbits.INT0E)
    {
        asm(
            "BSF _flap_event, 0\n"
            "BCF INTCON, 1\n");
    }
    if (INTCON3bits.INT1IF && INTCON3bits.INT1E)
    {

        asm(
            "BSF _flap_event, 1\n"
            "BCF INTCON3, 0\n");
    }
    if (INTCON3bits.INT2IF && INTCON3bits.INT2E)
    {
        asm("BSF _flap_event, 2\n"
            "BCF INTCON3, 1\n");
    }

    // Interruption ADC (clear flag en ASM, rÃ©cupÃ©rer ADRESH en m)
    else if (PIR1bits.ADIF)
    {
        // Clear ADIF (bit 6 of PIR1) via ASM
        asm(
            "BSF _ADC_event, 1\n"
            "MOVFF ADRESH, _ADC_value\n"
            "BCF PIR1, 6\n");
    }
}