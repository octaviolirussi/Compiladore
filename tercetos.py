from tablaSimbolos import SymbolTable

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
    # Constante para marcar que el destino de un salto es desconocido.
    PENDIENTE = '?' 
    
    def __init__(self,symbol_table,error_manager):
        self.tercetos = []
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


    def mostrar(self):
        print("\n=== CÓDIGO INTERMEDIO (TERCETOS) ===")
        for i, t in enumerate(self.tercetos):
            op1_str = str(t.op1)
            op2_str = str(t.op2)
            
            print(f"{i:d}: ({t.operador}, {op1_str}, {op2_str})")