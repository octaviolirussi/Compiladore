import copy
from tablaSimbolos import SymbolTable
from tercetos import GeneradorTercetos
from errorManager import ErrorManager

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
            # Correccion para la notación científica en floats
            label_base = str(original_key)
            # 1. Reemplazar caracteres no válidos (incluyendo el punto decimal y los signos)
            label_base = label_base.replace(':', '_').replace('[', 'T_').replace(']', '').replace('"', '')
            label_base = label_base.replace('.', '_')
            label_base = label_base.replace('+', 'P')  # P de Positivo
            label_base = label_base.replace('-', 'N')  # N de Negativo
            label_base = label_base.replace('F', 'E') # Normalizar la notación científica

            # 2. Eliminar guiones bajos iniciales si la clave original era solo un punto
            if label_base.startswith('_'):
                label_base = label_base.lstrip('_')
                
            # 3. Asegurar que la etiqueta final comience con una letra.
            if not label_base[0].isalpha():
                label_base = 'C' + label_base # Anteponer 'C' de Constante si no empieza con letra (ej: V_.45 -> V_C45)

            label = f"V_{label_base.upper()}"
            
        self.mem_map[original_key] = label
        return label

    def prepare_asm_data(self):
        """Define todas las variables, constantes y mensajes de error en .data (32-bit)."""
        
        # Mensajes de runtime (strings)
        self.runtime_labels["DVC"] = self._add_data_entry("DVC_MSG", "DB", "'Error en tiempo de ejecución: División por Cero.', 0", "STRING")
        self.runtime_labels["OVF_INT"] = self._add_data_entry("OVF_INT_MSG", "DB", "'Error en tiempo de ejecución: Overflow en suma de INT.', 0", "STRING")
        self.runtime_labels["OVF_FLOAT"] = self._add_data_entry("OVF_FLOAT_MSG", "DB", "'Error en tiempo de ejecución: Overflow en suma de FLOAT.', 0", "STRING")

        # Variables / constantes / parámetros
        for entry in self.ts.symbols.values():
            lexema_scope = entry.get("Lexema")
            uso = entry.get("Uso").upper()
            data_type = entry.get("data_type").upper() if entry.get("data_type") else "N/A"
            
            if uso in ["CONSTANTE", "VARIABLE", "PARAMETRO"]:
                asm_label = self._get_unique_asm_label(lexema_scope)
                
                # Ahora INT = DD (32 bits)
                if data_type == "INT":
                    initial_value = entry["Lexema"] if uso == "CONSTANTE" else "0"
                    self._add_data_entry(asm_label, "DD", initial_value, data_type) # DD = 32 bits (INT)
                elif data_type == "FLOAT":
                    if uso == "CONSTANTE":
                        lexema = str(entry["Lexema"])
                        # 1. Asegurar dígito inicial: Cambia '.45' a '0.45'
                        if lexema.startswith('.'):
                            lexema = '0' + lexema                        
                        # 2. Reemplazar F por E si tu compilador usa F para notación científica
                        lexema = lexema.replace('F', 'e') 
                        initial_value = lexema
                    else:
                        initial_value = "0.0"
                    self._add_data_entry(asm_label, "DD", initial_value, data_type)
                elif data_type == "STRING":
                    value = entry["Lexema"]
                    self._add_data_entry(asm_label, "DB", f"{value}, 0", data_type)

        # Temporales de tercetos -> DD por defecto para INT
        for i in range(len(self.tercetos)):
            terceto_ref = f"[{i}]"
            if terceto_ref not in self.mem_map:
                result_type = self.tercetos[i].result_type.upper() if self.tercetos[i].result_type else "INT"
                asm_label = self._get_unique_asm_label(terceto_ref)
                if result_type == "INT":
                    self._add_data_entry(asm_label, "DD", "0", result_type)
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
        self.asm_code.append(f"LABEL_{index}:") 
        
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
            self.asm_code.append(f"JMP LABEL_{t.op1.strip('[]')}")
        elif t.operador == 'BF': # Se asume que t.op1 es el resultado de una comparación booleana [T#]
            self.asm_code.append(f"    CMP dword ptr [{op1_asm}], 0")  # 0 = falso
            self.asm_code.append(f"    JE LABEL_{t.op2.strip('[]')}")      # Salta si falso
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

    ## Chequeos de Runtime: overflow en sumas y división por cero ---------------
    def generate_addition(self, res_asm, op1_asm, op2_asm, result_type):
        """Genera código para la suma en 32 bits (INT) o en FLOAT (FPU)."""
        if result_type.upper() == 'INT':
            self.asm_code.append(f"  ; Suma INT 32 bits - Terceto {len(self.asm_code)}")
            self.asm_code.append(f"  MOV EAX, dword ptr {op1_asm}")
            self.asm_code.append(f"  ADD EAX, dword ptr {op2_asm}")
            self.asm_code.append(f"  JO ErrorOverflowInt")
            self.asm_code.append(f"  MOV dword ptr [{res_asm}], EAX")
        elif result_type.upper() == 'FLOAT':
            self.asm_code.append(f"  ; Suma FLOAT - Terceto {len(self.asm_code)}")
            self.asm_code.append(f"  FLD dword ptr [{op1_asm}]")
            self.asm_code.append(f"  FADD dword ptr [{op2_asm}]")
            self.asm_code.append(f"  FSTSW AX")
            self.asm_code.append(f"  FWAIT")
            self.asm_code.append(f"  TEST AX, 0004h")
            self.asm_code.append(f"  JNZ ErrorOverflowFloat")
            self.asm_code.append(f"  FSTP dword ptr [{res_asm}]")

    def generate_subtraction(self, res_asm, op1_asm, op2_asm, result_type):
        if result_type.upper() == 'INT':
            self.asm_code.append(f"  ; Resta INT 32 bits - Terceto {len(self.asm_code)}")
            self.asm_code.append(f"  MOV EAX, dword ptr [{op1_asm}]")
            self.asm_code.append(f"  SUB EAX, dword ptr [{op2_asm}]")
            # self.asm_code.append(f"  JO ErrorOverflowInt")
            self.asm_code.append(f"  MOV dword ptr [{res_asm}], EAX")
        elif result_type.upper() == 'FLOAT':
            self.asm_code.append(f"  ; Resta FLOAT - Terceto {len(self.asm_code)}")
            self.asm_code.append(f"  FLD dword ptr [{op1_asm}]")
            self.asm_code.append(f"  FSUB dword ptr [{op2_asm}]")
            self.asm_code.append(f"  FSTSW AX")
            self.asm_code.append(f"  FWAIT")
            self.asm_code.append(f"  TEST AX, 0004h")
            # self.asm_code.append(f"  JNZ ErrorOverflowFloat")
            self.asm_code.append(f"  FSTP dword ptr [{res_asm}]")
    
    def generate_multiplication(self, res_asm, op1_asm, op2_asm, result_type):
        if result_type.upper() == 'INT':
            self.asm_code.append(f"  ; Multiplicacion INT 32 bits - Terceto {len(self.asm_code)}")
            self.asm_code.append(f"  MOV EAX, dword ptr [{op1_asm}]")
            self.asm_code.append(f"  IMUL EAX, dword ptr [{op2_asm}]")
            # self.asm_code.append(f"  JO ErrorOverflowInt")
            self.asm_code.append(f"  MOV dword ptr [{res_asm}], EAX")
        elif result_type.upper() == 'FLOAT':
            self.asm_code.append(f"  ; Multiplicacion FLOAT - Terceto {len(self.asm_code)}")
            self.asm_code.append(f"  FLD dword ptr [{op1_asm}]")
            self.asm_code.append(f"  FMUL dword ptr [{op2_asm}]")
            self.asm_code.append(f"  FSTSW AX")
            self.asm_code.append(f"  FWAIT")
            self.asm_code.append(f"  TEST AX, 0004h")
            # self.asm_code.append(f"  JNZ ErrorOverflowFloat")
            self.asm_code.append(f"  FSTP dword ptr [{res_asm}]")

    def generate_division(self, res_asm, op1_asm, op2_asm, result_type):
        if result_type.upper() == 'INT':
            self.asm_code.append(f"  ; Division INT 32 bits - Terceto {len(self.asm_code)}")
            self.asm_code.append(f"  MOV ECX, dword ptr [{op2_asm}]")
            self.asm_code.append(f"  CMP ECX, 0")
            self.asm_code.append(f"  JE ErrorDVC")
            self.asm_code.append(f"  MOV EAX, dword ptr [{op1_asm}]")
            self.asm_code.append(f"  CDQ")                    # Sign-extend EAX -> EDX:EAX
            self.asm_code.append(f"  IDIV ECX")               # EAX = EDX:EAX / ECX
            self.asm_code.append(f"  MOV dword ptr [{res_asm}], EAX")
        elif result_type.upper() == 'FLOAT':
            self.asm_code.append(f"  ; Division FLOAT - Terceto {len(self.asm_code)}")
            self.asm_code.append(f"  FLD dword ptr [{op2_asm}]")
            self.asm_code.append(f"  FTST")
            self.asm_code.append(f"  FWAIT")
            self.asm_code.append(f"  FSTSW AX")
            self.asm_code.append(f"  SAHF")
            self.asm_code.append(f"  JZ ErrorDVC")
            self.asm_code.append(f"  FLD dword ptr [{op1_asm}]")
            self.asm_code.append(f"  FDIV dword ptr [{op2_asm}]")
            self.asm_code.append(f"  FSTP dword ptr [{res_asm}]")

    def generate_conv_if(self, res_asm, op1_asm):
        self.asm_code.append(f"  ; CONV_I_F (INT a FLOAT) - Terceto {len(self.asm_code)}")
        self.asm_code.append(f"  FILD dword ptr [{op1_asm}]")
        self.asm_code.append(f"  FSTP dword ptr [{res_asm}]")

    ## Asignación
    def generate_assignment(self, dest_asm, src_asm, dest_op, src_op, result_type):
        entry = self.ts.get_token(dest_op, uso_preferido="VARIABLE")
        data_type_dest = entry.get("data_type").upper() if entry and entry.get("data_type") else None

        if data_type_dest == 'INT':
            self.asm_code.append(f"    MOV EAX, dword ptr [{src_asm}]")
            self.asm_code.append(f"    MOV dword ptr [{dest_asm}], EAX")
        elif data_type_dest == 'FLOAT':
            self.asm_code.append(f"    FLD dword ptr [{src_asm}]")
            self.asm_code.append(f"    FSTP dword ptr [{dest_asm}]")
        else: # STRING / fallback
            self.asm_code.append(f"    ; Asignacion de STRING/PUNTERO (copia simple de 32-bit)")
            self.asm_code.append(f"    MOV EAX, dword ptr [{src_asm}]")
            self.asm_code.append(f"    MOV dword ptr [{dest_asm}], EAX")
    
    # Comparaciones
    def generate_comparison(self, res_asm, op1_asm, op2_asm, operator, result_type):
        self.asm_code.append(f" ; Comparacion ({operator}) - Terceto {len(self.asm_code)}")
        self.asm_code.append(f"   MOV EAX, dword ptr [{op1_asm}]")
        self.asm_code.append(f"   CMP EAX, dword ptr [{op2_asm}]")

        set_instruction = ""
        if operator == '<':
            set_instruction = "SETL"
        elif operator == '>':
            set_instruction = "SETG"
        elif operator == '==':
            set_instruction = "SETE"
        elif operator == '!=':
            set_instruction = "SETNE"
        elif operator == '<=':
            set_instruction = "SETLE"
        elif operator == '>=':
            set_instruction = "SETGE"

        if set_instruction:
            self.asm_code.append(f"    {set_instruction} AL")
            self.asm_code.append(f"    MOVZX EAX, AL")
            self.asm_code.append(f"    MOV dword ptr [{res_asm}], EAX")
        
    def generate_print(self, op_to_print):
        """
        Traduce el terceto PRINT a codigo ASM usando printf.
        Soporta INT, FLOAT y STRING.
        """
        NEWLINE_LABEL = "NEWLINE"
        if NEWLINE_LABEL not in self.data_section:
            self.data_section[NEWLINE_LABEL] = ("DB", "13,10,0", "STRING")  # CRLF

        if isinstance(op_to_print, str) and op_to_print.startswith('"') and op_to_print.endswith('"'):
            # STRING literal
            label = self._get_unique_asm_label(op_to_print)
            value = f'{op_to_print},0'  # conserva las comillas
            self.data_section[label] = ("DB", value, "STRING")
            self.asm_code.append(f"    invoke printf, addr {label}")
            self.asm_code.append(f"    invoke printf, addr {NEWLINE_LABEL}")

        else:
            # ID, temporal o constante
            entry = self.ts.get_token(str(op_to_print), uso_preferido=None)
            data_type = entry.get("data_type").upper() if entry else "INT"
            label = self.get_op_asm_label(op_to_print)

            if data_type == "INT":
                self.asm_code.append(f"    invoke printf, cfm$(\"%d\\n\"), dword ptr [{label}]")
            elif data_type == "FLOAT":
                # Creamos un label temporal para almacenar el float como double
                tmp_double_label = self._get_unique_asm_label("tmp_double")
                self.data_section[tmp_double_label] = ("DQ", "0.0", "FLOAT64")  # 64 bits para printf

                # Convertimos float 32 a 64 bits y lo imprimimos
                self.asm_code.append(f"    FLD dword ptr [{label}]")           # carga float 32 bits
                self.asm_code.append(f"    FSTP qword ptr [{tmp_double_label}]")  # lo guarda como double
                self.asm_code.append(f"    invoke printf, cfm$(\"%f\\n\"), [{tmp_double_label}]")
    # ----------------------------------------------------------------------
    # 3. RUTINAS FINALES Y PIE DE ARCHIVO
    # ----------------------------------------------------------------------

    def generate_runtime_routines(self):
        """Genera las rutinas de manejo de errores en tiempo de ejecucion."""
        
        # Rutina de División por Cero
        self.asm_code.append(f"\nErrorDVC:")
        self.asm_code.append(f"\n{self.runtime_labels['DVC']}:") 
        self.asm_code.append(f"    PUSH {self.runtime_labels['DVC']}") 
        # self.asm_code.append(f"  CALL imprimir_string")
        self.asm_code.append(f"    ADD ESP, 4")
        self.asm_code.append(f"    invoke ExitProcess, 0")
                
        # Rutina de Overflow en Sumas INT
        self.asm_code.append(f"\nErrorOverflowInt:")
        self.asm_code.append(f"    PUSH {self.runtime_labels['OVF_INT']}")
        # self.asm_code.append(f"  CALL imprimir_string")
        self.asm_code.append(f"    ADD ESP, 4")
        self.asm_code.append(f"    invoke ExitProcess, 0")
        
        # Rutina de Overflow en Sumas FLOAT
        self.asm_code.append(f"\nErrorOverflowFloat:")
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
            "option casemap:none",
            "include \\masm32\\include\\masm32rt.inc",
            "includelib \\masm32\\lib\\masm32.lib",
            "includelib \\masm32\\lib\\kernel32.lib",
            "printf PROTO C :VARARG",
        ]

        # === .data SECTION ===
        output.append("\n.data")
        for label, (directive, value, data_type) in self.data_section.items():
            output.append(f"{label} {directive} {value} ; {data_type}")

        # Mensaje final opcional
        output.append("HELLO_MSG DB \"El programa se ejecuto correctamente.\",0")

        # === .code SECTION ===
        output.append("\n.code")
        output.append("start:")

        # Código generado
        output.extend(self.asm_code)

        # Salto a fin al terminar el programa principal
        output.append("    jmp fin")

        # Handlers de error
        output.append("\n; ----- HANDLERS DE ERROR -----")
        output.append("ErrorOverflowInt:")
        output.append('    print "Error en tiempo de ejecucion: Overflow en INT"')
        output.append("    invoke ExitProcess, 1")

        output.append("ErrorOverflowFloat:")
        output.append('    print "Error en tiempo de ejecucion: Overflow en FLOAT"')
        output.append("    invoke ExitProcess, 1")

        output.append("ErrorDVC:")
        output.append('    print "Error en tiempo de ejecucion: Division por Cero"')
        output.append("    invoke ExitProcess, 1")

        # Fin del programa
        output.append("\nfin:")
        output.append("    print ADDR HELLO_MSG")
        output.append("    invoke ExitProcess, 0")
        output.append("end start")

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