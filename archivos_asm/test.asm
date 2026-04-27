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
MAX_FLOAT_HEX DD 7F7FFFFFh ; FLOAT_LIMIT
MIN_FLOAT_HEX DD 0FF7FFFFFh ; FLOAT_LIMIT
V_A_G DW 0 ; INT
V_B_G DW 0 ; INT
V_C_G DW 0 ; INT
V_X_G DD 0.0 ; FLOAT
V_Y_G DD 0.0 ; FLOAT
V_D_G DD 0.0 ; FLOAT
V_F_G DD 0.0 ; FLOAT
V_A_0 DW 0 ; INT
V_A_1 DW 0 ; INT
V_A_2 DW 0 ; INT
NEWLINE DB 13,10,0 ; STRING
HELLO_MSG DB "El programa se ejecuto correctamente.",0

.code
start:
LABEL_0:
LABEL_1:
    MOV AX, WORD PTR [V_A_G]
    MOVSX EAX, AX
    invoke printf, cfm$("%d\n"), EAX
LABEL_2:
    JMP fin

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