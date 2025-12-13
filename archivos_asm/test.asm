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
V_C1 DB "1",0 ; STRING
V_N3 DW -3 ; INT
V_C1_5 DD 1.5 ; FLOAT
V_C2_EP1 DD 2.e+1 ; FLOAT
V_C2_1 DD 2.1 ; FLOAT
V_C3_0 DD 3.0 ; FLOAT
V_C3 DW 3 ; INT
V_C3_1 DD 3.1 ; FLOAT
V_C2 DW 2 ; INT
V_C0 DW 0 ; INT
V_A_G DW 0 ; INT
V_B_G DW 0 ; INT
V_C_G DW 0 ; INT
V_X_G DD 0.0 ; FLOAT
V_Y_G DD 0.0 ; FLOAT
V_A_0 DW 0 ; INT
V_A_1 DW 0 ; INT
V_A_2 DW 0 ; INT
V_A_3 DW 0 ; INT
V_A_4 DW 0 ; INT
V_A_5 DD 0.0 ; FLOAT
V_A_6 DW 0 ; INT
V_A_7 DW 0 ; INT
V_A_8 DW 0 ; INT
V_A_9 DD 0.0 ; FLOAT
V_A_10 DD 0.0 ; FLOAT
V_A_11 DW 0 ; INT
V_A_12 DW 0 ; INT
V_A_13 DD 0.0 ; FLOAT
V_A_14 DW 0 ; INT
V_A_15 DW 0 ; INT
NEWLINE DB 13,10,0 ; STRING
HELLO_MSG DB "El programa se ejecuto correctamente.",0

.code
start:
LABEL_0:
LABEL_1:
    MOV AX, WORD PTR [V_C2]
    MOV WORD PTR [V_A_G], AX
LABEL_2:
    MOV AX, WORD PTR [V_N3]
    MOV WORD PTR [V_B_G], AX
LABEL_3:
    FLD dword ptr [V_C1_5]
    FSTP dword ptr [V_X_G]
LABEL_4:
    FLD dword ptr [V_C2_EP1]
    FSTP dword ptr [V_Y_G]
LABEL_5:
 ; Comparacion (<)
   FLD dword ptr [V_C3_0]
   FLD dword ptr [V_C2_1]
   FCOMPP
   FSTSW AX
   SAHF
   SETB AL
   MOVZX EAX, AL
   MOV word ptr [V_A_5], AX
LABEL_6:
    CMP dword ptr [V_A_5], 0
    JE LABEL_8
LABEL_7:
    invoke printf, addr V_C1
    invoke printf, addr NEWLINE
LABEL_8:
LABEL_9:
  ; CONV_I_F (INT 16 → FLOAT 32)
  FILD WORD PTR [V_C3]
  FSTP DWORD PTR [V_A_9]
LABEL_10:
  ; Suma FLOAT - Deteccion por Valor INF
  FLD dword ptr [V_A_9]
  FADD dword ptr [V_C3_1]
  FSTP dword ptr [V_A_10]
  ; Suma FLOAT - Deteccion de Underflow y Overflow (Bandera)
  FLD dword ptr [V_A_9]
  FADD dword ptr [V_C3_1]
  FSTSW AX
  FWAIT
  TEST AX, 0008h
  JNZ ErrorOverflowFloat
  FSTP dword ptr [V_A_10]
LABEL_11:
    FLD dword ptr [V_A_10]
    FSTP dword ptr [V_X_G]
LABEL_12:
  ; Division INT 16 bits - Terceto 51
  MOV CX, WORD PTR [V_C0]
  CMP CX, 0
  JE ErrorDVC
  MOV AX, WORD PTR [V_C2]
  CWD
  IDIV CX
  MOV WORD PTR [V_A_12], AX
LABEL_13:
  ; CONV_I_F (INT 16 → FLOAT 32)
  FILD WORD PTR [V_A_12]
  FSTP DWORD PTR [V_A_13]
LABEL_14:
    FLD dword ptr [V_A_13]
    FSTP dword ptr [V_X_G]
LABEL_15:
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