class SymbolTable:
    
    def __init__(self):
        # Estructura: {id: {...datos...}}
        self.symbols = {}
        self.keywords = {}
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
                        token["Scope"] = f"{nombre_funcion}:{current_scope}"

    # ---------------------- UTILIDADES ----------------------
    def delete_token(self, lexema):
        to_delete = [k for k, v in self.symbols.items() if v.get("Lexema") == lexema]
        for key in to_delete:
            del self.symbols[key]

    def update_variable_type(self, lexema, data_type):
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
    
    def eliminar_variables_no_declaradas(self):
        """Elimina tokens tipo ID, uso VARIABLE, que tengan 'N/A' en el campo Scope (en cualquier parte)."""
        ids_a_eliminar = []

        for sym_id, entry in self.symbols.items():
            tipo = entry.get("type")
            uso = entry.get("Uso")
            scope = entry.get("Scope")

            # Verifica si es una variable ID con 'N/A' en el scope
            if tipo == "ID" and uso == "VARIABLE" and scope and "N/A" in str(scope).upper():
                ids_a_eliminar.append(sym_id)

        # Eliminar los símbolos luego de recorrer (para evitar modificar el diccionario durante la iteración)
        for sym_id in ids_a_eliminar:
            self.symbols.pop(sym_id, None)

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
