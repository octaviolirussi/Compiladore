import copy
from tablaSimbolos import SymbolTable
from tercetos import GeneradorTercetos
from errorManager import ErrorManager


# Asume que ErrorManager están importados o accesibles

class CodeGenerator:
    """Genera código Assembler para Pentium de 32 bits (NASM) a partir de los tercetos."""
    
    def __init__(self, symbol_table, terceto_generator, error_manager):
        self.ts = symbol_table
        self.tercetos = terceto_generator.tercetos
        self.error_manager = error_manager
        self.asm_code = []          # Lista para almacenar el código del segmento .code
        self.data_section = {}      # Diccionario: {etiqueta_asm: definicion_asm} para el segmento .data
        self.next_temp_id = 0       # Contador para generar nombres de temporales (T0, T1, ...)
        self.mem_map = {}           # Mapeo de (Lexema:Scope o [T#]) -> Etiqueta ASM
        self.temp_vars_created = set() # Variables temporales ASM ya definidas
        self.runtime_labels = {}    # Etiquetas de rutinas de error (Ej: DVC, Overflow)

    # ----------------------------------------------------------------------
    # 1. PREPARACIÓN DE LA SECCIÓN DE DATOS (.data)
    # ----------------------------------------------------------------------

    def _get_unique_asm_label(self, original_key, type_suffix=None):
        """Genera y mapea una etiqueta ASM única para un lexema/temporal."""
        if original_key in self.mem_map:
            return self.mem_map[original_key]
        
        # Detectar si la clave es una REFERENCIA DE TERCETO (ej: '[1]', '[20]')
        if isinstance(original_key, str) and original_key.startswith('[') and original_key.endswith(']'):
            # Usar V_A_ para Variables Auxiliares (Temporales)
            label_base = original_key.strip('[]')
            label = f"V_A_{label_base}" 
            
        else:
            # Generar nombre para VARIABLES DE USUARIO (ej: 'O:G', '2', '"hola"')
            # Generar nombre de etiqueta basado en la clave original
            # Reemplazar caracteres no válidos con '_'
            label_base = str(original_key).replace(':', '_').replace('[', 'T_').replace(']', '').replace('.', '_').replace('"', '')
            label = f"V_{label_base.upper()}"
            
        # Si ya existe, añadir un sufijo numérico para garantizar unicidad
        if label in self.data_section:
            label = f"{label}_{len(self.data_section)}"
            
        self.mem_map[original_key] = label
        return label

    def prepare_asm_data(self):
        """Define todas las variables, constantes y mensajes de error en .data."""
        
        # 1. Definir los mensajes de error de Runtime (Grupo 1)
        self.runtime_labels["DVC"] = self._add_data_entry("DVC_MSG", "DB", "'Error en tiempo de ejecución: División por Cero.', 0", "STRING")
        self.runtime_labels["OVF_INT"] = self._add_data_entry("OVF_INT_MSG", "DB", "'Error en tiempo de ejecución: Overflow en suma de INT.', 0", "STRING")
        self.runtime_labels["OVF_FLOAT"] = self._add_data_entry("OVF_FLOAT_MSG", "DB", "'Error en tiempo de ejecución: Overflow en suma de FLOAT.', 0", "STRING")

        # 2. Definir constantes, variables y parámetros
        for entry in self.ts.symbols.values():
            lexema_scope = entry.get("Lexema")
            uso = entry.get("Uso").upper()
            data_type = entry.get("data_type").upper() if entry.get("data_type") else "N/A"
            
            if uso in ["CONSTANTE", "VARIABLE", "PARAMETRO"]:
                asm_label = self._get_unique_asm_label(lexema_scope)
                
                # Definición por tipo
                if data_type == "INT":
                    initial_value = entry["Lexema"] if uso == "CONSTANTE" else "0"
                    self._add_data_entry(asm_label, "DW", initial_value, data_type) # DW = 16 bits (INT)
                elif data_type == "FLOAT":
                    initial_value = entry["Lexema"] if uso == "CONSTANTE" else "0.0"
                    self._add_data_entry(asm_label, "DD", initial_value, data_type) # DD = 32 bits (FLOAT)
                elif data_type == "STRING":
                    value = entry["Lexema"] 
                    self._add_data_entry(asm_label, "DB", f"{value}, 0", data_type) # DB = string con terminador 0
                    
        # 3. Definir temporales de tercetos ([T#]) que no estén ya mapeados
        for i in range(len(self.tercetos)):
            terceto = self.tercetos[i]
            terceto_ref = f"[{i}]"
            
            if terceto_ref not in self.mem_map:
                result_type = terceto.result_type.upper() if terceto.result_type else "INT" # Por defecto INT
                asm_label = self._get_unique_asm_label(terceto_ref)
                
                if result_type == "INT":
                    self._add_data_entry(asm_label, "DW", "0", result_type)
                elif result_type == "FLOAT":
                    self._add_data_entry(asm_label, "DD", "0.0", result_type)

    def _add_data_entry(self, label, directive, value, data_type):
        """Añade una entrada a la sección de datos, evitando duplicados."""
        if label not in self.data_section:
            self.data_section[label] = (directive, value, data_type)
        return label

    # ----------------------------------------------------------------------
    # 2. TRADUCCIÓN DE TERCETOS A ENSAMBLADOR (.code)
    # ----------------------------------------------------------------------

    def translate_terceto(self, index, t):
        """Traduce un terceto específico a código ASM, añadiéndolo a self.asm_code."""
        
        # Etiqueta de inicio del terceto (para saltos, BI, BF)
        self.asm_code.append(f"T{index}:") 
        
        # Obtener las etiquetas ASM de los operandos (variables/constantes/temporales)
        op1_asm = self.get_op_asm_label(t.op1)
        op2_asm = self.get_op_asm_label(t.op2)
        res_asm = self._get_unique_asm_label(f"[{index}]") # Etiqueta donde se almacena el resultado

        # Manejo de operadores
        if t.operador == '+':
            self.generate_addition(res_asm, op1_asm, op2_asm, t.result_type)
        elif t.operador == '*':
            self.generate_multiplication(res_asm, op1_asm, op2_asm, t.result_type)
        elif t.operador == '-':
            self.generate_subtraction(res_asm, op1_asm, op2_asm, t.result_type)
        elif t.operador == '/':
            self.generate_division(res_asm, op1_asm, op2_asm, t.result_type)
        elif t.operador == 'PRINT':
            self.generate_print(t.op1)
        elif t.operador == 'CONV_I_F':
            self.generate_conv_if(res_asm, op1_asm)
        elif t.operador == '=': # Asignación
            self.generate_assignment(op1_asm, op2_asm, t.op1, t.op2, t.result_type)        
        elif t.operador in ('<', '>', '==', '!=', '>=', '<='):
            self.generate_comparison(res_asm, op1_asm, op2_asm, t.operador, t.result_type)        
        elif t.operador == 'BI':
            self.asm_code.append(f"JMP T{t.op1.strip('[]')}")
        elif t.operador == 'BF': # Se asume que t.op1 es el resultado de una comparación booleana [T#]
            self.asm_code.append(f"CMP word {op1_asm}, 0") 
            self.asm_code.append(f"JE T{t.op2.strip('[]')}") # Salto si la condición es Falsa (0)
        # TODO... (Agregar lógica para el resto de operadores: *, -, >, <, funciones, etc.)

    def get_op_asm_label(self, op):
        """Devuelve la etiqueta ASM para un operando (lexema o referencia de terceto [N])."""
        if op is None:
            return None
        # Si es una referencia de terceto [N]
        if isinstance(op, str) and op.startswith('[') and op.endswith(']'):
            return self.mem_map.get(op)
        # Si es una variable/constante/parámetro
        return self.mem_map.get(op)

    ## Chequeos de Runtime

    def generate_division(self, res_asm, op1_asm, op2_asm, result_type):
        """Genera código para la división, incluyendo el chequeo de División por Cero."""
        
        if result_type.upper() == 'INT':
            # Chequeo División por Cero (INT)
            self.asm_code.append(f"  ; Chequeo División por Cero (INT) - Terceto {len(self.asm_code)}")
            self.asm_code.append(f"  MOV EAX, [{op2_asm}]")
            self.asm_code.append(f"  CMP EAX, 0")
            self.asm_code.append(f"  JE .ErrorDVC")
            
            # Operación de División (IDIV)
            self.asm_code.append(f"  MOV AX, word [{op1_asm}]")
            self.asm_code.append(f"  IDIV word [{op2_asm}] ; AX = AX / Divisor")
            self.asm_code.append(f"  MOV word [{res_asm}], AX")
            
        elif result_type.upper() == 'FLOAT':
            # Chequeo División por Cero (FLOAT)
            self.asm_code.append(f"  ; Chequeo División por Cero (FLOAT) - Terceto {len(self.asm_code)}")
            self.asm_code.append(f"  FLD dword ptr [{op2_asm}]")
            self.asm_code.append(f"  FTST")
            self.asm_code.append(f"  FWAIT")
            self.asm_code.append(f"  FSTSW AX")
            self.asm_code.append(f"  SAHF")
            self.asm_code.append(f"  JZ .ErrorDVC") # Salta si el divisor es 0.0
            
            # Operación de División (FDIV)
            self.asm_code.append(f"    FLD dword ptr [{op1_asm}]")
            self.asm_code.append(f"    FDIV dword ptr [{op2_asm}]") 
            self.asm_code.append(f"    FSTP dword ptr [{res_asm}]")

    def generate_addition(self, res_asm, op1_asm, op2_asm, result_type):
        """Genera código para la suma, incluyendo el chequeo de Overflow en Sumas."""
        
        if result_type.upper() == 'INT':
            self.asm_code.append(f"  ; Chequeo Overflow Suma (INT) - Terceto {len(self.asm_code)}")
            self.asm_code.append(f"  MOV EAX, 0") # Limpiar EAX para la operación de 16 bits
            self.asm_code.append(f"  MOV AX, dword ptr [{op1_asm}]")
            self.asm_code.append(f"  ADD AX, dword ptr [{op2_asm}]")
            self.asm_code.append(f"  JO .ErrorOverflowInt") # JO (Jump on Overflow)
            self.asm_code.append(f"  MOV dword ptr [{res_asm}], AX")
            
        elif result_type.upper() == 'FLOAT':
            self.asm_code.append(f"  ; Chequeo Overflow Suma (FLOAT) - Terceto {len(self.asm_code)}")
            self.asm_code.append(f"  FLD dword [{op1_asm}]")
            self.asm_code.append(f"  FADD dword [{op2_asm}]")
            
            # Chequeo de Overflow FPU (bit OE en la palabra de estado)
            self.asm_code.append(f"  FSTSW AX")
            self.asm_code.append(f"  FWAIT")
            self.asm_code.append(f"  TEST AX, 0004h") # Comprueba bit OE (0004h = 4 en hex)
            self.asm_code.append(f"  JNZ .ErrorOverflowFloat")
            
            self.asm_code.append(f"  FSTP dword [{res_asm}]")
    def generate_subtraction(self, res_asm, op1_asm, op2_asm, result_type):
        if result_type.upper() == 'INT':
            # Chequeo Overflow Resta (INT)
            self.asm_code.append(f"    MOV AX, word [{op1_asm}]")
            self.asm_code.append(f"    SUB AX, word [{op2_asm}]")
            self.asm_code.append(f"    JO .ErrorOverflowInt") # JO (Jump on Overflow) funciona para SUB/ADD
            self.asm_code.append(f"    MOV word [{res_asm}], AX")
        elif result_type.upper() == 'FLOAT':
            # Resta FLOAT (FSUB)
            self.asm_code.append(f"    FLD dword [{op1_asm}]")
            self.asm_code.append(f"    FSUB dword [{op2_asm}]")
            # Aquí también deberías chequear Overflow de FPU (como en la suma)
            self.asm_code.append(f"    FSTP dword [{res_asm}]")

    ## Conversiones Implícitas (CONV_I_F)
    def generate_conv_if(self, res_asm, op1_asm):
        # Esto genera una línea sin indentación inicial, solo con ';'
        self.asm_code.append(f"; CONV_I_F (INT a FLOAT) - Terceto {len(self.asm_code)}")
        # Esto genera una línea con 4 espacios y un tabulador (o múltiples espacios)
        self.asm_code.append(f"    FILD word [{op1_asm}]")
        self.asm_code.append(f"    FSTP dword ptr [{res_asm}]")

    ## Asignación
    def generate_assignment(self, dest_asm, src_asm, dest_op, src_op, result_type):
        entry = self.ts.get_token(dest_op, uso_preferido="VARIABLE")
        data_type_dest = entry.get("data_type").upper() if entry and entry.get("data_type") else None
        
        if data_type_dest == 'INT':
            self.asm_code.append(f"    MOV AX, {src_asm}")
            self.asm_code.append(f"    MOV {dest_asm}, AX")
        elif data_type_dest == 'FLOAT':
            self.asm_code.append(f"    FLD DWORD PTR {src_asm}")
            self.asm_code.append(f"    FSTP DWORD PTR {dest_asm}")
        else: # Asignación de String (solo funciona si el tamaño del destino es suficiente)
             self.asm_code.append(f"    MOV DWORD EAX, {src_asm}")
             self.asm_code.append(f"    MOV DWORD [{dest_asm}], EAX") # Solo copia punteros (simple para esta simulación)
    
    # Comparaciones
    def generate_comparison(self, res_asm, op1_asm, op2_asm, operator, result_type):
        """Genera código para operadores relacionales y almacena 0/1 en res_asm."""
        
        self.asm_code.append(f" ; Comparación ({operator}) - Terceto {len(self.asm_code)}")
        
        # Cargar OP1 y comparar con OP2
        self.asm_code.append(f"   MOV AX, word [{op1_asm}]")
        self.asm_code.append(f"   CMP AX, word [{op2_asm}]")
        
        # Determinar la instrucción SETcc
        set_instruction = ""
        if operator == '<':
            set_instruction = "SETL" # Set Less (menor con signo)
        elif operator == '>':
            set_instruction = "SETG" # Set Greater (mayor con signo)
        elif operator == '==':
            set_instruction = "SETE" # Set Equal (igual)
        # TODO: Añadir más operadores relacionales si es necesario: JNE/SETNE, JGE/SETGE, etc.

        if set_instruction:
            # 3. Guardar el resultado booleano (0 o 1) en AL
            self.asm_code.append(f" {set_instruction} AL ; AL = 1 si la condición es verdadera, 0 si no")
            
            # 4. Mover el resultado a la variable temporal (V_T_N)
            self.asm_code.append(f"  MOVZX EAX, AL ; Extiende AL (0/1) a EAX (32 bits)")
            self.asm_code.append(f"  MOV word [{res_asm}], AX ; Guarda el 0/1 en la variable temporal (DW)")
        
    def generate_print(self, op_to_print):
        """
        Traduce el terceto PRINT.
        Asume que las funciones de runtime (imprimir_string, imprimir_int, imprimir_float)
        están disponibles.
        """
        # 1. Determinar si es un literal STRING
        if isinstance(op_to_print, str) and op_to_print.startswith('"') and op_to_print.endswith('"'):
            data_type = "STRING"
            op_asm = self.get_op_asm_label(op_to_print)
        else:
            # 2. Obtener el tipo de ID, Constante o Temporal [T#]
            if isinstance(op_to_print, str) and op_to_print.startswith('['):
                # Es una referencia [T#]
                idx = int(op_to_print.strip('[]'))
                data_type = self.tercetos[idx].result_type.upper() if self.tercetos[idx].result_type else "INT"
            else:
                # Es un ID:Lexema:Scope o Constante (ej: 2)
                entry = self.ts.get_token(str(op_to_print), uso_preferido=None)
                data_type = entry.get("data_type").upper() if entry else "INT" # Fallback a INT
                
            op_asm = self.get_op_asm_label(op_to_print)

        self.asm_code.append(f"  ; PRINT {op_to_print} ({data_type})")
        
        if data_type == "STRING":
            # Pasa la dirección de la etiqueta del string
            self.asm_code.append(f"    PUSH offset {op_asm}")
            # self.asm_code.append(f"  CALL imprimir_string")
            self.asm_code.append(f"    ADD ESP, 4") # Limpiar pila (argumento 32-bit)
            
        elif data_type == "INT":
            # Pasa la dirección de la etiqueta del entero (DW)
            self.asm_code.append(f"    PUSH offset {op_asm}")
            # self.asm_code.append(f"  CALL imprimir_int")
            self.asm_code.append(f"    ADD ESP, 4")
            
        elif data_type == "FLOAT":
            # Pasa la dirección de la etiqueta del float (DD)
            self.asm_code.append(f"    PUSH offset {op_asm}")
            # self.asm_code.append(f"  CALL imprimir_float")
            self.asm_code.append(f"    ADD ESP, 4")
        else:
            # Esto no debería pasar con un análisis semántico completo
            self.error_manager.add(None, f"Advertencia: Tipo desconocido ({data_type}) para imprimir.", source="CodeGen")
    # ----------------------------------------------------------------------
    # 3. RUTINAS FINALES Y PIE DE ARCHIVO
    # ----------------------------------------------------------------------

    def generate_runtime_routines(self):
        """Genera las rutinas de manejo de errores en tiempo de ejecución."""
        
        # Rutina de División por Cero
        self.asm_code.append(f"\n.ErrorDVC:")
        self.asm_code.append(f"\n{self.runtime_labels['DVC']}:") 
        self.asm_code.append(f"    PUSH {self.runtime_labels['DVC']}") 
        # self.asm_code.append(f"  CALL imprimir_string")
        self.asm_code.append(f"    ADD ESP, 4")
        self.asm_code.append(f"    invoke ExitProcess, 0")
                
        # Rutina de Overflow en Sumas INT
        self.asm_code.append(f"\n.ErrorOverflowInt:")
        self.asm_code.append(f"    PUSH {self.runtime_labels['OVF_INT']}")
        # self.asm_code.append(f"  CALL imprimir_string")
        self.asm_code.append(f"    ADD ESP, 4")
        self.asm_code.append(f"    invoke ExitProcess, 0")
        
        # Rutina de Overflow en Sumas FLOAT
        self.asm_code.append(f"\n.ErrorOverflowFloat:")
        self.asm_code.append(f"    PUSH {self.runtime_labels['OVF_FLOAT']}")
        # self.asm_code.append(f"  CALL imprimir_string")
        self.asm_code.append(f"    ADD ESP, 4")
        self.asm_code.append(f"    invoke ExitProcess, 0")
        
        # Finalización normal del programa
        self.asm_code.append(f"\nEND_PROGRAM:")
        self.asm_code.append(f"    invoke ExitProcess, 0")
    
    def generate_final_file(self):
        """Combina la sección de datos y la sección de código en el archivo final."""
        output = [
        ".386",
        ".model flat, stdcall",
        "option casemap :none",
        # "extern imprimir_string, imprimir_int, imprimir_float",
        "include \\masm32\\include\\windows.inc",
        "include \\masm32\\include\\kernel32.inc",
        "includelib \\masm32\\lib\\kernel32.lib",
        "include \\masm32\\include\\masm32.inc",
        "includelib \\masm32\\lib\\masm32.lib",
        "include \\masm32\\include\\masm32rt.inc"
        ]
        
        output.append("\n.data")
        # Agregar entradas del segmento .data
        for label, (directive, value, data_type) in self.data_section.items():
            output.append(f"{label} {directive} {value} ; {data_type}")
            
        output.append("HELLO_MSG DB ""El programa se ejecuto correctamente."", 0")
                    
        output.append("\n.code")
        output.append("\nstart:")
        
        # Añadir el código generado
        output.extend(self.asm_code)
        
        output.append("fin:")
        output.append("\n    print ADDR HELLO_MSG")
        
        output.append("\n    invoke ExitProcess, 0")
        output.append("end start") # Directiva que marca el final del archivo y el punto de entrada
        
        return "\n".join(output)

    def generate_code(self):
        """Función principal para generar el código Assembler."""
        self.prepare_asm_data()
        self.asm_code = [] # Limpiar la sección de código antes de generar

        # Traducir tercetos uno por uno
        for i, t in enumerate(self.tercetos):
            self.translate_terceto(i, t)
            
        # self.generate_runtime_routines()
        
        return self.generate_final_file()