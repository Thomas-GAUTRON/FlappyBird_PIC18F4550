#include "sysconfig.h"
#include <xc.h>
#include "main.h"
#include "usb_cdc_lib.h"
#include <stdio.h>
#include <string.h>

void main(void) {
    // Initialisation de la biblioth?que USB
    initUSBLib();

    while (1) {
        // G?re les ?v?nements USB
        USBDeviceTasks();
        // V?rifie si l'USB est pr?t ? fonctionner
        if (isUSBReady()) {
            // Communication via USB CDC
            memset(usbReadBuffer, 0, sizeof(usbReadBuffer));  //R?initialise buffer de lecture
            uint8_t numBytesRead = getsUSBUSART(usbReadBuffer, sizeof(usbReadBuffer)); // Lit les donn?es re?ues

            if (numBytesRead > 0) {
                // Formate une r?ponse avec le message re?u
                snprintf(usbWriteBuffer, 32, "message recu: %s\n", usbReadBuffer);
                // Envoie les donn?es modifi?es
                putUSBUSART(usbWriteBuffer, strlen(usbWriteBuffer)); 
            }

            CDCTxService(); // Assure l'envoi des donn?es via USB
        }
    }
}