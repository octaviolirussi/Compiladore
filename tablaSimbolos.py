class SymbolTable:

    def __init__(self):
        self.symbols = {}
        self.keywords = {}

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
            self.symbols[lexema] = {
                "type": token_type,
            }

    #def update_token(self, lexema, value):
    #    if lexema in self.symbols:
    #        self.symbols[lexema]["value"] = value
    #    else:
    #        print(f"Error: Identificador '{lexema}' no declarado")

    def get_token(self, lexema):
        return self.symbols.get(lexema, None)

    def __str__(self):
        result = "Tabla de Símbolos:\n"
        for lexema, info in self.symbols.items():
            result += f"{lexema} -> {info}\n"
        return result