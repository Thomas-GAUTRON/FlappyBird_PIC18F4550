;==============================================================
; FICHIER : PushButtonNoRebound.asm
; OBJET   : Bouton anti-rebond (IDLE?BOUNCE?PRESSED?RELEASE)
; MCU     : PIC18F4550
;==============================================================

    LIST    P=18F4550
    #include <p18f4550.inc>

;==============================================================
; CONFIGURATION BITS
;==============================================================
    CONFIG  FOSC = HS
    CONFIG  WDT = OFF
    CONFIG  MCLRE = ON
    CONFIG  DEBUG = OFF
    CONFIG  CPUDIV = OSC1_PLL2
    CONFIG  PBADEN = OFF

;==============================================================
; CONSTANTES
;==============================================================
STATE_IDLE      EQU 0
STATE_BOUNCE    EQU 1
STATE_PRESSED   EQU 2
STATE_RELEASE   EQU 3

DEBOUNCE_MAX    EQU 20
FLAP_CODE       EQU 1

;==============================================================
; VARIABLES
;==============================================================
    CBLOCK  0x20
btn_state
bounce_cnt
tmp1
tmp2
    ENDC

;==============================================================
; PROGRAMME PRINCIPAL
;==============================================================
    ORG     0x0000
    goto    init

    ORG     0x0008
    retfie

;==============================================================
; INITIALISATION
;==============================================================
init:
    clrf    PORTB
    clrf    LATB
    clrf    PORTC
    clrf    LATC

    movlw   b'00000001'
    movwf   TRISB           ; RB0 entrée (bouton), RB4?RB7 sorties (LED état)
    movlw   b'11111110'
    movwf   TRISC           ; RC0 sortie (LED événement)
    bsf     INTCON2,7       ; désactiver pull-ups (nRBPU=1)
    movlw   0x0F
    movwf   ADCON1          ; désactiver entrées analogiques

    clrf    btn_state
    clrf    bounce_cnt

main_loop:
    call    button_fsm
    goto    main_loop

;==============================================================
; MACHINE À ÉTATS
;==============================================================
button_fsm:
    movf    btn_state, W

;--------------------------------------------------------------
; IDLE
;--------------------------------------------------------------
    xorlw   STATE_IDLE
    btfss   STATUS, Z
    goto    check_bounce

in_idle:
    movlw   b'00010000'
    movwf   LATB
    btfsc   PORTB, 0         ; si RB0=1 ? appui détecté
    goto    pressed_detected
    goto    fsm_end

pressed_detected:
    movlw   STATE_BOUNCE
    movwf   btn_state
    clrf    bounce_cnt
    goto    fsm_end

;--------------------------------------------------------------
; BOUNCE
;--------------------------------------------------------------
check_bounce:
    movf    btn_state, W
    xorlw   STATE_BOUNCE
    btfss   STATUS, Z
    goto    check_pressed

in_bounce:
    movlw   b'00100000'
    movwf   LATB
    btfsc   PORTB, 0         ; tant que bouton = 1
    goto    still_pressed
    movlw   STATE_IDLE
    movwf   btn_state
    goto    fsm_end

still_pressed:
    incf    bounce_cnt, F
    movf    bounce_cnt, W
    sublw   DEBOUNCE_MAX
    bnz     fsm_end
    movlw   STATE_PRESSED
    movwf   btn_state
    clrf    bounce_cnt
    goto    fsm_end

;--------------------------------------------------------------
; PRESSED
;--------------------------------------------------------------
check_pressed:
    movf    btn_state, W
    xorlw   STATE_PRESSED
    btfss   STATUS, Z
    goto    check_release

in_pressed:
    movlw   b'01000000'
    movwf   LATB
    btfsc   PORTB, 0         ; si RB0=1 ? encore appuyé
    goto    fsm_end
    movlw   STATE_RELEASE
    movwf   btn_state
    ; événement FLAP
    movlw   FLAP_CODE
    call    send_event
    clrf    bounce_cnt
    goto    fsm_end

;--------------------------------------------------------------
; RELEASE
;--------------------------------------------------------------
check_release:
    movf    btn_state, W
    xorlw   STATE_RELEASE
    btfss   STATUS, Z
    goto    fsm_end

in_release:
    movlw   b'10000000'
    movwf   LATB
    btfsc   PORTB, 0         ; bouton relâché = 0
    goto    fsm_end
    incf    bounce_cnt, F
    movf    bounce_cnt, W
    sublw   DEBOUNCE_MAX
    bnz     fsm_end
    movlw   STATE_IDLE
    movwf   btn_state
    clrf    bounce_cnt
    goto    fsm_end

fsm_end:
    return

;==============================================================
; ÉVÉNEMENT (LED RC0)
;==============================================================
    
send_event: 
    bsf     LATC, 0
    call    delay_1s
    bcf     LATC, 0
    return

;==============================================================
; DÉLAI ~1 s @ 8 MHz
;==============================================================
delay_1s:
    movlw   D'180'
d1:
    movwf   tmp1
d2:
    decfsz  tmp1, F
    goto    d2
    decfsz  WREG, F
    goto    d1
    return

    END
