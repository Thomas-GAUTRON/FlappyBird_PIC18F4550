;==============================================================
; FICHIER : PushButton_INT0_FSM.asm
; OBJET   : Bouton anti-rebond géré par FSM, déclenché par interruption haute
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
flap_flag       ; Flag levé à 1 pour un appui validé
int_request     ; Flag interne : interruption INT0 reçue
    ENDC

;==============================================================
; VECTEURS D’INTERRUPTION
;==============================================================
    ORG     0x0000
    goto    init

    ORG     0x0008               ; vecteur haute priorité
    goto    isr_high

    ORG     0x0018               ; vecteur basse priorité
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
    movwf   TRISB           ; RB0 = entrée bouton
    movlw   b'11111110'
    movwf   TRISC           ; RC0 sortie LED événement
    bsf     INTCON2,7       ; désactiver pull-ups (nRBPU=1)
    movlw   0x0F
    movwf   ADCON1          ; désactiver entrées analogiques

    clrf    btn_state
    clrf    bounce_cnt
    clrf    flap_flag
    clrf    int_request

    ;----------------------------------------------
    ; CONFIGURATION INTERRUPTION EXTERNE INT0
    ;----------------------------------------------
    bsf     RCON, IPEN        ; active priorités high/low
    bsf     INTCON, GIEH      ; active interruptions hautes globales
    bsf     INTCON2, INTEDG0  ; déclenche sur front montant (0→1)
    bcf     INTCON, INT0IF    ; clear flag INT0
    bsf     INTCON, INT0IE    ; active INT0

;==============================================================
; BOUCLE PRINCIPALE
;==============================================================
main_loop:
    call    button_fsm
    goto    main_loop

;==============================================================
; INTERRUPTION HAUTE PRIORITÉ
;==============================================================
isr_high:
    btfss   INTCON, INT0IF
    retfie

    ; Déclenchement détecté : marquer la demande
    movlw   1
    movwf   int_request

    ; Effacer le flag d’interruption matériel
    bcf     INTCON, INT0IF
    retfie

;==============================================================
; MACHINE À ÉTATS (FSM anti-rebond)
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

    ; si une interruption a signalé un appui
    movf    int_request, W
    bz      fsm_end          ; si 0, rien à faire

    ; sinon, on entre en phase de rebond
    movlw   STATE_BOUNCE
    movwf   btn_state
    clrf    bounce_cnt
    clrf    int_request
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

    btfss   PORTB, 0         ; bouton relâché ?
    goto    reset_idle

    incf    bounce_cnt, F
    movf    bounce_cnt, W
    sublw   DEBOUNCE_MAX
    bnz     fsm_end

    ; appui validé
    movlw   STATE_PRESSED
    movwf   btn_state
    clrf    bounce_cnt

    movlw   1
    movwf   flap_flag        ; lever flag unique
    movlw   FLAP_CODE
    call    send_event
    goto    fsm_end

reset_idle:
    movlw   STATE_IDLE
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
    btfsc   PORTB, 0         ; si bouton toujours appuyé
    goto    fsm_end

    movlw   STATE_RELEASE
    movwf   btn_state
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
    btfsc   PORTB, 0
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
; ÉVÉNEMENT VISUEL (LED RC0)
;==============================================================
send_event: 
    bsf     LATC, 0
    call    delay_100ms
    bcf     LATC, 0
    return

;==============================================================
; DÉLAI ~100 ms @ 8 MHz
;==============================================================
delay_100ms:
    movlw   D'18'
d1:
    movwf   tmp1
d2:
    decfsz  tmp1, F
    goto    d2
    decfsz  WREG, F
    goto    d1
    return

    END
