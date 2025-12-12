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
V_A_ DB "A:",0 ; STRING
V_C0 DD 0 ; INT
V_C1_0 DD 1.0 ; FLOAT
V_O_G DD 0 ; INT
V_K_G DD 0 ; INT
V_I_G DD 0.0 ; FLOAT
V_Z_G DD 0 ; INT
V_W_G DD 0.0 ; FLOAT
V_A_G DD 0.0 ; FLOAT
V_A_0 DD 0 ; INT
V_A_1 DD 0 ; INT
V_A_2 DD 0.0 ; FLOAT
V_A_3 DD 0 ; INT
V_A_4 DD 0.0 ; FLOAT
V_A_5 DD 0 ; INT
V_A_6 DD 0 ; INT
V_A_7 DD 0 ; INT
V_A_8 DD 0 ; INT
NEWLINE DB 13,10,0 ; STRING
V_TMP_DOUBLE DQ 0.0 ; FLOAT64
HELLO_MSG DB "El programa se ejecuto correctamente.",0

.code
start:
LABEL_0:
LABEL_1:
    MOV EAX, dword ptr [V_C0]
    MOV dword ptr [V_Z_G], EAX
LABEL_2:
  ; CONV_I_F (INT a FLOAT) - Terceto 5
  FILD dword ptr [V_Z_G]
  FSTP dword ptr [V_A_2]
LABEL_3:
    FLD dword ptr [V_A_2]
    FSTP dword ptr [V_W_G]
LABEL_4:
  ; Division FLOAT - Terceto 12
  FLD dword ptr [V_W_G]
  FTST
  FWAIT
  FSTSW AX
  SAHF
  JZ ErrorDVC
  FLD dword ptr [V_C1_0]
  FDIV dword ptr [V_W_G]
  FSTP dword ptr [V_A_4]
LABEL_5:
    FLD dword ptr [V_A_4]
    FSTP dword ptr [V_A_G]
LABEL_6:
    invoke printf, addr V_A_
    invoke printf, addr NEWLINE
LABEL_7:
    FLD dword ptr [V_A_G]
    FSTP qword ptr [V_TMP_DOUBLE]
    invoke printf, cfm$("%f\n"), [V_TMP_DOUBLE]
LABEL_8:
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