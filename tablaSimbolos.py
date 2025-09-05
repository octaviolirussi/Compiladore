class SymbolTable:

    
    symbols = {}
    keywords = {}

    def load_keyword(self):
        self.keywords = {
            "if": "IF",
            "else": "ELSE",
            "endif": "ENDIF",
            "print": "PRINT",
            "return": "RETURN",
            "while" : "WHILE",
            "do" : "DO",
            "float": "FLOAT"
        }

    def add_token(self, lexema, token_type=None):
        if lexema in self.symbols:
            print(f"Warning: Identificador '{lexema}' ya declarado")
        else:
            self.symbols.update({lexema:token_type})
            

    #def update_token(self, lexema, value):
    #    if lexema in self.symbols:
    #        self.symbols[lexema]["value"] = value
    #    else:
    #        print(f"Error: Identificador '{lexema}' no declarado")

    def get_token(self, lexema):
        return self.symbols.get(lexema, None)

    def show(self):
        result = "Tabla de Símbolos:\n"
        for lexema, token in self.symbols.items():
            result += f"{lexema} -> {token}\n"
        return result