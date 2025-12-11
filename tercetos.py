from tablaSimbolos import SymbolTable
import copy

class Terceto:
    def __init__(self, operador, op1, op2, result_type=None, lineno=None):
        self.operador = operador
        self.op1 = op1
        self.op2 = op2
        self.result_type = result_type
        self.lineno = lineno  

    def __repr__(self):
        return f"({self.operador}, {self.op1}, {self.op2}, TIPO={self.result_type})"

class GeneradorTercetos:
    PENDIENTE = '?' # Constante para marcar que el destino de un salto es desconocido.
    
    def __init__(self,symbol_table,error_manager):
        self.tercetos = []
        self.funciones = []
        self.symbol_table = symbol_table
        self.error_manager = error_manager
        self.current_scope = "G"  
        self.scope_stack = ["G"]  

    def nuevo(self, operador, op1, op2=None, result_type=None, lineno=None):
        indice = len(self.tercetos)
        self.tercetos.append(Terceto(operador, op1, op2, result_type, lineno))
        return f"[{indice}]"
    
    def get_result_type(self, index):
        """
            Retorna el tipo de dato del resultado del terceto en el índice dado.
            Esto es usado por el parser para la comprobación de tipos.
        """
        if isinstance(index, str):
            try:
                index = int(index.strip('[]'))
            except ValueError:
                return None # No es un índice válido
                
        if 0 <= index < len(self.tercetos):
            return self.tercetos[index].result_type 
        return None # Índice fuera de rango
    
    def backpatch(self, lista_indices_ref, destino_indice):
        """
        Rellena el campo de destino (op2) de los tercetos listados.

        Args:
            lista_indices_ref (list): Lista de strings de referencia (ej. ['[1]', '[3]']).
            destino_indice (int): El índice numérico del terceto destino (etiqueta).
        """
        destino_ref = f"[{destino_indice}]" 

        for indice_ref in lista_indices_ref:
            indice = int(indice_ref.strip('[]'))
            
            if 0 <= indice < len(self.tercetos):
                t = self.tercetos[indice]
                
                if t.op2 == self.PENDIENTE: 
                    t.op2 = destino_ref
                else:
                    t.op1 = destino_ref
            else:
                pass 

    def backpatch2(self, terceto, indice):
        """
        Asigna un nuevo valor al op2 del terceto recibido.
        'indice' puede ser un número o una referencia tipo '[5]'.
        """
        # Si llega un número, lo convertimos a referencia "[n]"
        if isinstance(indice, int):
            indice = f"[{indice}]"

        terceto.op2 = indice

    #FUNCION PARA MOVER UN TERCETO (BF)
    def mover_terceto(self, indice_origen, indice_destino):
        """
        Mueve un terceto de indice_origen a indice_destino.
        Ajusta automáticamente referencias internas a tercetos.
        """
        if indice_origen == indice_destino:
            return  # nada que hacer
        
        # Extraer el terceto
        t = self.tercetos.pop(indice_origen)
        
        # Insertar en nueva posición
        self.tercetos.insert(indice_destino, t)

        # Ajustar referencias internas de los demás tercetos
        for terceto in self.tercetos:
            for attr in ['op1', 'op2']:
                val = getattr(terceto, attr)
                if isinstance(val, str) and val.startswith('['):
                    idx = int(val.strip('[]'))
                    if indice_origen < indice_destino:  # se movió hacia adelante
                        if indice_origen < idx <= indice_destino:
                            setattr(terceto, attr, f"[{idx-1}]")
                        elif idx == indice_origen:
                            setattr(terceto, attr, f"[{indice_destino}]")
                    else:  # se movió hacia atrás
                        if indice_destino <= idx < indice_origen:
                            setattr(terceto, attr, f"[{idx+1}]")
                        elif idx == indice_origen:
                            setattr(terceto, attr, f"[{indice_destino}]")

    def actualizar_scope(self):
        """
        Recorre los tercetos, mantiene el scope según FUNC y END_FUNC,
        y verifica que los parámetros solo se usen dentro de su propia función.
        """
        self.current_scope = "G"
        self.scope_stack = ["G"]
        self.funcion_actual = None  # para saber en qué función estamos
        self.errores_semanticos = []

        for i, t in enumerate(self.tercetos):
            # --- Entrar en función ---
            if t.operador == "FUNC":
                self.funcion_actual = str(t.op1)
                nuevo_scope = f"{self.funcion_actual}:{self.scope_stack[-1]}"
                self.scope_stack.append(nuevo_scope)
                self.current_scope = nuevo_scope

            # --- Salir de función ---
            elif t.operador == "END_FUNC":
                if len(self.scope_stack) > 1:
                    self.scope_stack.pop()
                self.current_scope = self.scope_stack[-1]
                self.funcion_actual = None  # ya no estamos dentro de ninguna función

            # --- Otros tercetos ---
            else:
                for op in [t.op1, t.op2]:
                    if not isinstance(op, str):
                        continue
                    if not op.isidentifier():
                        continue

                    param_funcs = self._buscar_parametro(op)
                    if param_funcs:
                        # Si estoy dentro de una función, verifico que coincida con al menos una pertenencia
                        if self.funcion_actual and self.funcion_actual not in param_funcs:
                            msg = f"Error: parámetro '{op}' pertenece a {param_funcs} pero se usa en {self.funcion_actual}"
                            self.error_manager.add(t.lineno, msg, source="Scope")


    def _buscar_parametro(self, nombre):
        """
        Devuelve una lista con todas las funciones de pertenencia
        en las que el identificador 'nombre' aparece como parámetro.
        """
        funciones_pertenencia = []
        for entry in self.symbol_table.symbols.values():
            if entry["Lexema"] == nombre and entry["Uso"].upper() == "PARAMETRO":
                funciones_pertenencia.append(entry["Funcion_Pertenencia"])
        return funciones_pertenencia if funciones_pertenencia else None
    
    def actualizar_tercetos(self):
        "funcion para agregar en los tercetos el lexema con su correspondiente ambito"
        self.current_scope = "G"
        self.scope_stack = ["G"]
        self.funcion_actual = None  # para saber en qué función estamos

        for i, t in enumerate(self.tercetos):
            # --- Entrar en función ---
            if t.operador == "FUNC":
                self.funcion_actual = str(t.op1)
                nuevo_scope = f"{self.scope_stack[-1]}:{self.funcion_actual}"
                self.scope_stack.append(nuevo_scope)
                self.current_scope = nuevo_scope
                t.op1 = t.op1 + ":" + self.scope_stack[-1]

            # --- Salir de función ---
            elif t.operador == "END_FUNC":
                if len(self.scope_stack) > 1:
                    t.op1 = t.op1 + ":" + self.scope_stack[-1]
                    self.scope_stack.pop()
                self.current_scope = self.scope_stack[-1]
                self.funcion_actual = None  # ya no estamos dentro de ninguna función

            #otros tercetos
            else:
                for operand in [t.op1, t.op2]:
                    # Ignorar operandos vacíos
                    if operand is None:
                        continue

                    # Ignorar números reales
                    if isinstance(operand, (int, float)):
                        continue

                    # Ignorar strings numéricas
                    if isinstance(operand, str) and operand.isdigit():
                        continue

                    if operand.lower() in ("int", "float"):
                        continue

                    # 5. Si es un acceso tipo [A], [1], [temp] → descartar
                    if operand.startswith("[") and operand.endswith("]"):
                        continue

                    # Ignorar literales entre comillas
                    if isinstance(operand, str) and (
                        operand.startswith('"') and operand.endswith('"')
                    ):
                        continue

                    s = str(operand)

                    if self.es_float_o_punto(s):
                        continue

                    # En este punto, si es str, lo considerás un IDENTIFICADOR (variable o parámetro)
                    if isinstance(operand, str):
                        if t.operador == "CALL":
                            func = t.op1 + ":" + self.scope_stack[-1] + ":" + t.op1
                            e=False
                            for entry in self.symbol_table.symbols.values():
                                if entry["Lexema"] == func:
                                    t.op1 = func
                                    e=True
                                    break
                            if not e:
                                msg = f"Error: funcion '{func}' invocada fuera de su ambito"
                                self.error_manager.add(t.lineno, msg, source="Scope")

                        if t.operador == "->":     
                            first = operand.split(":")[0]   
                            for entry in self.symbol_table.symbols.values():
                                if entry["Lexema"] == first + ":"+ self.scope_stack[-1] + ":" + entry["Funcion_Pertenencia"]:
                                    t.operador = "="
                                    if t.op1 == operand:
                                        t.op1 = entry["Lexema"]
                                    elif t.op2 == operand:
                                        t.op2 = entry["Lexema"]

                                    seguir = False
                                    break  # sale solo del for
                                
                        for entry in self.symbol_table.symbols.values():
                            last = self.scope_stack[-1]
                            if entry["Lexema"] == operand + ":" + str(last) and entry["Uso"] == "PARAMETRO":
                                if t.op1 == operand:
                                    t.op1 = operand + ":" + last
                                else:
                                    t.op2 = operand + ":" + last
                                break
                        
                        seguir = True
                        scope = self.scope_stack.copy()   # usa copia

                        while seguir and scope:
                            last = scope[-1]

                            for entry in self.symbol_table.symbols.values():
                                if entry["Lexema"] == operand + ":" + last and entry["Uso"] in ("VARIABLE", "FUNCION"):
                                    
                                    # actualizar en tercetos
                                    if t.op1 == operand:
                                        t.op1 = operand + ":" + last
                                    elif t.op2 == operand:
                                        t.op2 = operand + ":" + last

                                    seguir = False
                                    break  # sale solo del for

                            if not seguir:
                                break  # corta también el while
                            
                            scope.pop()  # elimina último scope y sigue buscando
        
            
        for i, t in enumerate(self.tercetos):
            "Verifico si existen variables no declaradas"
            for operand in [t.op1, t.op2]:
                    # Ignorar operandos vacíos
                    if operand is None:
                        continue

                    # Ignorar números reales
                    if isinstance(operand, (int, float)):
                        continue

                    # Ignorar strings numéricas
                    if isinstance(operand, str) and operand.isdigit():
                        continue

                    if operand.lower() in ("int", "float"):
                        continue

                    # 5. Si es un acceso tipo [A], [1], [temp] → descartar
                    if operand.startswith("[") and operand.endswith("]"):
                        continue

                    # Ignorar literales entre comillas
                    if isinstance(operand, str) and (
                        operand.startswith('"') and operand.endswith('"')
                    ):
                        continue

                    s = str(operand)

                    if self.es_float_o_punto(s):
                        continue

                    if t.operador == "CVR_RET":
                        continue

                    # En este punto, si es str, lo considerás un IDENTIFICADOR (variable o parámetro)
                    if isinstance(operand, str):
                        if ":" not in operand:
                            msg = f"ERROR: Identificador '{operand}' no está declarado."
                            self.error_manager.add(t.lineno, msg, source="Scope")
                            
                            
                            
    def es_float_o_punto(self,s: str) -> bool:
        """
        Devuelve True si 's' debe ser ignorado porque parece un float
        o un número con punto, según tus reglas.
        """

        if not isinstance(s, str):
            return False

        s = s.strip()

        if not s:
            return False

        # 1) Si empieza con un número y contiene un punto en alguna parte → ignorar
        if s[0].isdigit() and "." in s:
            return True

        # 2) Si empieza con '.' y el siguiente carácter es un número → ignorar
        if s.startswith(".") and len(s) > 1 and s[1].isdigit():
            return True

        return False
    
    def eliminar_declaraciones(self):

            original = copy.copy(self.tercetos)
            
            for i in range(len(self.tercetos) - 1, -1, -1):
                t = self.tercetos[i]

                if t.operador in ("DECL"):
                    self.tercetos.pop(i)
                    continue  # pasar al siguiente índice hacia atrás

            self.actualizar_referencias(original,self.tercetos)

    def mover_funciones(self):
        "Sacamos las funciones de los tercetos y las ponemos al final"

        funciones_guardadas = {}
        original = copy.copy(self.tercetos)
        #cuanto la cantidad de funciones y las ponemos en una lista
        funciones = []
        for entry in self.symbol_table.symbols.values():
            if entry["Uso"] == "FUNCION":
                funciones.append(entry["Lexema"])

        for func in funciones:
            i = 0
            elim = 0
            funciones_guardadas[func] = []
            while i < len(self.tercetos):
                t = self.tercetos[i]
                if t.operador == "FUNC" and func == t.op1:
                    funciones_guardadas[func].append(t)
                    i += 1
                    elim+=1

                    # contador de anidamiento para ignorar funciones internas
                    profundidad = 1

                    # recorrer hacia adelante hasta cerrar la función
                    while i < len(self.tercetos) and profundidad > 0:
                        t2 = self.tercetos[i]

                        # Si entro a una función interna → solo aumento profundidad
                        if t2.operador == "FUNC":
                            profundidad += 1
                            i += 1
                            continue

                        # Si salgo de una función
                        if t2.operador == "END_FUNC":
                            profundidad -= 1
                            i += 1
                            continue

                        # Solo guardar tercetos si estoy en la función "nivel 1"
                        if profundidad == 1:
                            funciones_guardadas[func].append(t2)
                            elim+=1
                        i += 1
                    funciones_guardadas[func].append(t2)
                    elim+=1
                    break  # TERMINA búsqueda de esta función
                i += 1
        self.elim_tercetos()

        for nombre_func, lista in funciones_guardadas.items():
            self.tercetos.extend(lista)   # agrega los tercetos al final

        self.actualizar_referencias(original,self.tercetos)

    def elim_tercetos(self):
        i = len(self.tercetos) - 1
        while i >= 0:
            t = self.tercetos[i]

            if t.operador == "END_FUNC":
                nombre_func = t.op1
                self.tercetos.pop(i)

                i -= 1

                # Ahora eliminar hasta el FUNC correcto
                while i >= 0:
                    t2 = self.tercetos[i]

                    if t2.operador == "FUNC" and t2.op1 == nombre_func:
                        self.tercetos.pop(i)  # eliminar FUNC
                        break

                    self.tercetos.pop(i)
                    i -= 1

            else:
                i -= 1

    def actualizar_referencias(self, original, nuevo):
        """
        Actualiza las referencias [N] de tercetos reordenados.
        """

        # 1. índice original → objeto original
        orig_idx_to_obj = {i: original[i] for i in range(len(original))}

        # 2. objeto → índice nuevo
        new_obj_to_idx = {nuevo[i]: i for i in range(len(nuevo))}

        # 3. Reemplazar referencias
        for t in nuevo:
            for campo in ("op1", "op2"):
                ref = getattr(t, campo)

                if not (isinstance(ref, str) and ref.startswith("[") and ref.endswith("]")):
                    continue

                try:
                    old_idx = int(ref[1:-1])
                except:
                    continue

                obj = orig_idx_to_obj.get(old_idx)
                if obj is None:
                    continue

                new_idx = new_obj_to_idx.get(obj)
                if new_idx is None:
                    # el terceto fue eliminado
                    continue

                setattr(t, campo, f"[{new_idx}]")

    def get_llamadas(self):
        return self.myparser.llamadas
    
    def generar_label(self):
        for i, t in enumerate(self.tercetos):
            if t.operador == "LABEL":
                t.operador = f"{t.operador}_{i}"
            elif t.operador == "->":
                t.operador = "="
            elif t.operador == "CALL":
                func = ":".join(t.op1.split(":")[1:])   
                j = i + 1                               
                terc = self.tercetos[j]

                while terc.operador == "CVR_RET":
                    var = terc.op2.split(":")[0]        

                    terc.op2 = f"{var}:{func}"
                    terc.operador = "="

                    j += 1
                    if j >= len(self.tercetos):
                        break
                    terc = self.tercetos[j]
    
    def correcciones(self):
        "Todas las correcciones del TP3 se ejecutan aca"
        self.actualizar_scope()
        self.actualizar_tercetos()
        self.eliminar_declaraciones()
        self.mover_funciones()
        self.generar_label()
        self.symbol_table.agrega_returns(self.tercetos)
        self.symbol_table.update_returns_values(self.tercetos)
        
    def mostrar(self):
        print("\n=== CÓDIGO INTERMEDIO (TERCETOS) ===")
        for i, t in enumerate(self.tercetos):
            op1_str = str(t.op1)
            op2_str = str(t.op2)
            
            result_type_str = f"TIPO={t.result_type}" if t.result_type else ""
            
            print(f"{i:d}: ({t.operador}, {op1_str}, {op2_str}, {result_type_str})")