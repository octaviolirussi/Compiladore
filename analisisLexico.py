from sly import Lexer
# un cambio
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
    ID          = r'[A-Z][A-Z0-9%]{0,19}'
    CONST_INT   = r'\d+I'
    CONST_FLOAT = r'((\d+\.\d*)|(\d*\.\d+))(F[+-]\d+)?'
    RESERVED    = r'if|else|endif|print|return|while|do'
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


    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t
    
    #Track line number
    @_(r'\n+')
    def ignore_newline(self,t):
        self.lineno += len(t.value)
    
    #Acciones semanticas
    #ID
    

    # Manejo de errores
    def error(self, t):
        print(f"Carácter ilegal '{t.value[0]}'")
        self.index += 1


if __name__ == '__main__':
    lexer = MyLexer()
    # Abrimos el archivo en modo lectura ('r')
    with open("caso1.txt", "r", encoding="utf-8") as f:
        text = f.read()  # lee todo el contenido
    for tok in lexer.tokenize(text):
        print('type=%r, value=%r' % (tok.type, tok.value))