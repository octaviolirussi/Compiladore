.386
.model flat, stdcall
option casemap :none
include \masm32\include\windows.inc
include \masm32\include\kernel32.inc
includelib \masm32\lib\kernel32.lib
include \masm32\include\masm32.inc
includelib \masm32\lib\masm32.lib
include \masm32\include\masm32rt.inc

.data
DVC_MSG DB 'Error en tiempo de ejecución: División por Cero.', 0 ; STRING
OVF_INT_MSG DB 'Error en tiempo de ejecución: Overflow en suma de INT.', 0 ; STRING
OVF_FLOAT_MSG DB 'Error en tiempo de ejecución: Overflow en suma de FLOAT.', 0 ; STRING
V_2 DW 2 ; INT
V_O_G DW 0 ; INT
V_A_0 DW 0 ; INT
V_A_1 DW 0 ; INT
V_A_2 DW 0 ; INT
HELLO_MSG DB El programa se ejecuto correctamente., 0

.code

start:
T0:
T1:
    MOV AX, V_2
    MOV V_O_G, AX
T2:
fin:

    print ADDR HELLO_MSG

    invoke ExitProcess, 0
end start