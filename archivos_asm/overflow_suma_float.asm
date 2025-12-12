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
V_N_ DB "N:",0 ; STRING
V_C_ DB "C:",0 ; STRING
V_HOLA DB "hola",0 ; STRING
V_C25 DD 25 ; INT
V_C3 DD 3 ; INT
V_C2 DD 2 ; INT
V_C3_40282347EP38 DD 3.40282347e+38 ; FLOAT
V_C0_0 DD 0.0 ; FLOAT
V_C35 DD 35 ; INT
V_C1 DD 1 ; INT
V_O_G DD 0 ; INT
V_K_G DD 0 ; INT
V_I_G DD 0.0 ; FLOAT
V_B_G DD 0.0 ; FLOAT
V_N_G DD 0.0 ; FLOAT
V_C_G DD 0.0 ; FLOAT
V_A_0 DD 0 ; INT
V_A_1 DD 0.0 ; FLOAT
V_A_2 DD 0 ; INT
V_A_3 DD 0 ; INT
V_A_4 DD 0 ; INT
V_A_5 DD 0 ; INT
V_A_6 DD 0 ; INT
V_A_7 DD 0 ; INT
V_A_8 DD 0.0 ; FLOAT
V_A_9 DD 0 ; INT
V_A_10 DD 0.0 ; FLOAT
V_A_11 DD 0 ; INT
V_A_12 DD 0 ; INT
V_A_13 DD 0 ; INT
V_A_14 DD 0 ; INT
V_A_15 DD 0 ; INT
V_A_16 DD 0 ; INT
V_A_17 DD 0.0 ; FLOAT
V_A_18 DD 0 ; INT
V_A_19 DD 0 ; INT
V_A_20 DD 0 ; INT
V_A_21 DD 0 ; INT
V_A_22 DD 0.0 ; FLOAT
V_A_23 DD 0.0 ; FLOAT
V_A_24 DD 0 ; INT
V_A_25 DD 0 ; INT
V_A_26 DD 0 ; INT
V_A_27 DD 0 ; INT
NEWLINE DB 13,10,0 ; STRING
V_TMP_DOUBLE DQ 0.0 ; FLOAT64
HELLO_MSG DB "El programa se ejecuto correctamente.",0

.code
start:
LABEL_0:
LABEL_1:
  ; CONV_I_F (INT a FLOAT) - Terceto 2
  FILD dword ptr [V_C25]
  FSTP dword ptr [V_A_1]
LABEL_2:
    FLD dword ptr [V_A_1]
    FSTP dword ptr [V_I_G]
LABEL_3:
  ; Suma INT 32 bits - Terceto 9
  MOV EAX, dword ptr V_C3
  ADD EAX, dword ptr V_C3
  JO ErrorOverflowInt
  MOV dword ptr [V_A_3], EAX
LABEL_4:
    MOV EAX, dword ptr [V_A_3]
    MOV dword ptr [V_O_G], EAX
LABEL_5:
  ; Suma INT 32 bits - Terceto 18
  MOV EAX, dword ptr V_C2
  ADD EAX, dword ptr V_O_G
  JO ErrorOverflowInt
  MOV dword ptr [V_A_5], EAX
LABEL_6:
    MOV EAX, dword ptr [V_A_5]
    MOV dword ptr [V_K_G], EAX
LABEL_7:
    FLD dword ptr [V_C3_40282347EP38]
    FSTP dword ptr [V_B_G]
LABEL_8:
  ; Resta FLOAT - Terceto 30
  FLD dword ptr [V_C0_0]
  FSUB dword ptr [V_B_G]
  FSTSW AX
  FWAIT
  TEST AX, 0004h
  FSTP dword ptr [V_A_8]
LABEL_9:
    FLD dword ptr [V_A_8]
    FSTP dword ptr [V_N_G]
LABEL_10:
  ; Suma FLOAT - Deteccion por Valor INF
  FLD dword ptr [V_N_G]
  FADD dword ptr [V_N_G]
  FSTP dword ptr [V_A_10]
  ; Suma FLOAT - Deteccion de Underflow y Overflow (Bandera)
  FLD dword ptr [V_N_G]
  FADD dword ptr [V_N_G]
  FSTSW AX
  FWAIT
  TEST AX, 0008h
  JNZ ErrorOverflowFloat
  FSTP dword ptr [V_A_10]
LABEL_11:
    FLD dword ptr [V_A_10]
    FSTP dword ptr [V_C_G]
LABEL_12:
    invoke printf, addr V_N_
    invoke printf, addr NEWLINE
LABEL_13:
    FLD dword ptr [V_N_G]
    FSTP qword ptr [V_TMP_DOUBLE]
    invoke printf, cfm$("%f\n"), [V_TMP_DOUBLE]
LABEL_14:
    invoke printf, addr V_C_
    invoke printf, addr NEWLINE
LABEL_15:
    FLD dword ptr [V_C_G]
    FSTP qword ptr [V_TMP_DOUBLE]
    invoke printf, cfm$("%f\n"), [V_TMP_DOUBLE]
LABEL_16:
LABEL_17:
  ; CONV_I_F (INT a FLOAT) - Terceto 72
  FILD dword ptr [V_C35]
  FSTP dword ptr [V_A_17]
LABEL_18:
 ; Comparacion (<) - Terceto 76
   MOV EAX, dword ptr [V_I_G]
   CMP EAX, dword ptr [V_A_17]
    SETL AL
    MOVZX EAX, AL
    MOV dword ptr [V_A_18], EAX
LABEL_19:
    CMP dword ptr [V_A_18], 0
    JE LABEL_26
LABEL_20:
    FLD dword ptr [V_I_G]
    FSTP qword ptr [V_TMP_DOUBLE]
    invoke printf, cfm$("%f\n"), [V_TMP_DOUBLE]
LABEL_21:
    invoke printf, addr V_HOLA
    invoke printf, addr NEWLINE
LABEL_22:
  ; CONV_I_F (INT a FLOAT) - Terceto 93
  FILD dword ptr [V_C1]
  FSTP dword ptr [V_A_22]
LABEL_23:
  ; Suma FLOAT - Deteccion por Valor INF
  FLD dword ptr [V_I_G]
  FADD dword ptr [V_A_22]
  FSTP dword ptr [V_A_23]
  ; Suma FLOAT - Deteccion de Underflow y Overflow (Bandera)
  FLD dword ptr [V_I_G]
  FADD dword ptr [V_A_22]
  FSTSW AX
  FWAIT
  TEST AX, 0008h
  JNZ ErrorOverflowFloat
  FSTP dword ptr [V_A_23]
LABEL_24:
    FLD dword ptr [V_A_23]
    FSTP dword ptr [V_I_G]
LABEL_25:
JMP LABEL_16
LABEL_26:
LABEL_27:
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