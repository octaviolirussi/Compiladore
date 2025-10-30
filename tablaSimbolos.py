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
            Agrega un lexema. Para constantes, registra el tipo de dato y Uso='CONSTANTE'.
            Para IDs, registra el tipo de token (ID).
            """
            if lexema not in self.symbols:
                entry = {"type": token_type, "Uso": "VARIABLE"} # Por defecto, asumimos variable para ID
                data_type = None

                if token_type == "CONST_INT":
                    data_type = "INT"
                    entry["Uso"] = "CONSTANTE" # Uso para constantes
                elif token_type == "CONST_FLOAT":
                    data_type = "FLOAT"
                    entry["Uso"] = "CONSTANTE" # Uso para constantes

                entry["data_type"] = data_type
                self.symbols[lexema] = entry
    
    def add_negative_token(self, positive_lexema, negative_value):
        negative_lexema = str(negative_value)
        
        entry = self.symbols.get(positive_lexema)
        
        if entry:
            self.symbols[negative_lexema] = entry.copy()
            self.symbols[negative_lexema]['value'] = negative_value
            
    def add_function(self, lexema, return_type, param_list):
            """
            Agrega la función y registra sus parámetros.
            La función usa 'param_list' que es una lista de tuplas de parámetros.
            """
            entry = {
                "type": "FUNCTION",              
                "data_type": return_type,
                "Uso": "FUNCION",        
                "parameters": param_list         
            }
            self.symbols[lexema] = entry 
            
            for param in param_list:
                # La tupla de parámetro puede ser:
                # ('param', <tipo>, <ID>) O ('param', <CV>, <tipo>, <ID>)
                
                # Obtener el nombre (ID) y el tipo de dato del parámetro
                param_id = param[-1]    # Siempre es el último elemento
                
                # El tipo está en la penúltima posición si no hay 'CV', o antepenúltima si hay 'CV'
                # Dada la estructura: ('param', type, ID) o ('param', CV, type, ID)
                # El tipo es param[-2]
                param_type = param[-2]  

                # Registrar el parámetro como ID en la tabla.
                # TODO ACA SEGURO HAYA QUE VER LO DE LOS AMBITOS
                if param_id not in self.symbols or self.symbols[param_id].get("type") == "ID":
                    '''"F3": {
                            "type": "FUNCTION",
                            "data_type": "int",
                            "parameters": [
                                ('param', 'int', 'W'), 
                                ('param', 'int', 'Z')
                            ]
                    }'''
                    self.symbols[param_id] = {
                        "type": "ID", 
                        "data_type": param_type,
                        "Uso": "PARAMETRO"}
                    

    def delete_token(self, lexema):
        if lexema in self.symbols:
            self.symbols.pop(lexema) 

            
    def update_token(self, lexema, new_value):
        new_lexema = str(new_value) 
        
        if lexema in self.symbols:
            entry = self.symbols.pop(lexema) 
            
            self.symbols[new_lexema] = entry
            
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
            # Aumentar la longitud de la línea de separación
            result += "---------------------------------------------------------\n"
            
            # Nuevo encabezado con la columna 'Uso'
            result += "{:<15} {:<15} {:<10} {:<15}\n".format("Lexema", "Token Type", "Data Type", "Uso") 
            result += "---------------------------------------------------------\n"
            
            for lexema, entry in self.symbols.items():
                token_type = entry.get("type", "N/A")
                data_type = entry.get("data_type", "N/A") if entry.get("data_type") else "N/A"
                uso = entry.get("Uso", "N/A") # Extraer el nuevo atributo 'Uso'
                
                # Formatear la nueva fila, incluyendo 'Uso'
                result += "{:<15} {:<15} {:<10} {:<15}\n".format(lexema, token_type, data_type, uso)
                
            result += "---------------------------------------------------------\n"
            return result