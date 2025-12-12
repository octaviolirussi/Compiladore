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
V_ADIOS DB "Adios",0 ; STRING
V_HOLA DB "Hola",0 ; STRING
V_C1_234 DD 1.234 ; FLOAT
V_C5 DD 5 ; INT
V_C2 DD 2 ; INT
V_C0 DD 0 ; INT
V_C2_2 DD 2.2 ; FLOAT
V_C10 DD 10 ; INT
V_D_G_F2_F3 DD 0.0 ; FLOAT
V_J_G_F2 DD 0 ; INT
V_B_G_F2 DD 0 ; INT
V_O_G DD 0.0 ; FLOAT
V_Y_G DD 0 ; INT
V_L1_G_F2 DD 0.0 ; FLOAT
V_Y_G_F2_F3 DD 0 ; INT
V_A_G_F2_F3 DD 0.0 ; FLOAT
V_A_0 DD 0 ; INT
V_A_1 DD 0 ; INT
V_A_2 DD 0 ; INT
V_A_3 DD 0 ; INT
V_A_4 DD 0 ; INT
V_A_5 DD 0 ; INT
V_A_6 DD 0.0 ; FLOAT
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
V_A_17 DD 0.0 ; FLOAT
V_A_18 DD 0.0 ; FLOAT
V_A_19 DD 0 ; INT
V_A_20 DD 0.0 ; FLOAT
V_A_21 DD 0.0 ; FLOAT
V_A_22 DD 0 ; INT
V_A_23 DD 0.0 ; FLOAT
V_A_24 DD 0 ; INT
V_A_25 DD 0 ; INT
V_A_26 DD 0 ; INT
V_A_27 DD 0 ; INT
V_A_28 DD 0.0 ; FLOAT
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
V_A_42 DD 0 ; INT
NEWLINE DB 13,10,0 ; STRING
V_TMP_DOUBLE DQ 0.0 ; FLOAT64
HELLO_MSG DB "El programa se ejecuto correctamente.",0

.code
start:
LABEL_0:
LABEL_1:
  ; Suma INT 32 bits - Terceto 2
  MOV EAX, dword ptr V_C2
  ADD EAX, dword ptr V_C2
  JO ErrorOverflowInt
  MOV dword ptr [V_A_1], EAX
LABEL_2:
    MOV EAX, dword ptr [V_A_1]
    MOV dword ptr [V_Y_G], EAX
LABEL_3:
LABEL_4:

F2_G_F2:
    PUSH EBP
    MOV EBP, ESP
LABEL_5:
  ; Suma INT 32 bits - Terceto 17
  MOV EAX, dword ptr V_C2
  ADD EAX, dword ptr V_C0
  JO ErrorOverflowInt
  MOV dword ptr [V_A_5], EAX
LABEL_6:
  ; CONV_I_F (INT a FLOAT) - Terceto 23
  FILD dword ptr [V_A_5]
  FSTP dword ptr [V_A_6]
LABEL_7:
    FLD dword ptr [V_A_6]
    FSTP dword ptr [V_L1_G_F2]
LABEL_8:
    FLD dword ptr [V_O_G]
    FSTP dword ptr [V_D_G_F2_F3]
LABEL_9:
    CALL F3_G_F2_F3
    MOV dword ptr [V_A_9], EAX
LABEL_10:
    FLD dword ptr [V_D_G_F2_F3]
    FSTP dword ptr [V_O_G]
LABEL_11:
    MOV EAX, dword ptr [V_A_9]
    MOV dword ptr [V_J_G_F2], EAX
LABEL_12:
    invoke printf, cfm$("%d\n"), dword ptr [V_J_G_F2]
LABEL_13:
    MOV EAX, dword ptr [V_B_G_F2]
    MOV ESP, EBP
    POP EBP
    RET
LABEL_14:
    MOV ESP, EBP
    POP EBP
    RET
LABEL_15:

F3_G_F2_F3:
    PUSH EBP
    MOV EBP, ESP
LABEL_16:
    FLD dword ptr [V_C5]
    FSTP dword ptr [V_D_G_F2_F3]
LABEL_17:
  ; CONV_I_F (INT a FLOAT) - Terceto 61
  FILD dword ptr [V_C2]
  FSTP dword ptr [V_A_17]
