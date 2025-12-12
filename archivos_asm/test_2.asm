.386
option casemap:none
include \masm32\include\masm32rt.inc
includelib \masm32\lib\masm32.lib
includelib \masm32\lib\kernel32.lib
printf PROTO C :VARARG

.data
DVC_MSG DB 'Error en tiempo de ejecución: División por Cero.', 0 ; STRING
OVF_INT_MSG DB 'Error en tiempo de ejecución: Overflow en suma de INT.', 0 ; STRING
OVF_FLOAT_MSG DB 'Error en tiempo de ejecución: Overflow en suma de FLOAT.', 0 ; STRING
V_INF_CONST DD 7F800000h ; HEX_FLOAT
V_NINF_CONST DD 7F800000h ; HEX_FLOAT
V_DA_CERO__ DB "Da cero: ",0 ; STRING
V_C2 DD 2 ; INT
V_C3 DD 3 ; INT
V_C1_5 DD 1.5 ; FLOAT
V_C2_EP1 DD 2.e+1 ; FLOAT
V_C1 DD 1 ; INT
V_C10 DD 10 ; INT
V_L_G_F1 DD 0 ; INT
V_K_G_F1 DD 0 ; INT
V_C0 DD 0 ; INT
V_A_G DD 0 ; INT
V_B_G DD 0 ; INT
V_C_G DD 0 ; INT
V_X_G DD 0.0 ; FLOAT
V_Y_G DD 0.0 ; FLOAT
V_I_G_F1 DD 0 ; INT
V_A_0 DD 0 ; INT
V_A_1 DD 0 ; INT
V_A_2 DD 0 ; INT
V_A_3 DD 0 ; INT
V_A_4 DD 0 ; INT
V_A_5 DD 0 ; INT
V_A_6 DD 0 ; INT
V_A_7 DD 0 ; INT
V_A_8 DD 0 ; INT
V_A_9 DD 0 ; INT
V_A_10 DD 0 ; INT
V_A_11 DD 0 ; INT
V_A_12 DD 0 ; INT
V_A_13 DD 0 ; INT
V_A_14 DD 0 ; INT
V_A_15 DD 0 ; INT
V_A_16 DD 0 ; INT
V_A_17 DD 0 ; INT
V_A_18 DD 0 ; INT
V_A_19 DD 0 ; INT
V_A_20 DD 0 ; INT
V_A_21 DD 0 ; INT
V_A_22 DD 0 ; INT
V_A_23 DD 0 ; INT
V_A_24 DD 0 ; INT
V_A_25 DD 0 ; INT
V_A_26 DD 0 ; INT
V_A_27 DD 0 ; INT
V_A_28 DD 0 ; INT
V_A_29 DD 0 ; INT
V_A_30 DD 0 ; INT
V_A_31 DD 0 ; INT
V_A_32 DD 0 ; INT
V_A_33 DD 0 ; INT
V_A_34 DD 0 ; INT
V_A_35 DD 0 ; INT
V_A_36 DD 0 ; INT
V_A_37 DD 0 ; INT
V_A_38 DD 0 ; INT
NEWLINE DB 13,10,0 ; STRING
HELLO_MSG DB "El programa se ejecuto correctamente.",0

.code
start:
LABEL_0:
LABEL_1:
    MOV EAX, dword ptr [V_C2]
    MOV dword ptr [V_A_G], EAX
LABEL_2:
    MOV EAX, dword ptr [V_C3]
    MOV dword ptr [V_B_G], EAX
LABEL_3:
    FLD dword ptr [V_C1_5]
    FSTP dword ptr [V_X_G]
LABEL_4:
    FLD dword ptr [V_C2_EP1]
    FSTP dword ptr [V_Y_G]
LABEL_5:
    MOV EAX, dword ptr [V_A_G]
    MOV dword ptr [V_L_G_F1], EAX
LABEL_6:
    MOV EAX, dword ptr [V_B_G]
    MOV dword ptr [V_K_G_F1], EAX
LABEL_7:
    CALL F1_G_F1
    MOV dword ptr [V_A_7], EAX
LABEL_8:
    MOV EAX, dword ptr [V_L_G_F1]
    MOV dword ptr [V_A_G], EAX
LABEL_9:
    MOV EAX, dword ptr [V_K_G_F1]
    MOV dword ptr [V_B_G], EAX
