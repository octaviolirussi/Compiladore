class SymbolTable:
    '''almacenar y gestionar toda la información relevante sobre los identificadores (variables, constantes, funciones, etc.) encontrados en el código fuente del programa, además de realizar validaciones de reglas de visibilidad (scope) y existencia.'''
    
    def __init__(self,error_manager):
        # Estructura: {id: {...datos...}}
        self.symbols = {}
        self.keywords = {}
        self.error_manager = error_manager
        self.next_id = 1
        self.load_keyword()

    def load_keyword(self):
        self.keywords = {
            "if": "IF",
            "else": "ELSE",
            "endif": "ENDIF",
            "print": "PRINT",
            "return": "RETURN",
            "while": "WHILE",
            "do": "DO",
            "float": "FLOAT",
            "int": "INT",
            "cv": "CV",
            "program": "PROGRAMA"
        }

    # ---------------------- TOKENS BÁSICOS ----------------------
    def add_token(self, lexema, token_type):
        entry = {
            "ID": self.next_id,
            "Lexema": lexema,
            "type": token_type,
            "Uso": "VARIABLE",
            "data_type": None,
            "Funcion_Pertenencia": "N/A",
            "Modificador": "N/A",
            "Scope": "N/A"
        }

        if token_type == "PROGRAMA":
            entry["data_type"] = "FUNCTION"
            entry["Uso"] = "PROGRAMA"
        elif token_type == "CONST_INT":
            entry["data_type"] = "INT"
            entry["Uso"] = "CONSTANTE"
        elif token_type == "CONST_FLOAT":
            entry["data_type"] = "FLOAT"
            entry["Uso"] = "CONSTANTE"
        elif token_type == "STRING":
            entry["data_type"] = "STRING"
            entry["Uso"] = "CONSTANTE"

        self.symbols[self.next_id] = entry
        self.next_id += 1

    def add_negative_token(self, positive_lexema, negative_value):
        negative_lexema = str(negative_value)
        entry = self.get_token(positive_lexema)
        if entry:
            copied = entry.copy()
            copied["Lexema"] = negative_lexema
            copied["value"] = negative_value
            copied["ID"] = self.next_id
            self.symbols[self.next_id] = copied
            self.next_id += 1

    # ---------------------- FUNCIONES Y PARÁMETROS ----------------------
    def add_function(self, lexema, return_type, param_list):
        '''Registra una nueva función, incluyendo su tipo de retorno, y luego itera sobre la lista de parámetros para registrarlos individualmente con su tipo de dato y su Modificador (CV)'''
        
        func_entry = {
            "ID": self.next_id,
            "Lexema": lexema,
            "type": "FUNCTION",
            "data_type": return_type,
            "Uso": "FUNCION",
            "Funcion_Pertenencia": "N/A",
            "Modificador": "N/A",
            "Scope": "N/A",
            "parameters": param_list
        }
        self.symbols[self.next_id] = func_entry
        self.next_id += 1

        # Registrar parámetros
        for param in param_list:
            param_id = param[-1]
            param_type = param[-2]
            modificador = "N/A"
            if len(param) == 4 and param[1].lower() == "cv":
                modificador = "CV"

            entry = {
                "ID": self.next_id,
                "Lexema": param_id,
                "type": "ID",
                "data_type": param_type,
                "Uso": "PARAMETRO",
                "Funcion_Pertenencia": lexema,
                "Modificador": modificador,
                "Scope": "N/A"
            }
            self.symbols[self.next_id] = entry
            self.next_id += 1

    # ---------------------- SCOPES ----------------------
    def add_scope(self, lexema, data_type=None, uso="VARIABLE", scope="G"):
        entry = {
            "ID": self.next_id,
            "Lexema": lexema,
            "type": "ID",
            "data_type": data_type,
            "Uso": uso,
            "Funcion_Pertenencia": "N/A",
            "Modificador": "N/A",
            "Scope": scope
        }
        self.symbols[self.next_id] = entry
        self.next_id += 1

    def actualizar_scope_bloque_automatica(self, nombre_funcion, lista_tercetos, indice_inicio, indice_fin=None):
        if not lista_tercetos:
            return
        if indice_fin is None:
            indice_fin = len(lista_tercetos)

        for i in range(indice_inicio, indice_fin):
            terceto = lista_tercetos[i]
            if terceto.operador == 'DECL':
                val = terceto.op2
                tokens = self.find_by_lexema(val)
                for token in tokens:
                    if token["Uso"] == "VARIABLE":
                        current_scope = token.get("Scope", "G")
                        
                        # Dividir en partes y eliminar duplicados
                        parts = current_scope.split(':')
                        if nombre_funcion not in parts:
                            parts.insert(0, nombre_funcion)  # agregamos al inicio
                        token["Scope"] = ':'.join(parts)

    # ---------------------- UTILIDADES ----------------------
    def delete_token(self, lexema):
        to_delete = [k for k, v in self.symbols.items() if v.get("Lexema") == lexema]
        for key in to_delete:
            del self.symbols[key]

    def update_variable_type(self, lexema, data_type):
        '''Utilizado en el análisis semántico para asignar un tipo de dato concreto (INT, FLOAT) a una variable 
        después de que su declaración ha sido parseada.'''
        for entry in self.symbols.values():
            if entry["Lexema"] == lexema and entry["Uso"] in ["VARIABLE", "N/A"]:
                entry["data_type"] = data_type.upper()

    def get_token(self, lexema, uso_preferido=None):
        """Busca el símbolo por lexema (ignorando mayúsculas/minúsculas).
        Si hay duplicados, devuelve el más reciente o el que coincida con el uso preferido.
        """
        coincidencias = [
            entry for entry in self.symbols.values()
            if entry.get("Lexema", "").upper() == lexema.upper()
        ]
        if not coincidencias:
            return None

        if uso_preferido:
            for entry in reversed(coincidencias):  # reversed() = el más nuevo primero
                if entry.get("Uso") == uso_preferido:
                    return entry

        # si no hay uso preferido, devolvés el más nuevo
        return coincidencias[-1]

    def find_by_lexema(self, lexema):
        """Retorna una lista de todas las entradas con ese lexema."""
        return [v for v in self.symbols.values() if v["Lexema"] == lexema]

    def get_data_type(self, lexema):
        entry = self.get_token(lexema)
        return entry["data_type"] if entry else None
    
    def eliminar(self, tercetos=None):
        """
        Elimina:
        1. Variables tipo ID, uso VARIABLE, que tengan 'N/A' en Scope.
        2. Constantes duplicadas (deja solo una).
        3. Variables duplicadas (mismo Lexema y Scope).
        4. Variables tipo ID duplicadas por Lexema (aunque tengan Scope distinto).
        
        Guarda en self.duplicadas_scope entradas completas (ID_original, ID_eliminado, entry_original, entry_eliminado)
        para que la verificación posterior tenga toda la información.

        Adicional: guarda todas las variables tipo ID sin duplicados en self.variables_list
        con toda su información.
        """
        ids_a_eliminar = []
        self.duplicadas_scope = []       # lista final con detalles completos
        self.variables_list = {}         # dict para variables únicas: clave=(lexema,scope), valor=entry completo
        vistos_constantes = {}
        vistos_variables_scope = {}      # para duplicados por Lexema+Scope
        vistos_lexema = {}               # para duplicados solo por Lexema

        for sym_id, entry in list(self.symbols.items()):
            tipo = entry.get("type")
            uso = entry.get("Uso")
            lexema = entry.get("Lexema")
            scope = entry.get("Scope")

            # --- 1. Variables sin scope válido ---
            if tipo == "ID" and uso == "VARIABLE" and (not scope or "N/A" in str(scope).upper()):
                ids_a_eliminar.append(sym_id)
                continue

            # --- 2. Constantes duplicadas ---
            if (tipo and tipo.startswith("CONST")) or (uso and uso.upper() == "CONSTANTE"):
                if lexema in vistos_constantes:
                    ids_a_eliminar.append(sym_id)
                else:
                    vistos_constantes[lexema] = sym_id
                continue

            # --- 3. Variables duplicadas por Lexema+Scope ---
            if tipo == "ID" and uso and uso.upper() == "VARIABLE":
                clave_scope = (lexema, scope)
                if clave_scope not in self.variables_list:
                    self.variables_list[clave_scope] = entry.copy()

                if clave_scope in vistos_variables_scope:
                    id_original = vistos_variables_scope[clave_scope]
                    entry_original = self.symbols[id_original].copy()
                    entry_eliminado = entry.copy()
                    self.duplicadas_scope.append({
                        "Lexema": lexema,
                        "Scope": scope,
                        "ID_original": id_original,
                        "ID_eliminado": sym_id,
                        "entry_original": entry_original,
                        "entry_eliminado": entry_eliminado
                    })
                    ids_a_eliminar.append(sym_id)
                else:
                    vistos_variables_scope[clave_scope] = sym_id

                # --- 4. Variables duplicadas solo por Lexema ---
                if lexema in vistos_lexema:
                    id_original = vistos_lexema[lexema]
                    entry_original = self.symbols[id_original].copy()
                    entry_eliminado = entry.copy()
                    self.duplicadas_scope.append({
                        "Lexema": lexema,
                        "Scope": scope,
                        "ID_original": id_original,
                        "ID_eliminado": sym_id,
                        "entry_original": entry_original,
                        "entry_eliminado": entry_eliminado
                    })
                    ids_a_eliminar.append(sym_id)
                else:
                    vistos_lexema[lexema] = sym_id

        # Eliminar marcadas
        for sym_id in ids_a_eliminar:
            self.symbols.pop(sym_id, None)

        # Convertir dict a lista ordenada
        self.variables_list = list(self.variables_list.values())

        self.verificacion_scope(tercetos,self.variables_list)
        self.verifico_existencia(tercetos)
        self.validar_variables(tercetos)
        self.verificar_funciones(tercetos)

    # ---------------------- MOSTRAR TABLA ----------------------
    def show(self):
        result = "Tabla de Símbolos:\n"
        result += "-" * 120 + "\n"
        result += "{:<5} {:<15} {:<15} {:<10} {:<15} {:<20} {:<15} {:<10}\n".format(
            "ID", "Lexema", "Token Type", "Data Type", "Uso", "Función Pertenencia", "Modificador", "Scope"
        )
        result += "-" * 120 + "\n"

        for sym_id, entry in sorted(self.symbols.items()):
            result += "{:<5} {:<15} {:<15} {:<10} {:<15} {:<20} {:<15} {:<10}\n".format(
                str(entry.get("ID", sym_id) or "N/A"),
                str(entry.get("Lexema", "N/A") or "N/A"),
                str(entry.get("type", "N/A") or "N/A"),
                str(entry.get("data_type", "N/A") or "N/A"),
                str(entry.get("Uso", "N/A") or "N/A"),
                str(entry.get("Funcion_Pertenencia", "N/A") or "N/A"),
                str(entry.get("Modificador", "N/A") or "N/A"),
                str(entry.get("Scope", "N/A") or "N/A")
            )

        result += "-" * 120 + "\n"
        return result

    def verificacion_scope(self, tercetos, variables_list):
        """
        Verifica scopes de variables y funciones según los tercetos y la lista de variables tipo ID.
        Copia correctamente type y data_type desde los registros originales antes de eliminar.
        """

        nuevas_entradas = []

        # Diccionario rápido por Lexema para obtener la info original
        variables_dict = {v["Lexema"]: v for v in variables_list}

        scope_stack = ["G"]
        current_scope = "G"
        declaradas_por_scope = {"G": set()}

        # --- Paso 0: preparar mapping de type/data_type de la tabla actual ---
        type_mapping = {}
        for sym_id, entry in self.symbols.items():
            lex = entry.get("Lexema")
            type_mapping[lex] = {"type": entry.get("type", "ID"), "data_type": entry.get("data_type", "N/A")}

        # Recorremos los tercetos
        for idx, t in enumerate(tercetos):
            op = getattr(t, "operador", None)
            # --- FUNC: entramos a nuevo scope ---
            if op == "FUNC":
                func_name = str(t.op1)
                parent_scope = scope_stack[-1]
                current_scope = f"{func_name}:{parent_scope}" if parent_scope != "G" else func_name
                scope_stack.append(current_scope)

                # Tomar type y data_type desde type_mapping o default
                type_info = type_mapping.get(func_name, {"type": "FUNCTION", "data_type": "N/A"})
                entry_func = {
                    "ID": self.next_id,
                    "Lexema": func_name,
                    "type": type_info.get("type", "FUNCTION"),
                    "data_type": type_info.get("data_type", "N/A"),
                    "Uso": "FUNCION",
                    "Funcion_Pertenencia": parent_scope if parent_scope != "G" else "N/A",
                    "Modificador": "N/A",
                    "Scope": current_scope
                }
                nuevas_entradas.append(entry_func)
                self.next_id += 1
                declaradas_por_scope[current_scope] = set()
                continue

            # --- END_FUNC: salimos de scope ---
            if op == "END_FUNC":
                if len(scope_stack) > 1:
                    scope_stack.pop()
                current_scope = scope_stack[-1]
                continue

            # --- DECL: declaración de variable ---
            if op == "DECL":
                lexema = str(t.op2)
                scope_actual = current_scope

                # Revisar si fue declarada en este scope o ancestors
                is_redeclarada = False
                for scope in scope_stack:
                    if lexema in declaradas_por_scope.get(scope, set()):
                        is_redeclarada = True
                        msg = f"ERROR: Variable '{lexema}' redeclarada en scope '{scope}'"
                        self.error_manager.add(t.lineno, msg, source="Scope")
                        break

                if not is_redeclarada:
                    declaradas_por_scope.setdefault(scope_actual, set()).add(lexema)
                    # Tomar type y data_type del mapping o de variables_list
                    type_info = type_mapping.get(lexema, {"type": "ID", "data_type": "N/A"})
                    entry_var = {
                        "ID": self.next_id,
                        "Lexema": lexema,
                        "type": type_info.get("type", "ID"),
                        "data_type": type_info.get("data_type", "N/A"),
                        "Uso": "VARIABLE",
                        "Funcion_Pertenencia": current_scope.split(":")[1] if ":" in current_scope else "N/A",
                        "Modificador": "N/A",
                        "Scope": current_scope
                    }
                    nuevas_entradas.append(entry_var)
                    self.next_id += 1

        # --- Paso 1: eliminar registros viejos de las variables que estamos procesando ---
        lexemas_a_eliminar = [v["Lexema"] for v in variables_list]

        ids_a_eliminar = [
            sym_id
            for sym_id, e in self.symbols.items()
            if e.get("Lexema") in lexemas_a_eliminar and e.get("Uso", "").upper() == "VARIABLE"
        ]

        for sym_id in ids_a_eliminar:
            self.symbols.pop(sym_id, None)

        # --- Paso 2: agregar nuevas entradas ---
        for entry in nuevas_entradas:
            self.symbols[entry["ID"]] = entry

        #elimino funciones repetidas
        ids_a_eliminar = []
        for sym_id, entry in list(self.symbols.items()):
            if entry.get("Uso", "").upper() == "FUNCION" and entry.get("Scope", "").upper() == "N/A":
                ids_a_eliminar.append(sym_id)

        for sym_id in ids_a_eliminar:
            del self.symbols[sym_id]

    def validar_variables(self, tercetos):
        """
        Valida el uso de variables y parámetros en los tercetos:
        - Se ignoran DECL, PARAMETRO, CONST y referencias a otros tercetos.
        - Verifica IDs tipo VARIABLE o PARAMETRO según la tabla de símbolos.
        - current_scope indica el scope actual.
        - Variables globales son accesibles desde cualquier scope.
        - Parámetros son accesibles solo dentro de su función de pertenencia.
        """
        errores = []

        scope_stack = ["G"]
        current_scope = "G"

        def norm_scope(s):
            return str(s).strip() if s else ""

        def is_child_scope(parent, child):
            """True si 'child' es descendiente de 'parent'."""
            if parent == child:
                return False
            p_parts = parent.split(":")
            c_parts = child.split(":")
            return all(p in c_parts for p in p_parts) and len(c_parts) > len(p_parts)

        for idx, t in enumerate(tercetos):
            op = getattr(t, "operador", None)

            # Manejo de FUNC y END_FUNC
            if op == "FUNC":
                func_name = str(t.op1)
                parent_scope = scope_stack[-1]
                current_scope = f"{func_name}:{parent_scope}" if parent_scope != "G" else func_name
                scope_stack.append(current_scope)
                continue
            elif op == "END_FUNC":
                if len(scope_stack) > 1:
                    scope_stack.pop()
                current_scope = scope_stack[-1]
                continue

            # Ignorar declaraciones
            if op == "DECL":
                continue

            # Obtener posibles lexemas (VARIABLE o PARAMETRO)
            lexemas_validos = [
                e.get("Lexema") for e in self.symbols.values()
                if e.get("Uso", "").upper() in ("VARIABLE", "PARAMETRO")
            ]

            lexema = getattr(t, "op1", None)
            if lexema not in lexemas_validos:
                continue  # ignorar literales, constantes, referencias, etc.

            # Buscar coincidencias en la tabla de símbolos
            posibles = [
                e for e in self.symbols.values()
                if e.get("Lexema") == lexema and e.get("Uso", "").upper() in ("VARIABLE", "PARAMETRO")
            ]

            if not posibles:
                continue

            # Verificar accesibilidad
            uso_valido = False
            for e in posibles:
                scope_var = norm_scope(e.get("Scope"))
                uso = e.get("Uso", "").upper()

                # Variables globales siempre accesibles
                if uso == "VARIABLE" and scope_var == "G":
                    uso_valido = True
                    break

                # Variables locales accesibles en su scope o descendientes
                if uso == "VARIABLE" and (current_scope == scope_var or is_child_scope(scope_var, current_scope)):
                    uso_valido = True
                    break

                # Parámetros accesibles solo dentro de su función de pertenencia
                if uso == "PARAMETRO":
                    func_pert = e.get("Funcion_Pertenencia")
                    if func_pert and (func_pert == current_scope or current_scope.startswith(func_pert)):
                        uso_valido = True
                        break

            if not uso_valido:
                msg = f"ERROR: Variable o parámetro '{lexema}' no accesible desde scope '{current_scope}'."
                self.error_manager.add(t.lineno, msg, source="Scope")

    def verificar_funciones(self, tercetos):
        """
        Verifica funciones y parámetros:
        - Funciones globales no pueden repetirse.
        - Funciones internas pueden repetirse si están en distintos scopes padres.
        - Parámetros solo pueden usarse dentro de su función de pertenencia.
        - Ignora tercetos con operador '->'.
        - Si un nombre de parámetro es redefinido como variable en un scope interno, no se considera error.
        """
        scope_stack = ["G"]
        funciones_globales = set()  # nombres de funciones globales ya declaradas

        def norm_scope(s):
            return str(s).strip() if s else ""

        for idx, t in enumerate(tercetos):
            op = getattr(t, "operador", None)

            # --- Ignorar tercetos con '->' ---
            if op == "->":
                continue

            # --- Declaración de función ---
            if op == "FUNC":
                func_name = str(t.op1)
                parent_scope = scope_stack[-1]

                if parent_scope == "G":
                    # Función global duplicada
                    if func_name in funciones_globales:
                        msg = f"ERROR: Función global '{func_name}' ya declarada (terceto {idx})."
                        self.error_manager.add(t.lineno, msg, source="Scope")
                    else:
                        funciones_globales.add(func_name)
                else:
                    # Función interna duplicada en el mismo parent_scope
                    duplicada = any(
                        e.get("Lexema") == func_name and
                        e.get("Uso", "").upper() == "FUNCION" and
                        norm_scope(e.get("Scope")) == parent_scope
                        for e in self.symbols.values()
                    )
                    if duplicada:
                        msg = f"ERROR: Función '{func_name}' ya declarada en el scope '{parent_scope}' (terceto {idx})."
                        self.error_manager.add(t.lineno, msg, source="Scope")

                # Agregar nuevo scope
                internal_scope = f"{func_name}:{parent_scope}" if parent_scope != "G" else func_name
                scope_stack.append(internal_scope)

            elif op == "END_FUNC":
                if len(scope_stack) > 1:
                    scope_stack.pop()

            # --- Verificación de parámetros ---
            if op != "DECL":
                for attr in ["op1", "op2", "op3"]:
                    val = getattr(t, attr, None)
                    if not val:
                        continue

                    val_str = str(val)

                    # Buscar parámetros con ese lexema
                    parametros = [
                        e for e in self.symbols.values()
                        if e.get("Lexema") == val_str and e.get("Uso", "").upper() == "PARAMETRO"
                    ]
                    if not parametros:
                        continue  # no es parámetro, ignorar

                    # Buscar si hay una variable local con ese nombre (oculta el parámetro)
                    variable_local = any(
                        e.get("Lexema") == val_str and
                        e.get("Uso", "").upper() == "VARIABLE" and
                        any(s in norm_scope(e.get("Scope")) for s in scope_stack)
                        for e in self.symbols.values()
                    )
                    if variable_local:
                        continue  # hay una variable local con ese nombre, no es error

                    # Verificar que el parámetro se use dentro de su función de pertenencia
                    valido = False
                    for p in parametros:
                        funcion_pert = p.get("Funcion_Pertenencia")
                        if any(funcion_pert == s.split(":")[0] or funcion_pert == s for s in scope_stack):
                            valido = True
                            break

                    if not valido:
                        msg = f"ERROR: Parámetro '{val_str}' usado fuera de su función '{parametros[0].get('Funcion_Pertenencia')}'."
                        self.error_manager.add(t.lineno, msg, source="Scope")


    def verifico_existencia(self, tercetos):
        """
        Verifica que los identificadores usados en los tercetos existan en la tabla de símbolos.
        Regla:
        - Si el valor contiene letras mayúsculas (ej: 'U', 'W', 'Z', 'ABC'),
            se considera un posible identificador (variable o parámetro).
        - Si no existe en la tabla de símbolos con uso VARIABLE o PARAMETRO → error.
        - Ignora valores con corchetes (p.ej. [9]) o que no sean cadenas.
        """
        for idx, t in enumerate(tercetos):
            op = getattr(t, "operador", None)
            if op == "->":  # ignorar redirecciones
                continue

            for attr in ["op1", "op2", "op3"]:
                val = getattr(t, attr, None)
                if not val or not isinstance(val, str):
                    continue

                # Ignorar valores tipo [9] o constantes numéricas
                if "[" in val or "]" in val or val.replace('.', '', 1).isdigit():
                    continue
                
                if any(c.isupper() for c in val):
                    # Ignorar cadenas entre comillas dobles
                    if val.startswith('"') and val.endswith('"'):
                        continue

                # Solo analizamos lexemas que tienen al menos una mayúscula (ej: U, W, Z)
                if any(c.isupper() for c in val):
                    # Buscar en la tabla de símbolos si existe como VARIABLE o PARAMETRO
                    existe = any(
                        e.get("Lexema") == val and
                        e.get("Uso", "").upper() in ("VARIABLE", "PARAMETRO", "FUNCION")
                        for e in self.symbols.values()
                    )

                    if not existe:
                        msg = f"ERROR: Identificador '{val}' no está declarado."
                        self.error_manager.add(t.lineno, msg, source="Scope")