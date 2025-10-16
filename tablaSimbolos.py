class SymbolTable:
    
    def __init__(self):
        # Estructura de símbolos: {lexema: {"type": "ID" | "CONST_INT" | "CONST_FLOAT", "data_type": "INT" | "FLOAT" | None}}
        self.symbols = {} 
        self.keywords = {}
        self.load_keyword() # Load keywords upon creation

    def load_keyword(self):
        self.keywords = {
            "if": "IF",
            "else": "ELSE",
            "endif": "ENDIF",
            "print": "PRINT",
            "return": "RETURN",
            "while" : "WHILE",
            "do" : "DO",
            "float": "FLOAT",
            "int" : "INT",
            "cv" : "CV"
        }

    def add_token(self, lexema, token_type):
        """
        Agrega un lexema. Para constantes, registra el tipo de dato.
        Para IDs, registra el tipo de token (ID).
        """
        if lexema not in self.symbols:
            entry = {"type": token_type}
            data_type = None

            if token_type == "CONST_INT":
                data_type = "INT"
            elif token_type == "CONST_FLOAT":
                data_type = "FLOAT"

            entry["data_type"] = data_type
            self.symbols[lexema] = entry
    
    def add_negative_token(self, positive_lexema, negative_value):
        negative_lexema = str(negative_value)
        
        entry = self.symbols.get(positive_lexema)
        
        if entry:
            self.symbols[negative_lexema] = entry.copy()
            self.symbols[negative_lexema]['value'] = negative_value
        else:
            print(f"Warning: El lexema positivo '{positive_lexema}' no existe en la tabla de símbolos para añadir su contraparte negativa.")

    def delete_token(self, lexema):
        if lexema in self.symbols:
            self.symbols.pop(lexema) 
        else:
            print(f"Warning: El lexema '{lexema}' no existe en la tabla de símbolos para eliminar.")
            
    def update_token(self, lexema, new_value):
        new_lexema = str(new_value) 
        
        if lexema in self.symbols:
            entry = self.symbols.pop(lexema) 
            
            self.symbols[new_lexema] = entry
        else:
            print(f"Warning: El lexema '{lexema}' no existe en la tabla de símbolos para actualizar.")
            
    def get_token(self, lexema):
        """Retorna el diccionario de atributos asociado al lexema."""
        return self.symbols.get(lexema, None)
    
    def get_data_type(self, lexema):
        """Método de conveniencia para obtener el tipo de dato."""
        entry = self.symbols.get(lexema)
        if entry:
            return entry.get("data_type")
        return None

    def show(self):
        result = "Tabla de Símbolos:\n"
        result += "----------------------------------------------\n"
        result += "{:<15} {:<15} {:<10}\n".format("Lexema", "Type", "Data Type")
        result += "----------------------------------------------\n"
        for lexema, entry in self.symbols.items():
            token_type = entry.get("type", "N/A")
            data_type = entry.get("data_type", "N/A") if entry.get("data_type") else "N/A"
            result += "{:<15} {:<15} {:<10}\n".format(lexema, token_type, data_type)
        result += "----------------------------------------------\n"
        return result