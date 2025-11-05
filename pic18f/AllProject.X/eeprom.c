#include <xc.h>
// Fonction pour écrire dans l'EEPROM
void EEPROM_Write(unsigned char adresse, unsigned char donnee) {
    EEADR = adresse;
    EEDATA = donnee;
    EECON1bits.EEPGD = 0;
    EECON1bits.CFGS = 0;
    EECON1bits.WREN = 1;
    
    INTCONbits.GIE = 0;
    EECON2 = 0x55;
    EECON2 = 0xAA;
    EECON1bits.WR = 1;
    INTCONbits.GIE = 1;
    
    while(EECON1bits.WR);
    EECON1bits.WREN = 0;
}

// Fonction pour lire l'EEPROM
unsigned char EEPROM_Read(unsigned char adresse) {
    EEADR = adresse;
    EECON1bits.EEPGD = 0;
    EECON1bits.CFGS = 0;
    EECON1bits.RD = 1;
    return EEDATA;
}