LABEL_10:
    MOV EAX, dword ptr [V_A_7]
    MOV dword ptr [V_C_G], EAX
LABEL_11:
    invoke printf, cfm$("%d\n"), dword ptr [V_A_G]
LABEL_12:
    invoke printf, cfm$("%d\n"), dword ptr [V_B_G]
LABEL_13:
    invoke printf, cfm$("%d\n"), dword ptr [V_C_G]
LABEL_14:
  ; Suma INT 32 bits - Terceto 38
  MOV EAX, dword ptr V_A_G
  ADD EAX, dword ptr V_B_G
  JO ErrorOverflowInt
  MOV dword ptr [V_A_14], EAX
LABEL_15:
 ; Comparacion (==) - Terceto 44
   MOV EAX, dword ptr [V_A_14]
   CMP EAX, dword ptr [V_C0]
    SETE AL
    MOVZX EAX, AL
    MOV dword ptr [V_A_15], EAX
LABEL_16:
    CMP dword ptr [V_A_15], 0
    JE LABEL_20
LABEL_17:
    invoke printf, addr V_DA_CERO__
    invoke printf, addr NEWLINE
LABEL_18:
  ; Suma INT 32 bits - Terceto 57
  MOV EAX, dword ptr V_A_G
  ADD EAX, dword ptr V_B_G
  JO ErrorOverflowInt
  MOV dword ptr [V_A_18], EAX
LABEL_19:
    invoke printf, cfm$("%d\n"), dword ptr [V_A_18]
LABEL_20:
LABEL_21:
LABEL_22:

F1_G_F1:
    PUSH EBP
    MOV EBP, ESP
LABEL_23:
    MOV EAX, dword ptr [V_C1]
    MOV dword ptr [V_I_G_F1], EAX
LABEL_24:
    MOV EAX, dword ptr [V_C0]
    MOV dword ptr [V_L_G_F1], EAX
LABEL_25:
    MOV EAX, dword ptr [V_C0]
    MOV dword ptr [V_K_G_F1], EAX
LABEL_26:
LABEL_27:
 ; Comparacion (<) - Terceto 82
   MOV EAX, dword ptr [V_I_G_F1]
   CMP EAX, dword ptr [V_C10]
    SETL AL
    MOVZX EAX, AL
    MOV dword ptr [V_A_27], EAX
LABEL_28:
    CMP dword ptr [V_A_27], 0
    JE LABEL_36
LABEL_29:
  ; Suma INT 32 bits - Terceto 92
  MOV EAX, dword ptr V_L_G_F1
  ADD EAX, dword ptr V_I_G_F1
  JO ErrorOverflowInt
  MOV dword ptr [V_A_29], EAX
LABEL_30:
    MOV EAX, dword ptr [V_A_29]
    MOV dword ptr [V_L_G_F1], EAX
LABEL_31:
  ; Resta INT 32 bits - Terceto 101
  MOV EAX, dword ptr [V_K_G_F1]
  SUB EAX, dword ptr [V_I_G_F1]
  MOV dword ptr [V_A_31], EAX
LABEL_32:
    MOV EAX, dword ptr [V_A_31]
    MOV dword ptr [V_K_G_F1], EAX
LABEL_33:
  ; Suma INT 32 bits - Terceto 109
  MOV EAX, dword ptr V_I_G_F1
  ADD EAX, dword ptr V_C1
  JO ErrorOverflowInt
  MOV dword ptr [V_A_33], EAX
LABEL_34:
    MOV EAX, dword ptr [V_A_33]
    MOV dword ptr [V_I_G_F1], EAX
LABEL_35:
JMP LABEL_26
LABEL_36:
LABEL_37:
    MOV EAX, dword ptr [V_C10]
    MOV ESP, EBP
    POP EBP
    RET
LABEL_38:
    MOV ESP, EBP
    POP EBP
    RET
    jmp fin

; ----- HANDLERS DE ERROR -----
ErrorOverflowInt:
    print "Error en tiempo de ejecucion: Overflow en INT"
    invoke ExitProcess, 1
ErrorOverflowFloat:
    print "Error en tiempo de ejecucion: Overflow en FLOAT"
    invoke ExitProcess, 1
ErrorDVC:
    print "Error en tiempo de ejecucion: Division por Cero"
    invoke ExitProcess, 1

fin:
    print ADDR HELLO_MSG
    invoke ExitProcess, 0
end start