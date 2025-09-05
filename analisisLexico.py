from sly import Lexer

# probando
class MyLexer(Lexer):

    def __init__(self):
        self.lineno = 1

    # Lista de tokens
    tokens = { ID, CONST_INT, CONST_FLOAT, NUMBER, PLUS, MINUS, TIMES, DIVIDE, ASSIGN, GE, LE, GT, LT, EQ, NE
              ,LPAREN, RPAREN, LBRACE, RBRACE, UNDERSCORE, SEMI, COMMA, ARROW, STRING, RESERVED, IF, ELSE, ENDIF, PRINT, RETURN, WHILE, DO}
    ignore = ' \t'
    
    # Comentarios
    ignore_comment = r'##(.|\n)*?##'

    #Ignore new line
    ignore_newline = r'\n+'

    # Reglas de tokens
    RESERVED    = r'if|else|endif|print|return|while|do|float' 
    ID          = r'[A-Z][A-Z0-9%]{0,}'
    CONST_INT   = r'\d+I'
    CONST_FLOAT = r'((\d+\.\d*)|(\d*\.\d+))(F[+-]\d+)?'
    PLUS        = r'\+'
    MINUS       = r'-'
    TIMES       = r'\*'
    DIVIDE      = r'/'
    EQ          = r'=='
    ASSIGN      = r'='
    GE          = r'>='
    LE          = r'<='
    NE          = r'=!'
    GT          = r'>'
    LT          = r'<'
    ARROW       = r'->'
    LPAREN      = r'\('
    RPAREN      = r'\)'
    LBRACE      = r'\{'
    RBRACE      = r'\}'
    UNDERSCORE  = r'_'
    SEMI        = r';'
    COMMA       = r','
    STRING      = r'"[^"\n]*"'

    # Palabras reservadas
    RESERVED['if']     = IF
    RESERVED['else']   = ELSE
    RESERVED['endif']  = ENDIF
    RESERVED['print']  = PRINT
    RESERVED['return'] = RETURN
    RESERVED['while']  = WHILE
    RESERVED['do']     = DO


    #Track line number
    @_(r'\n+')
    def ignore_newline(self,t):
        self.lineno += len(t.value)
    
    #Acciones semanticas
    #ID
    @_(r'[A-Z][A-Z0-9%]{0,}')
    def ID(self, t):
        max_length = 20
    
    # Truncar si excede longitud máxima
        if len(t.value) > max_length:
            print(f"Warning: Identificador '{t.value}' truncado a {max_length} caracteres (línea {self.lineno})")
            t.value = t.value[:max_length]

        t.lineno = self.lineno
        return t

    # Manejo de errores
    def error(self, t):
        print(f"Carácter ilegal '{t.value[0]}' en línea {self.lineno}")
        self.index += 1  # Avanza solo un carácter para continuar

if __name__ == '__main__':
    lexer = MyLexer()
    # Abrimos el archivo en modo lectura ('r')
    with open("caso1.txt", "r", encoding="utf-8") as f:
        text = f.read()  # lee todo el contenido
    for tok in lexer.tokenize(text):
        print('type=%r, value=%r' % (tok.type, tok.value))