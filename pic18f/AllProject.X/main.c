#include "sysconfig.h"
#include <xc.h>
#include "main.h"
#include "usb_cdc_lib.h"
#include <stdio.h>
#include <string.h>

void __interrupt(high_priority) irq_handle_high(void);
#pragma config  WDT = OFF
#pragma config  MCLRE = ON
#pragma config  DEBUG = OFF
#pragma config  CPUDIV = OSC1_PLL2
int flap_event = 0;

int main()
{
    asm(
        "clrf TRISD\n" // PORTD en sortie (LED)
        "setf TRISB\n"
        "bcf INTCON2, 7 ; Disable PORTB pull-ups\n"
        "bcf INTCON, 7  ; Enable high priority interrupts\n"
        "bcf INTCON, 2 ; Clear INT0 flag\n"
        "bsf INTCON, 4 ; Enable INT0 interrupt\n"
    );

    initUSBLib();
    CDCSetBaudRate(38400); // Configurer le baudrate USB CDC à 38400 bps
    while (1)
    {
         USBDeviceTasks();
         if(isUSBReady())
        {
            PORTCbits.RC0 = 1;  // LED ON si USB pr�t
        }
        else
        {
            PORTCbits.RC0 = 0;  // LED OFF si USB pas pr�t
        }
        if(flap_event && isUSBReady())
        {
            putrsUSBUSART("f\n");
            flap_event -= 1;
        }
         CDCTxService();
    }
    return 0;
}

void __interrupt() irq_handle_high(void)
{
    processUSBTasks(); // G?re les ?v?nements USB
    // Test du flag : est-ce une interruption sur le port B ?
    if (INTCONbits.INT0IF)
    {
        asm(
            "bcf INTCON, 2 ; Clear INT0 flag\n"
            "incf _flap_event, F\n"
        );
    }
}
