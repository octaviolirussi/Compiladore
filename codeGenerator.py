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
        self.func_return_types = {}      
        self.func_stack = []  

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
            label_base = str(original_key)

            # Elimina comillas y reemplaza espacios
            label_base = label_base.replace('"', '')
            label_base = label_base.replace(' ', '_')

            # Reemplaza caracteres no válidos
            label_base = label_base.replace(':', '_')
            label_base = label_base.replace('[', 'T_')
            label_base = label_base.replace(']', '')
            label_base = label_base.replace('.', '_')
            label_base = label_base.replace('+', 'P')
            label_base = label_base.replace('-', 'N')
            label_base = label_base.replace('!', '')

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

        self.runtime_labels["INF_CONST"] = self._add_data_entry("V_INF_CONST", "DD", "7F800000h", "HEX_FLOAT")
        self.runtime_labels["NINF_CONST"] = self._add_data_entry("V_NINF_CONST", "DD", "7F800000h", "HEX_FLOAT")

        
        # Variables / constantes / parámetros
        for entry in self.ts.symbols.values():
            lexema_scope = entry.get("Lexema")
            uso = entry.get("Uso").upper()
            data_type = entry.get("data_type").upper() if entry.get("data_type") else "N/A"
            
            if uso in ["CONSTANTE", "VARIABLE", "PARAMETRO"]:
                asm_label = self._get_unique_asm_label(lexema_scope)
                
                
                if data_type == "INT":
                    initial_value = entry["Lexema"] if uso == "CONSTANTE" else "0"
                    self._add_data_entry(asm_label, "DW", initial_value, data_type) # DD = 32 bits (INT)
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
        elif t.operador == 'FUNC':
            self.generate_function_start(t.op1)   
        elif t.operador == 'END_FUNC':
            self.generate_function_end()
        elif t.operador == 'RETURN':
            self.generate_return(op1_asm)
        elif t.operador == 'CALL':
            self.generate_call(t.op1, res_asm)
        elif t.operador == 'END_PROGRAM':
            self.asm_code.append("    JMP fin")


    def get_op_asm_label(self, op):
        """Devuelve la etiqueta ASM para un operando (lexema o referencia de terceto [N])."""
        if op is None:
            return None
        
        # Convertir a cadena para la búsqueda, ya que las claves de las constantes suelen ser strings
        op_key = str(op)

        # Si es una referencia de terceto [N]
        if op_key.startswith('[') and op_key.endswith(']'):
            return self.mem_map.get(op_key)

        # Si es una variable/constante/parámetro
        return self.mem_map.get(op_key)

    ## Chequeos de Runtime: overflow en sumas y división por cero ---------------
    def generate_addition(self, res_asm, op1_asm, op2_asm, result_type):
        """Genera código para la suma en 32 bits (INT) o en FLOAT (FPU)."""
        if result_type.upper() == 'INT':
            self.asm_code.append(f"  ; Suma INT 16 bits")
            self.asm_code.append(f"  MOV AX, WORD PTR [{op1_asm}]")
            self.asm_code.append(f"  ADD AX, WORD PTR [{op2_asm}]")
            self.asm_code.append(f"  JO ErrorOverflowInt")
            self.asm_code.append(f"  MOV WORD PTR [{res_asm}], AX")
        
        elif result_type.upper() == 'FLOAT':
            INF_LABEL = self.runtime_labels.get("INF_CONST")
            NINF_LABEL = self.runtime_labels.get("NINF_CONST")

            self.asm_code.append(f"  ; Suma FLOAT - Deteccion por Valor INF")
            
            self.asm_code.append(f"  FLD dword ptr [{op1_asm}]")
            self.asm_code.append(f"  FADD dword ptr [{op2_asm}]")
            
            self.asm_code.append(f"  FSTP dword ptr [{res_asm}]") 
            
            # --- CHEQUEOS DE OVERFLOW ---
            
            # self.asm_code.append(f"  MOV EAX, dword ptr [{res_asm}]") 
            
            # self.asm_code.append(f"  CMP EAX, dword ptr [{INF_LABEL}]") 
            # self.asm_code.append(f"  JE ErrorOverflowFloat") 
            
            # self.asm_code.append(f"  CMP EAX, dword ptr [{NINF_LABEL}]") 
            # self.asm_code.append(f"  JE ErrorOverflowFloat")
            
            self.asm_code.append(f"  ; Suma FLOAT - Deteccion de Underflow y Overflow (Bandera)")
            
            self.asm_code.append(f"  FLD dword ptr [{op1_asm}]")
            self.asm_code.append(f"  FADD dword ptr [{op2_asm}]")
            
            self.asm_code.append(f"  FSTSW AX")
            self.asm_code.append(f"  FWAIT")
            self.asm_code.append(f"  TEST AX, 0008h")  # Chequea el bit de excepción de Overflow (0008h)
            self.asm_code.append(f"  JNZ ErrorOverflowFloat") # Salta si Overflow detectado
            self.asm_code.append(f"  FSTP dword ptr [{res_asm}]")
            pass

    def generate_subtraction(self, res_asm, op1_asm, op2_asm, result_type):
        if result_type.upper() == 'INT':
            self.asm_code.append(f"  ; Resta INT 16 bits - Terceto {len(self.asm_code)}")
            self.asm_code.append(f"  MOV AX, WORD PTR [{op1_asm}]")
            self.asm_code.append(f"  SUB AX, WORD PTR [{op2_asm}]")
            self.asm_code.append(f"  JO ErrorOverflowInt")
            self.asm_code.append(f"  MOV WORD PTR [{res_asm}], AX")

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
            self.asm_code.append(f"  ; Multiplicacion INT 16 bits - Terceto {len(self.asm_code)}")
            self.asm_code.append(f"  MOV AX, WORD PTR [{op1_asm}]")
            self.asm_code.append(f"  IMUL WORD PTR [{op2_asm}]")   
            self.asm_code.append(f"  JO ErrorOverflowInt")
            self.asm_code.append(f"  MOV WORD PTR [{res_asm}], AX")
        elif result_type.upper() == 'FLOAT':
            self.asm_code.append(f"  ; Multiplicacion FLOAT - Terceto {len(self.asm_code)}")
            self.asm_code.append(f"  FLD dword ptr [{op1_asm}]")
            self.asm_code.append(f"  FMUL dword ptr [{op2_asm}]")
            self.asm_code.append(f"  FSTSW AX")
            self.asm_code.append(f"  FWAIT")
            self.asm_code.append(f"  TEST AX, 0004h")
            self.asm_code.append(f"  FSTP dword ptr [{res_asm}]")

    def generate_division(self, res_asm, op1_asm, op2_asm, result_type):
        if result_type.upper() == 'INT':
            self.asm_code.append(f"  ; Division INT 16 bits - Terceto {len(self.asm_code)}")

            # divisor
            self.asm_code.append(f"  MOV CX, WORD PTR [{op2_asm}]")
            self.asm_code.append(f"  CMP CX, 0")
            self.asm_code.append(f"  JE ErrorDVC")

            # dividendo
            self.asm_code.append(f"  MOV AX, WORD PTR [{op1_asm}]")
            self.asm_code.append(f"  CWD")              

            # division con signo
            self.asm_code.append(f"  IDIV CX")           

            # resultado
            self.asm_code.append(f"  MOV WORD PTR [{res_asm}], AX")
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
        self.asm_code.append(f"  ; CONV_I_F (INT 16 → FLOAT 32)")
        self.asm_code.append(f"  FILD WORD PTR [{op1_asm}]")
        self.asm_code.append(f"  FSTP DWORD PTR [{res_asm}]")

    ## Asignación
    def generate_assignment(self, dest_asm, src_asm, dest_op, src_op, result_type):
        entry = self.ts.get_token(dest_op, uso_preferido="VARIABLE")
        data_type_dest = entry.get("data_type").upper() if entry and entry.get("data_type") else None

        if data_type_dest == 'INT':
            self.asm_code.append(f"    MOV AX, WORD PTR [{src_asm}]")
            self.asm_code.append(f"    MOV WORD PTR [{dest_asm}], AX")
        elif data_type_dest == 'FLOAT':
            self.asm_code.append(f"    FLD dword ptr [{src_asm}]")
            self.asm_code.append(f"    FSTP dword ptr [{dest_asm}]")
        else: # STRING / fallback
            self.asm_code.append(f"    ; Asignacion de STRING/PUNTERO (copia simple de 32-bit)")
            self.asm_code.append(f"    MOV EAX, dword ptr [{src_asm}]")
            self.asm_code.append(f"    MOV dword ptr [{dest_asm}], EAX")
    
    # Comparaciones
    def generate_comparison(self, res_asm, op1_asm, op2_asm, operator, result_type):
        self.asm_code.append(f" ; Comparacion ({operator})")

        if result_type.upper() == "INT":
            self.asm_code.append(f"   MOVSX EAX, word ptr [{op1_asm}]")
            self.asm_code.append(f"   MOVSX EBX, word ptr [{op2_asm}]")
            self.asm_code.append(f"   CMP EAX, EBX")

            setcc = {
                "<":  "SETL",
                ">":  "SETG",
                "==": "SETE",
                "!=": "SETNE",
                "<=": "SETLE",
                ">=": "SETGE"
            }[operator]

        else:
            self.asm_code.append(f"   FLD dword ptr [{op2_asm}]")  
            self.asm_code.append(f"   FLD dword ptr [{op1_asm}]")  
            self.asm_code.append(f"   FCOMPP")
            self.asm_code.append(f"   FSTSW AX")
            self.asm_code.append(f"   SAHF")

            setcc = {
                "<":  "SETB",
                ">":  "SETA",
                "==": "SETE",
                "!=": "SETNE",
                "<=": "SETBE",
                ">=": "SETAE"
            }[operator]

        # Resultado booleano (0 o 1)
        self.asm_code.append(f"   {setcc} AL")
        self.asm_code.append(f"   MOVZX EAX, AL")
        self.asm_code.append(f"   MOV word ptr [{res_asm}], AX")
        
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
                self.asm_code.append(f"    MOV AX, WORD PTR [{label}]")
                self.asm_code.append(f"    MOVSX EAX, AX")
                self.asm_code.append(f"    invoke printf, cfm$(\"%d\\n\"), EAX")
            elif data_type == "FLOAT":
                # Creamos un label temporal para almacenar el float como double
                tmp_double_label = self._get_unique_asm_label("tmp_double")
                self.data_section[tmp_double_label] = ("DQ", "0.0", "FLOAT64")  # 64 bits para printf

                # Convertimos float 32 a 64 bits y lo imprimimos
                self.asm_code.append(f"    FLD dword ptr [{label}]")           # carga float 32 bits
                self.asm_code.append(f"    FSTP qword ptr [{tmp_double_label}]")  # lo guarda como double
                self.asm_code.append(f"    invoke printf, cfm$(\"%f\\n\"), [{tmp_double_label}]")

    def generate_function_start(self, func_name):
        # Etiqueta global visible desde main
        self.asm_code.append("")
        func_name = func_name.replace(":", "_")
        self.asm_code.append(f"{func_name}:")
        self.asm_code.append("    PUSH EBP")
        self.asm_code.append("    MOV EBP, ESP")

    def generate_function_end(self):
        self.asm_code.append("    MOV ESP, EBP")
        self.asm_code.append("    POP EBP")
        self.asm_code.append("    RET")

    def generate_return(self, value_asm):
        # Mover el valor al registro EAX (convención estándar)
        self.asm_code.append(f"    MOV EAX, dword ptr [{value_asm}]")
        self.asm_code.append("    MOV ESP, EBP")
        self.asm_code.append("    POP EBP")
        self.asm_code.append("    RET")

    def generate_call(self, function_name, res_asm):
        """
        Genera código ASM para llamar a una función.
        Si la función devuelve un valor, RETURN debe haber depositado el valor en EAX (INT)
        o en ST(0) (FLOAT).
        """
        function_name = function_name.replace(":", "_")
        self.asm_code.append(f"    CALL {function_name}")

        # Si no hay retorno, no generamos asignación
        if res_asm is None:
            return

        # Detectar tipo del retorno
        ret_type = self.func_return_types.get(function_name, "INT")

        if ret_type == "INT":
            # Guardar EAX en el temporal de resultado
            self.asm_code.append(f"    MOV dword ptr [{res_asm}], EAX")

        elif ret_type == "FLOAT":
            # Guardar retorno FLOAT desde FPU
            self.asm_code.append(f"    FSTP dword ptr [{res_asm}]")
    # ----------------------------------------------------------------------
    # 3. RUTINAS FINALES Y PIE DE ARCHIVO
    # ----------------------------------------------------------------------

    def generate_runtime_routines(self):
        """Genera las rutinas de manejo de errores en tiempo de ejecucion."""
        
        # Rutina de División por Cero
        self.asm_code.append(f"\nErrorDVC:")
        self.asm_code.append(f"\n{self.runtime_labels['DVC']}:") 
        self.asm_code.append(f"    PUSH {self.runtime_labels['DVC']}") 
        self.asm_code.append(f"    ADD ESP, 4")
        self.asm_code.append(f"    invoke ExitProcess, 0")
                
        # Rutina de Overflow en Sumas INT
        self.asm_code.append(f"\nErrorOverflowInt:")
        self.asm_code.append(f"    PUSH {self.runtime_labels['OVF_INT']}")
        self.asm_code.append(f"    ADD ESP, 4")
        self.asm_code.append(f"    invoke ExitProcess, 0")
        
        # Rutina de Overflow en Sumas FLOAT
        self.asm_code.append(f"\nErrorOverflowFloat:")
        self.asm_code.append(f"    PUSH {self.runtime_labels['OVF_FLOAT']}")
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