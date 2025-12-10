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
V_C3 DD 3 ; INT
V_C1_5 DD 1.5 ; FLOAT
V_C2_EP1 DD 2.e+1 ; FLOAT
V_C0 DD 0 ; INT
V_A_G_F1 DD 0 ; INT
V_C6 DD 6 ; INT
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
V_A_13 DD 0 ; INT
V_A_14 DD 0 ; INT
V_A_15 DD 0 ; INT
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
    MOV EAX, dword ptr [V_C6]
    MOV dword ptr [V_A_G_F1], EAX
LABEL_6:
    CALL F1_G_F1
    MOV dword ptr [V_A_6], EAX
LABEL_7:
  ; Suma INT 32 bits - Terceto 20
  MOV EAX, dword ptr V_A_6
  ADD EAX, dword ptr V_C2
  JO ErrorOverflowInt
  MOV dword ptr [V_A_7], EAX
LABEL_8:
    MOV EAX, dword ptr [V_A_7]
    MOV dword ptr [V_B_G], EAX
LABEL_9:
    invoke printf, cfm$("%d\n"), dword ptr [V_B_G]
LABEL_10:
LABEL_11:

F1_G_F1:
    PUSH EBP
    MOV EBP, ESP
    ; --- espacio para variables  ---
LABEL_12:
  ; Suma INT 32 bits - Terceto 38
  MOV EAX, dword ptr V_C2
  ADD EAX, dword ptr V_A_G_F1
  JO ErrorOverflowInt
  MOV dword ptr [V_A_12], EAX
LABEL_13:
    MOV EAX, dword ptr [V_A_12]
    MOV dword ptr [V_A_G_F1], EAX
LABEL_14:
    MOV EAX, dword ptr [V_C0]
    MOV ESP, EBP
    POP EBP
    RET
LABEL_15:
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