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
V_B DB "B",0 ; STRING
V_I_ DB "I:",0 ; STRING
V_K_ DB "K:",0 ; STRING
V_ESMAYOR DB "esMayor",0 ; STRING
V_ESMENOR DB "esMenor",0 ; STRING
V_HOLA DB "hola",0 ; STRING
V_C32767 DD 32767 ; INT
V_C25 DD 25 ; INT
V_C3 DD 3 ; INT
V_C2 DD 2 ; INT
V_C35 DD 35 ; INT
V_C1 DD 1 ; INT
V_O_G DD 0 ; INT
V_K_G DD 0 ; INT
V_I_G DD 0 ; INT
V_A_G DD 0 ; INT
V_B_G DD 0 ; INT
V_C_G DD 0 ; INT
V_D_G DD 0 ; INT
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
NEWLINE DB 13,10,0 ; STRING
HELLO_MSG DB "El programa se ejecuto correctamente.",0

.code
start:
LABEL_0:
LABEL_1:
  ; Multiplicacion INT 32 bits - Terceto 2
  MOV EAX, dword ptr [V_C32767]
  IMUL EAX, dword ptr [V_C32767]
  MOV dword ptr [V_A_1], EAX
LABEL_2:
    MOV EAX, dword ptr [V_A_1]
    MOV dword ptr [V_A_G], EAX
LABEL_3:
  ; Multiplicacion INT 32 bits - Terceto 10
  MOV EAX, dword ptr [V_A_G]
  IMUL EAX, dword ptr [V_C2]
  MOV dword ptr [V_A_3], EAX
LABEL_4:
    MOV EAX, dword ptr [V_A_3]
    MOV dword ptr [V_B_G], EAX
LABEL_5:
  ; Suma INT 32 bits - Terceto 18
  MOV EAX, dword ptr V_C_G
  ADD EAX, dword ptr V_C3
  JO ErrorOverflowInt
  MOV dword ptr [V_A_5], EAX
LABEL_6:
    MOV EAX, dword ptr [V_A_5]
    MOV dword ptr [V_D_G], EAX
LABEL_7:
    invoke printf, addr V_B
    invoke printf, addr NEWLINE
LABEL_8:
    invoke printf, cfm$("%d\n"), dword ptr [V_B_G]
LABEL_9:
    MOV EAX, dword ptr [V_C25]
    MOV dword ptr [V_I_G], EAX
LABEL_10:
  ; Suma INT 32 bits - Terceto 35
  MOV EAX, dword ptr V_C3
  ADD EAX, dword ptr V_C3
  JO ErrorOverflowInt
  MOV dword ptr [V_A_10], EAX
LABEL_11:
    MOV EAX, dword ptr [V_A_10]
    MOV dword ptr [V_O_G], EAX
LABEL_12:
  ; Suma INT 32 bits - Terceto 44
  MOV EAX, dword ptr V_C2
  ADD EAX, dword ptr V_O_G
  JO ErrorOverflowInt
  MOV dword ptr [V_A_12], EAX
LABEL_13:
    MOV EAX, dword ptr [V_A_12]
    MOV dword ptr [V_K_G], EAX
LABEL_14:
    invoke printf, addr V_I_
    invoke printf, addr NEWLINE
LABEL_15:
    invoke printf, cfm$("%d\n"), dword ptr [V_I_G]
LABEL_16:
    invoke printf, addr V_K_
    invoke printf, addr NEWLINE
LABEL_17:
    invoke printf, cfm$("%d\n"), dword ptr [V_K_G]
LABEL_18:
 ; Comparacion (>=) - Terceto 63
   MOV EAX, dword ptr [V_O_G]
   CMP EAX, dword ptr [V_K_G]
    SETGE AL
    MOVZX EAX, AL
    MOV dword ptr [V_A_18], EAX
LABEL_19:
    CMP dword ptr [V_A_18], 0
    JE LABEL_23
LABEL_20:
    invoke printf, addr V_ESMAYOR
    invoke printf, addr NEWLINE
LABEL_21:
    invoke printf, cfm$("%d\n"), dword ptr [V_O_G]
LABEL_22:
JMP LABEL_26
LABEL_23:
LABEL_24:
    invoke printf, addr V_ESMENOR
    invoke printf, addr NEWLINE
LABEL_25:
    invoke printf, cfm$("%d\n"), dword ptr [V_O_G]
LABEL_26:
LABEL_27:
LABEL_28:
 ; Comparacion (<) - Terceto 88
   MOV EAX, dword ptr [V_I_G]
   CMP EAX, dword ptr [V_C35]
    SETL AL
    MOVZX EAX, AL
    MOV dword ptr [V_A_28], EAX
LABEL_29:
    CMP dword ptr [V_A_28], 0
    JE LABEL_35
LABEL_30:
    invoke printf, cfm$("%d\n"), dword ptr [V_I_G]
LABEL_31:
    invoke printf, addr V_HOLA
    invoke printf, addr NEWLINE
LABEL_32:
  ; Suma INT 32 bits - Terceto 103
  MOV EAX, dword ptr V_I_G
  ADD EAX, dword ptr V_C1
  JO ErrorOverflowInt
  MOV dword ptr [V_A_32], EAX
LABEL_33:
    MOV EAX, dword ptr [V_A_32]
    MOV dword ptr [V_I_G], EAX
LABEL_34:
JMP LABEL_27
LABEL_35:
LABEL_36:
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