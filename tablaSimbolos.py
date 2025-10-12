from colorama import Fore, Style

class SymbolTable:
    
    def __init__(self):
        self.symbols = {}  # {lexema_key: {"type": token_type, "value": lexema}}
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

    def print_color(self,msg):
        print(Fore.YELLOW + msg + Style.RESET_ALL)

    def add_token(self, lexema, token_type=None):
        if lexema not in self.symbols:
            self.symbols.update({lexema:token_type})
    
    def add_negative_token(self, positive_lexema, negative_value):
        negative_lexema = str(negative_value)
        
        token_type = self.symbols.get(positive_lexema)
        
        if token_type:
            self.symbols[negative_lexema] = token_type
        else:
            self.print_color(f"Warning: El lexema positivo '{positive_lexema}' no existe en la tabla de símbolos para añadir su contraparte negativa.")

    def delete_token(self, lexema):
        if lexema in self.symbols:
            # Sacar la clave positiva
            token_type = self.symbols.pop(lexema) 
        else:
            self.print_color(f"Warning: El lexema '{lexema}' no existe en la tabla de símbolos para eliminar.")
            
    def update_token(self, lexema, new_value):
        # self.add_negative_token(lexema, new_value) 
        
        new_lexema = str(new_value) 
        
        if lexema in self.symbols:
            token_type = self.symbols.get(lexema)
            self.symbols.update({new_lexema: token_type}) 
        else:
            self.print_color(f"Warning: El lexema '{lexema}' no existe en la tabla de símbolos para actualizar.")

        
    def get_token(self, lexema):
        return self.symbols.get(lexema, None)
 
    def show(self):
        result = "Tabla de Símbolos:\n"
        for lexema, token in self.symbols.items():
            result += f"{lexema} -> {token}\n"
        return result