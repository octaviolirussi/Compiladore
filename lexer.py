from sly import Lexer 
from tablaSimbolos import SymbolTable
from errorManager import ErrorManager

class MyLexer(Lexer):
    
    def __init__(self,symbol_table,error_manager):
        self.lineno = 1
        self.symbol_table = symbol_table
        self.error_manager = error_manager


    # Lista de tokens
    tokens = { PROGRAMA, ID, CONST_INT, CONST_FLOAT, GE, LE, EQ, NE
              , ARROW, STRING, RESERVED, IF, ELSE, ENDIF, PRINT, RETURN, WHILE, DO, FLOAT
              ,INT, CV}
   
    literals = { '+', '-', '*', '/', '=', '>', '<',
                 '(', ')', '{', '}', '_', ';', ',', ';' }

    ignore = ' \t'


    #Ignore new line
    ignore_newline = r'\n+'

    # Reglas de tokens
    RESERVED    = r'[a-z]+' 
    ID          = r'[A-Z][A-Z0-9%]{0,}'
    CONST_INT   = r'\d+I'
    CONST_FLOAT = r'((\d+\.\d*)|(\d*\.\d+))(F[+-]\d+)?'
    EQ          = r'=='
    GE          = r'>='
    LE          = r'<='
    NE          = r'!='
    ARROW       = r'->'
    STRING      = r'"[^"\n]*"'

    # Palabras reservadas (se mantiene igual)
    RESERVED['if']      = IF
    RESERVED['else']    = ELSE
    RESERVED['endif']   = ENDIF
    RESERVED['print']   = PRINT
    RESERVED['return']  = RETURN
    RESERVED['while']   = WHILE
    RESERVED['do']      = DO
    RESERVED['float']   = FLOAT
    RESERVED['int']     = INT
    RESERVED['cv']      = CV

    #Track line number
    @_(r'\n+')
    def ignore_newline(self,t):
        self.lineno += len(t.value)

    # #Ignora comentarios y cuenta lineas
    @_(r'##(.|\n| )*?##')
    def comments(self,t):
        self.lineno += t.value.count('\n')
        pass
    
    # --- comentarios sin cierre hasta EOF ---
    @_('##(.|\\n)*')
    def unclosed_comment(self, t):
        # se llegó al fin de archivo sin otro ##
        self.lineno += t.value.count('\n')
        msg = "Warning: comentario iniciado nunca se cerró con '##'"
        self.error_manager.add(t.lineno,msg,source="lexer")
        pass

    #Acciones semanticas
    
    #ID
    @_(r'[A-Z][A-Z0-9%]{0,}')
    def ID(self, t):
        max_length = 20

        if 'PROGRAMA' in t.value:
            t.type = 'PROGRAMA' # Cambiar el tipo de token a PROGRAMA
            self.symbol_table.add_token(t.value, "PROGRAMA")
            return t
    
        # Truncar si excede longitud máxima
        if len(t.value) > max_length:
            msg = f"Warning: Identificador '{t.value}' truncado a {max_length} caracteres"
            self.error_manager.add(t.lineno,msg,source="lexer")
            t.value = t.value[:max_length]

        # Agregar a la tabla de simbolos
        self.symbol_table.add_token(t.value, "ID")
        self.symbol_table.add_token(t.value, "ID")
        t.lineno = self.lineno
        return t

    #STRING
    @_(r'"[^"\n]*"')
    def STRING(self,t):
        # Agregar a la tabla de simbolos
        self.symbol_table.add_token(t.value, "STRING")
        return t
    
    @_('"[^"\n]*\n')
    def UNCLOSED_STRING(self, t):
        self.lineno += 1
        msg = "Warning: cadena sin cierre antes de salto de línea"
        self.error_manager.add(t.lineno, msg, source="lexer")
        return None

    #CONST_INT
    @_(r'\d+I')
    def CONST_INT(self,t):
        #Verifico rangos
        MAX_INT = 32767+1 
        t.value = t.value[:-1]
        if (int(t.value) >= 0 and int(t.value) <= MAX_INT):
            self.symbol_table.add_token(t.value, "CONST_INT")
                
        else:
            # Pongo el límite para que no corte la ejecución
            msg = f"Error: Constante entera fuera de rango. Se usará el límite."
            self.error_manager.add(t.lineno, msg, source="lexer")
            t.value = MAX_INT
            self.symbol_table.add_token(t.value, "CONST_INT")
        return t    

    #CONST_FLOAT
    @_(r'((\d+\.\d*)|(\d*\.\d+))(F[+-]\d+)?')
    def CONST_FLOAT(self,t):
    #Verifico rangos positivos
        MIN_FLOAT_POSITIVO = 1.17549435e-38
        MAX_FLOAT_POSITIVO = 3.40282347e38 
        if 'F' in t.value.upper():
            temp_value = t.value.replace('F', 'e') 
            numero = float(temp_value) 
            t.value = temp_value
                
        else:
            numero = float(t.value)

        if numero != 0.0 and numero < MIN_FLOAT_POSITIVO:
            # Pongo el límite para que no corte la ejecución
            msg = f"Error: Constante entera {numero} fuera de rango. Se usará {MIN_FLOAT_POSITIVO}."
            self.error_manager.add(t.lineno, msg, source="lexer")
            t.value = MIN_FLOAT_POSITIVO
            self.symbol_table.add_token(str(t.value), "CONST_FLOAT") 
                
        elif numero > MAX_FLOAT_POSITIVO:
            # Pongo el límite para que no corte la ejecución
            msg = f"Error: Constante entera {numero} fuera de rango. Se usará {MAX_FLOAT_POSITIVO}."
            self.error_manager.add(t.lineno, msg, source="lexer")
            t.value = MAX_FLOAT_POSITIVO   
            self.symbol_table.add_token(str(t.value), "CONST_FLOAT")   
                    
        else: 
            self.symbol_table.add_token(str(t.value), "CONST_FLOAT")  
            
        t.lineno = self.lineno
        return t

    #Palabra reservada no encontrada
    @_(r'[a-z]+')
    def RESERVED(self,t):
        if t.value not in self.symbol_table.keywords:
            msg = f"Warning: Palabra reservada {t.value} no encontrada"
            self.error_manager.add(t.lineno,msg,source="lexer")
            return None
        
    @_(r'\d+')
    def NUMBER(self,t):
        msg = f"Warning: Número {t.value} sin sufijo"
        self.error_manager.add(t.lineno,msg,source="lexer")
        return None
    
    # Caracteres ilegales
    def error(self, t):
        msg = f"Warning: Carácter ilegal '{t.value[0]}'"
        self.error_manager.add(t.lineno,msg,source="lexer")
        self.index += 1  # Avanza solo un carácter para continuar
  