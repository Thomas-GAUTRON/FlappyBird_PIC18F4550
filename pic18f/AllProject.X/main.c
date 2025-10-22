#include "sysconfig.h"
#include <xc.h>
#include "main.h"
#include "usb_cdc_lib.h"
#include <stdio.h>
#include <string.h>

typedef enum
{
    MODE_NOTHING,
    FLAPPY_ACCUEIL,
    FLAPPY_BTN,
    FLAPPY_POTENTIOMETRE,
} E_mode;

void __interrupt(high_priority) irq_handle_high(void);
void affiche_score(void);

#pragma config WDT = OFF
#pragma config MCLRE = ON
#pragma config DEBUG = OFF
#pragma config CPUDIV = OSC1_PLL2

uint8_t  flap_event = 0;
uint8_t  ADC_event = 0;
uint8_t  num7seg = 0;
int ADC_value;
int score = 1234;

E_mode current_mode = MODE_NOTHING;
volatile unsigned char timer_count = 0;

int main()
{
    /* Configuration des ports, INT0, ADC et Timer1 (assembleur inline) */
    asm(
        "; Configuration des ports\n"
        "MOVLW 0x00\n"
        "MOVWF TRISD\n"
        "MOVLW 0xFF\n"
        "MOVWF TRISB\n"
        "MOVLW 0x00\n"
        "MOVWF TRISC\n"
        "MOVLW 0x00\n"
        "MOVWF PORTC\n"
        "MOVLW 0x00\n"
        "MOVWF PORTD\n"
        "MOVLW 0xF0\n"
        "MOVWF TRISA\n"
        "MOVLW 0x0A\n"
        "MOVWF ADCON1\n"
        "; Configuration INT0\n"
        "BSF INTCON2, 7\n" /* Désactiver pull-ups (RBPU = bit 7) */
        "BSF INTCON, 7\n"  /* Activer interruptions hautes (GIEH = bit 7) */
        "BCF INTCON, 1\n"  /* Effacer flag INT0 (INT0IF = bit 1) */
        "BSF INTCON, 4\n"  /* Activer INT0 (INT0IE = bit 4) */
        "; Configuration ADC\n"
        "BCF PIR1, 6\n" /* Clear ADIF (ADIF = bit 6) */
        "BSF PIE1, 6\n" /* Enable ADC interrupt (ADIE = bit 6) */
        "MOVLW 0x20\n"  /* CHS = 8 (bits 5..2 = 1000) */
        "MOVWF ADCON0\n"
        "MOVLW 0x00\n" /* ADFM = 0 (justifié à gauche) et config par défaut */
        "MOVWF ADCON2\n"
        "BSF ADCON0, 0\n" /* ADON = bit 0 -> ADON = 1 */
        "; Configuration Timer1\n"
        "MOVLW 0xB0\n" /* RD16 = 1, T1CKPS = 0b11 => 0x80 + 0x30 = 0xB0 */
        "MOVWF T1CON\n"
        "MOVLW 0xC5\n"
        "MOVWF TMR1H\n"
        "MOVLW 0x68\n"
        "MOVWF TMR1L\n"
        "BCF PIR1, 0\n"  /* Clear TMR1IF (bit 0) */
        "BSF PIE1, 0\n"  /* Enable TMR1IE (bit 0) */
        "BSF T1CON, 0\n" /* Start Timer1 (TMR1ON = bit 0) */
    );
    initUSBLib();
    CDCSetBaudRate(38400); // Configurer le baudrate USB CDC à 38400 bps

    while (1)
    {
        affiche_score();
        USBDeviceTasks();

        if (isUSBReady())
        {
            PORTCbits.RC0 = 1; // LED ON si USB prêt
        }
        else
        {
            PORTCbits.RC0 = 0; // LED OFF si USB pas prêt
        }

        // Changer de mode en fonction des commandes reçues
        memset(usbReadBuffer, 0, sizeof(usbReadBuffer));                       // R?initialise buffer de lecture
        int numBytesRead = getsUSBUSART(usbReadBuffer, sizeof(usbReadBuffer)); // Lit les donn?es re?ues
        if (numBytesRead > 0)
        {
            if (usbReadBuffer[0] == 'a')
            {
                current_mode = FLAPPY_ACCUEIL;
                score = 0;
                putrsUSBUSART("Accueil\n");
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
            else if (usbReadBuffer[0] == 's')
            {
                score += 1;
                putrsUSBUSART("Score incrémenté\n");               
            }
            else
            {
                current_mode = MODE_NOTHING;
                putrsUSBUSART("Mode inconnu\n");
            }
        }

        if (flap_event && isUSBReady() && (current_mode == FLAPPY_BTN || current_mode == FLAPPY_ACCUEIL))
        {
            putrsUSBUSART("f\n");
            flap_event -= 1;
        }

        if (ADC_event && isUSBReady() && (current_mode == FLAPPY_POTENTIOMETRE || current_mode == FLAPPY_ACCUEIL))
        {
            char buffer[20];
            sprintf(buffer, "ADC:%d\n", ADC_value);
            putrsUSBUSART(buffer);
            ADC_event = 0;
        }

        CDCTxService();
    }
    return 0;
}

int tab_int_to_7seg(int val)
{
    int tab[10] = {0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F};
    return tab[val];
}

void affiche_score()
{
    int buffer_score = score;
    if(num7seg == 0) {
        PORTD = 0x00;
        PORTA = 0x01;
        PORTD = tab_int_to_7seg(buffer_score % 10);
    }
    else if(num7seg == 1) {
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
    else if(num7seg == 3){
        PORTD = 0x00;
        PORTA = 0x08;
        buffer_score /= 1000;
        PORTD = tab_int_to_7seg(buffer_score % 10);
    }
    num7seg = (num7seg + 1)%4;
}

void __interrupt(high_priority) irq_handle_high(void)
{
    processUSBTasks(); // Gère les événements USB

    // Interruption INT0 (via ASM pour flags)
    if (INTCONbits.INT0IF)
    {
        asm(
            "INCF _flap_event, F\n"
            "BCF INTCON, 1\n"
        );
    }

    // Interruption ADC (clear flag en ASM, récupérer ADRESH en m)
    if (PIR1bits.ADIF)
    {
       
        /* Clear ADIF (bit 6 of PIR1) via ASM */
        asm(
            "MOVLW 0x01\n"
            "MOVWF _ADC_event\n"
            "MOVFF ADRESH, _ADC_value\n"
            "BCF PIR1, 6\n"
            );
    }

    // Interruption Timer1 - toutes les ~10ms
    else if (PIR1bits.TMR1IF)
    {
        // Recharger Timer1
        TMR1H = 0xC5;
        TMR1L = 0x68;
        PIR1bits.TMR1IF = 0;

        timer_count++;

        // Tous les 10 x 10ms = 100ms
        if (timer_count >= 10)
        {
            timer_count = 0;

            // Démarrer conversion ADC si aucune conversion en cours
            if (ADCON0bits.GO == 0 && (current_mode == FLAPPY_POTENTIOMETRE || current_mode == FLAPPY_ACCUEIL))
            {
                ADCON0bits.GO = 1;
            }
        }
    }
}