LABEL_18:
  ; Suma FLOAT - Deteccion por Valor INF
  FLD dword ptr [V_A_17]
  FADD dword ptr [V_L1_G_F2]
  FSTP dword ptr [V_A_18]
  ; Suma FLOAT - Deteccion de Underflow y Overflow (Bandera)
  FLD dword ptr [V_A_17]
  FADD dword ptr [V_L1_G_F2]
  FSTSW AX
  FWAIT
  TEST AX, 0008h
  JNZ ErrorOverflowFloat
  FSTP dword ptr [V_A_18]
LABEL_19:
    FLD dword ptr [V_A_18]
    FSTP dword ptr [V_A_G_F2_F3]
LABEL_20:
  ; CONV_I_F (INT a FLOAT) - Terceto 81
  FILD dword ptr [V_C5]
  FSTP dword ptr [V_A_20]
LABEL_21:
  ; Suma FLOAT - Deteccion por Valor INF
  FLD dword ptr [V_C1_234]
  FADD dword ptr [V_A_20]
  FSTP dword ptr [V_A_21]
  ; Suma FLOAT - Deteccion de Underflow y Overflow (Bandera)
  FLD dword ptr [V_C1_234]
  FADD dword ptr [V_A_20]
  FSTSW AX
  FWAIT
  TEST AX, 0008h
  JNZ ErrorOverflowFloat
  FSTP dword ptr [V_A_21]
LABEL_22:
    FLD dword ptr [V_A_21]
    FSTP dword ptr [V_L1_G_F2]
LABEL_23:
  ; CONV_I_F (INT a FLOAT) - Terceto 101
  FILD dword ptr [V_C2]
  FSTP dword ptr [V_A_23]
LABEL_24:
 ; Comparacion (>) - Terceto 105
   MOV EAX, dword ptr [V_A_G_F2_F3]
   CMP EAX, dword ptr [V_A_23]
    SETG AL
    MOVZX EAX, AL
    MOV dword ptr [V_A_24], EAX
LABEL_25:
    CMP dword ptr [V_A_24], 0
    JE LABEL_33
LABEL_26:
    FLD dword ptr [V_A_G_F2_F3]
    FSTP qword ptr [V_TMP_DOUBLE]
    invoke printf, cfm$("%f\n"), [V_TMP_DOUBLE]
LABEL_27:
  ; Suma INT 32 bits - Terceto 119
  MOV EAX, dword ptr V_C2
  ADD EAX, dword ptr V_C2
  JO ErrorOverflowInt
  MOV dword ptr [V_A_27], EAX
LABEL_28:
  ; CONV_I_F (INT a FLOAT) - Terceto 125
  FILD dword ptr [V_A_27]
  FSTP dword ptr [V_A_28]
LABEL_29:
    FLD dword ptr [V_A_28]
    FSTP dword ptr [V_A_G_F2_F3]
LABEL_30:
    FLD dword ptr [V_A_G_F2_F3]
    FSTP qword ptr [V_TMP_DOUBLE]
    invoke printf, cfm$("%f\n"), [V_TMP_DOUBLE]
LABEL_31:
    invoke printf, addr V_ADIOS
    invoke printf, addr NEWLINE
LABEL_32:
JMP LABEL_38
LABEL_33:
LABEL_34:
    MOV EAX, dword ptr [V_C2]
    MOV dword ptr [V_Y_G_F2_F3], EAX
LABEL_35:
  ; Suma INT 32 bits - Terceto 145
  MOV EAX, dword ptr V_C2
  ADD EAX, dword ptr V_C0
  JO ErrorOverflowInt
  MOV dword ptr [V_A_35], EAX
LABEL_36:
    MOV EAX, dword ptr [V_A_35]
    MOV dword ptr [V_Y_G_F2_F3], EAX
LABEL_37:
    invoke printf, cfm$("%d\n"), dword ptr [V_Y_G_F2_F3]
LABEL_38:
LABEL_39:
    FLD dword ptr [V_C2_2]
    FSTP dword ptr [V_L1_G_F2]
LABEL_40:
    invoke printf, addr V_HOLA
    invoke printf, addr NEWLINE
LABEL_41:
    MOV EAX, dword ptr [V_C10]
    MOV ESP, EBP
    POP EBP
    RET
LABEL_42:
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