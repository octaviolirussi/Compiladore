from sly import Lexer
from tablaSimbolos import SymbolTable
from colorama import Fore, Style

symbol_Table = SymbolTable() 

class MyLexer(Lexer):
    

    def __init__(self):
        self.lineno = 1


    # Lista de tokens
    tokens = { ID, UMINUS, CONST_INT, CONST_FLOAT, NUMBER, GE, LE, GT, LT, EQ, NE
              , ARROW, STRING, RESERVED, IF, ELSE, ENDIF, PRINT, RETURN, WHILE, DO, FLOAT
              ,INT, CV}
   
    literals = { '+', '-', '*', '/', '=', '>', '<',
                 '(', ')', '{', '}', '_', ';', ',', ';' }

    ignore = ' \t'

    #Ignore new line
    ignore_newline = r'\n+'


    # TODO revisar que no haga conflictos con lo de UMINUS
    # Reglas de tokens
    RESERVED    = r'[a-z]+' 
    ID          = r'[A-Z][A-Z0-9%]{0,}'
    UMINUS       = r'-'
    CONST_INT   = r'\d+I'
    CONST_FLOAT = r'((\d+\.\d*)|(\d*\.\d+))(F[+-]\d+)?'
    EQ          = r'=='
    GE          = r'>='
    LE          = r'<='
    NE          = r'!='
    ARROW       = r'->'
    STRING      = r'"[^"\n]*"'

    # Palabras reservadas
    RESERVED['if']     = IF
    RESERVED['else']   = ELSE
    RESERVED['endif']  = ENDIF
    RESERVED['print']  = PRINT
    RESERVED['return'] = RETURN
    RESERVED['while']  = WHILE
    RESERVED['do']     = DO
    RESERVED['float']  = FLOAT
    RESERVED['int']    = INT
    RESERVED['cv']     = CV

    def print_color(self,msg):
        print(Fore.YELLOW + msg + Style.RESET_ALL)

    #Track line number
    @_(r'\n+')
    def ignore_newline(self,t):
        self.lineno += len(t.value)

    #Ignora comentarios y cuenta lineas
    @_(r'##(.|\n| )*?##')
    def comments(self,t):
         self.lineno += t.value.count('\n')
         pass
    
    #Acciones semanticas
    
    #ID
    @_(r'[A-Z][A-Z0-9%]{0,}')
    def ID(self, t):
        max_length = 20

    # Truncar si excede longitud máxima
        if len(t.value) > max_length:
            msg = f"Warning: Identificador '{t.value}' truncado a {max_length} caracteres (línea {self.lineno})"
            self.print_color(msg)
            t.value = t.value[:max_length]

        # Agregar a la tabla de simbolos
        symbol_Table.add_token(t.value, "ID")
        t.lineno = self.lineno
        return t

    #CONST_INT
    @_(r'\d+I')
    def CONST_INT(self,t):
        #Verifico rangos
        numero = int(t.value[:-1])
        if (numero >= -2**15 and numero <= 2**15): #2**15-1
            # Agregar a la tabla de simbolos
            t.value = t.value[:-1]
            symbol_Table.add_token(t.value, "CONST_INT")
            return t
        else:
            msg = f"Warning: Constante entera fuera de rango (linea {self.lineno})"
            self.print_color(msg)
            return None

    #CONST_FLOAT
    @_(r'((\d+\.\d*)|(\d*\.\d+))(F[+-]\d+)?')
    def CONST_FLOAT(self,t):
        #Verifico rangos
        if 'F' in t.value.upper():
            partes = t.value.split('F')
            base = float(partes[0])
            exponente = int(partes[1])
            numero = base * (10 ** exponente)
        else:
            numero = float(t.value)
        if numero >= 1.17549435**(-38) and numero <= 3.40282347**38:
            # Agregar a la tabla de simbolos
            t.value = t.value.replace('F', 'E')  # cambia "F" por "E"
            symbol_Table.add_token(t.value, "CONST_FLOAT")  
            return t
        else:
            msg = f"Warning: Constante flotante fuera de rango (linea {self.lineno})"
            self.print_color(msg)
            return None

    #STRING
    @_(r'"[^"\n]*"')
    def STRING(self,t):
        # Agregar a la tabla de simbolos
        symbol_Table.add_token(t.value, "STRING")
        return t

    #Palabra reservada no encontrada
    @_(r'[a-z]+')
    def RESERVED(self,t):
        if t.value not in symbol_Table.keywords:
            msg = f"Warning: Palabra reservada {t.value} no encontrada (linea {self.lineno})"
            self.print_color(msg)
            return None
        
    @_(r'\d+')
    def NUMBER(self,t):
        msg = f"Warning: Número {t.value} sin sufijo (línea {self.lineno})"
        self.print_color(msg)
        return None
    
    # Caracteres ilegales
    def error(self, t):
        
        msg = f"Warning: Carácter ilegal '{t.value[0]}' (línea {self.lineno})"
        self.print_color(msg)
        self.index += 1  # Avanza solo un carácter para continuar
   