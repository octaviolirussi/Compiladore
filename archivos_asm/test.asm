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
V_C3 DD 3 ; INT
V_C1_5 DD 1.5 ; FLOAT
V_C2_EP1 DD 2.e+1 ; FLOAT
V_B_G_F1_F2 DD 0 ; INT
V_C6 DD 6 ; INT
V_C15 DD 15 ; INT
V_C10 DD 10 ; INT
V_C4 DD 4 ; INT
V_A_G_F1 DD 0 ; INT
V_C2 DD 2 ; INT
V_A_G DD 0 ; INT
V_B_G DD 0 ; INT
V_C_G DD 0 ; INT
V_X_G DD 0.0 ; FLOAT
V_Y_G DD 0.0 ; FLOAT
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
V_A_13 DD 0.0 ; FLOAT
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
V_A_39 DD 0 ; INT
V_A_40 DD 0 ; INT
V_A_41 DD 0 ; INT
NEWLINE DB 13,10,0 ; STRING
V_TMP_DOUBLE DQ 0.0 ; FLOAT64
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
    MOV EAX, dword ptr [V_B_G]
    MOV dword ptr [V_A_G_F1], EAX
LABEL_6:
    CALL F1_G_F1
    MOV dword ptr [V_A_6], EAX
LABEL_7:
    MOV EAX, dword ptr [V_A_G_F1]
    MOV dword ptr [V_B_G], EAX
LABEL_8:
    invoke printf, cfm$("%d\n"), dword ptr [V_A_6]
LABEL_9:
    MOV EAX, dword ptr [V_B_G]
    MOV dword ptr [V_A_G_F1], EAX
LABEL_10:
    CALL F1_G_F1
    MOV dword ptr [V_A_10], EAX
LABEL_11:
    MOV EAX, dword ptr [V_A_G_F1]
    MOV dword ptr [V_B_G], EAX
LABEL_12:
  ; Suma INT 32 bits - Terceto 34
  MOV EAX, dword ptr V_A_10
  ADD EAX, dword ptr V_C2
  JO ErrorOverflowInt
  MOV dword ptr [V_A_12], EAX
LABEL_13:
  ; CONV_I_F (INT a FLOAT) - Terceto 40
  FILD dword ptr [V_A_12]
  FSTP dword ptr [V_A_13]
LABEL_14:
    FLD dword ptr [V_A_13]
    FSTP dword ptr [V_X_G]
LABEL_15:
    FLD dword ptr [V_X_G]
    FSTP qword ptr [V_TMP_DOUBLE]
    invoke printf, cfm$("%f\n"), [V_TMP_DOUBLE]
LABEL_16:
    invoke printf, cfm$("%d\n"), dword ptr [V_B_G]
LABEL_17:
LABEL_18:

F1_G_F1:
    PUSH EBP
    MOV EBP, ESP
LABEL_19:
    invoke printf, cfm$("%d\n"), dword ptr [V_A_G_F1]
LABEL_20:
    MOV EAX, dword ptr [V_C6]
    MOV dword ptr [V_B_G_F1_F2], EAX
LABEL_21:
    CALL F2_G_F1_F2
    MOV dword ptr [V_A_21], EAX
LABEL_22:
    MOV EAX, dword ptr [V_A_21]
    MOV dword ptr [V_A_G_F1], EAX
LABEL_23:
  ; Suma INT 32 bits - Terceto 70
  MOV EAX, dword ptr V_A_G_F1
  ADD EAX, dword ptr V_C2
  JO ErrorOverflowInt
  MOV dword ptr [V_A_23], EAX
LABEL_24:
    MOV EAX, dword ptr [V_A_23]
    MOV dword ptr [V_A_G_F1], EAX
LABEL_25:
 ; Comparacion (<=) - Terceto 79
   MOV EAX, dword ptr [V_A_G_F1]
   CMP EAX, dword ptr [V_C15]
    SETLE AL
    MOVZX EAX, AL
    MOV dword ptr [V_A_25], EAX
LABEL_26:
    CMP dword ptr [V_A_25], 0
    JE LABEL_30
LABEL_27:
  ; Suma INT 32 bits - Terceto 89
  MOV EAX, dword ptr V_C10
  ADD EAX, dword ptr V_C10
  JO ErrorOverflowInt
  MOV dword ptr [V_A_27], EAX
LABEL_28:
    MOV EAX, dword ptr [V_A_27]
    MOV ESP, EBP
    POP EBP
    RET
LABEL_29:
JMP LABEL_32
LABEL_30:
LABEL_31:
    MOV EAX, dword ptr [V_C4]
    MOV ESP, EBP
    POP EBP
    RET
LABEL_32:
LABEL_33:
    MOV ESP, EBP
    POP EBP
    RET
LABEL_34:

F2_G_F1_F2:
    PUSH EBP
    MOV EBP, ESP
LABEL_35:
  ; Suma INT 32 bits - Terceto 118
  MOV EAX, dword ptr V_B_G_F1_F2
  ADD EAX, dword ptr V_C2
  JO ErrorOverflowInt
  MOV dword ptr [V_A_35], EAX
LABEL_36:
    MOV EAX, dword ptr [V_A_35]
    MOV dword ptr [V_B_G_F1_F2], EAX
LABEL_37:
    invoke printf, cfm$("%d\n"), dword ptr [V_B_G_F1_F2]
LABEL_38:
  ; Suma INT 32 bits - Terceto 129
  MOV EAX, dword ptr V_C2
  ADD EAX, dword ptr V_B_G_F1_F2
  JO ErrorOverflowInt
  MOV dword ptr [V_A_38], EAX
LABEL_39:
    MOV EAX, dword ptr [V_A_38]
    MOV dword ptr [V_B_G_F1_F2], EAX
LABEL_40:
    MOV EAX, dword ptr [V_B_G_F1_F2]
    MOV ESP, EBP
    POP EBP
    RET
LABEL_41:
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