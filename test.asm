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
V_O_ DB "O:",0 ; STRING
V_K_ DB "K:",0 ; STRING
V_ESMAYOR DB "esMayor",0 ; STRING
V_ESMENOR DB "esMenor",0 ; STRING
V_0 DD 0 ; INT
V_3 DD 3 ; INT
V_2 DD 2 ; INT
V_1 DD 1 ; INT
V_O_G DD 0 ; INT
V_K_G DD 0 ; INT
V_I_G DD 0 ; INT
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
NEWLINE DB 13,10,0 ; STRING
HELLO_MSG DB "El programa se ejecuto correctamente.",0

.code
start:
LABEL_0:
LABEL_1:
    MOV EAX, dword ptr [V_0]
    MOV dword ptr [V_I_G], EAX
LABEL_2:
  ; Suma INT 32 bits - Terceto 5
  MOV EAX, dword ptr [V_3]
  ADD EAX, dword ptr [V_3]
  JO ErrorOverflowInt
  MOV dword ptr [V_A_2], EAX
LABEL_3:
    MOV EAX, dword ptr [V_A_2]
    MOV dword ptr [V_O_G], EAX
LABEL_4:
  ; Suma INT 32 bits - Terceto 14
  MOV EAX, dword ptr [V_2]
  ADD EAX, dword ptr [V_O_G]
  JO ErrorOverflowInt
  MOV dword ptr [V_A_4], EAX
LABEL_5:
    MOV EAX, dword ptr [V_A_4]
    MOV dword ptr [V_K_G], EAX
LABEL_6:
    invoke printf, addr V_O_
    invoke printf, addr NEWLINE
LABEL_7:
    invoke printf, cfm$("%d\n"), dword ptr [V_O_G]
LABEL_8:
    invoke printf, addr V_K_
    invoke printf, addr NEWLINE
LABEL_9:
    invoke printf, cfm$("%d\n"), dword ptr [V_K_G]
LABEL_10:
 ; Comparación (>=) - Terceto 33
   MOV EAX, dword ptr [V_O_G]
   CMP EAX, dword ptr [V_K_G]
    SETGE AL
    MOVZX EAX, AL
    MOV dword ptr [V_A_10], EAX
LABEL_11:
    CMP dword ptr [V_A_10], 0
    JE LABEL_15
LABEL_12:
    invoke printf, addr V_ESMAYOR
    invoke printf, addr NEWLINE
LABEL_13:
    invoke printf, cfm$("%d\n"), dword ptr [V_O_G]
LABEL_14:
JMP LABEL_18
LABEL_15:
LABEL_16:
    invoke printf, addr V_ESMENOR
    invoke printf, addr NEWLINE
LABEL_17:
    invoke printf, cfm$("%d\n"), dword ptr [V_O_G]
LABEL_18:
LABEL_19:
LABEL_20:
 ; Comparación (<) - Terceto 58
   MOV EAX, dword ptr [V_I_G]
   CMP EAX, dword ptr [V_2]
    SETL AL
    MOVZX EAX, AL
    MOV dword ptr [V_A_20], EAX
LABEL_21:
    CMP dword ptr [V_A_20], 0
    JE LABEL_26
LABEL_22:
    invoke printf, cfm$("%d\n"), dword ptr [V_I_G]
LABEL_23:
  ; Suma INT 32 bits - Terceto 70
  MOV EAX, dword ptr [V_I_G]
  ADD EAX, dword ptr [V_1]
  JO ErrorOverflowInt
  MOV dword ptr [V_A_23], EAX
LABEL_24:
    MOV EAX, dword ptr [V_A_23]
    MOV dword ptr [V_I_G], EAX
LABEL_25:
JMP LABEL_19
LABEL_26:
LABEL_27:
    jmp fin

; ----- HANDLERS DE ERROR -----
ErrorOverflowInt:
    print "Error en tiempo de ejecución: Overflow en INT"
    invoke ExitProcess, 1
ErrorOverflowFloat:
    print "Error en tiempo de ejecución: Overflow en FLOAT"
    invoke ExitProcess, 1
ErrorDVC:
    print "Error en tiempo de ejecución: División por Cero"
    invoke ExitProcess, 1

fin:
    print ADDR HELLO_MSG
    invoke ExitProcess, 0
end start