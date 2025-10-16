from sly import Lexer 
from tablaSimbolos import SymbolTable
    
class MyLexer(Lexer):

  
    def __init__(self, symbol_table):
        self.lineno = 1
        self.symbol_table = symbol_table
        self.comment_start_lineno = 0 
        self.state = 'INITIAL'
        
    # Lista de tokens (se mantiene igual)
    tokens = { ID, CONST_INT, CONST_FLOAT, GE, LE, EQ, NE
               , ARROW, STRING, RESERVED, IF, ELSE, ENDIF, PRINT, RETURN, WHILE, DO, FLOAT
               ,INT, CV, UMINUS}
    
    literals = { '+', '-', '*', '/', '=', '>', '<',
                 '(', ')', '{', '}', '_', ';', ',', ';' }

    ignore = ' \t'

    # Reglas de tokens (se mantienen igual)
    RESERVED      = r'[a-z]+' 
    ID            = r'[A-Z][A-Z0-9%]{0,}'
    CONST_INT     = r'\d+I'
    CONST_FLOAT   = r'((\d+\.\d*)|(\d*\.\d+))(F[+-]\d+)?'
    EQ            = r'=='
    GE            = r'>='
    LE            = r'<='
    NE            = r'!='
    ARROW         = r'->'
    STRING        = r'"[^"\n]*"'

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


    # Track line number (fuera de comentarios)
    @_(r'\n+')
    def ignore_newline(self,t):
        self.lineno += len(t.value)
        
    @_(r'##.*?##')
    def ignore_comment(self,t):
        self.state = 'comment'
        self.comment_start_lineno = self.lineno
   
    # --- ACCIONES SEMÁNTICAS (Mantienen el @_ decorador) ---
 #ID
    @_(r'[A-Z][A-Z0-9%]{0,}')
    def ID(self, t):
        if self.state == 'INITIAL':
            max_length = 20

        # Truncar si excede longitud máxima
            if len(t.value) > max_length:
                msg = f"Warning: Identificador '{t.value}' truncado a {max_length} caracteres (línea {self.lineno})"
                self.print_color(msg)
                t.value = t.value[:max_length]

            # Agregar a la tabla de simbolos
            self.symbol_table.add_token(t.value, "ID")
            t.lineno = self.lineno
            return t

    #CONST_INT
    @_(r'\d+I')
    def CONST_INT(self,t):
        #Verifico rangos
        if self.state == 'INITIAL':
            MAX_INT = 32767+1 
            t.value = t.value[:-1]
            if (int(t.value) >= 0 and int(t.value) <= MAX_INT):
                self.symbol_table.add_token(t.value, "CONST_INT")
                
            else:
                # Pongo el límite para que no corte la ejecución
                msg = f"Warning: Constante entera fuera de rango (linea {self.lineno}). Se usará el límite."
                print(msg)
                t.value = MAX_INT
                self.symbol_table.add_token(t.value, "CONST_INT")
            return t    

    #CONST_FLOAT
    @_(r'((\d+\.\d*)|(\d*\.\d+))(F[+-]\d+)?')
    def CONST_FLOAT(self,t):
        #Verifico rangos positivos
        if self.state == 'INITIAL':
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
                msg = f"Warning: Constante entera {numero} fuera de rango (linea {self.lineno}). Se usará {MIN_FLOAT_POSITIVO}."
                print(msg)
                t.value = MIN_FLOAT_POSITIVO
                self.symbol_table.add_token(str(t.value), "CONST_FLOAT") 
                
            elif numero > MAX_FLOAT_POSITIVO:
                # Pongo el límite para que no corte la ejecución
                msg = f"Warning: Constante entera {numero} fuera de rango (linea {self.lineno}). Se usará {MAX_FLOAT_POSITIVO}."
                print(msg)
                t.value = MAX_FLOAT_POSITIVO   
                self.symbol_table.add_token(str(t.value), "CONST_FLOAT")   
                    
            else: 
                self.symbol_table.add_token(str(t.value), "CONST_FLOAT")  
            
            t.lineno = self.lineno
            return t

    #STRING
    @_(r'"[^"\n]*"')
    def STRING(self,t):
        # Agregar a la tabla de simbolos
        if self.state == 'INITIAL':
            self.symbol_table.add_token(t.value, "STRING")
            return t

    #Palabra reservada no encontrada
    @_(r'[a-z]+')
    def RESERVED(self,t):
        if self.state == 'INITIAL':
            if t.value not in self.symbol_table.keywords:
                msg = f"Warning: Palabra reservada {t.value} no encontrada (linea {self.lineno})"
                print(msg)
                return None
        
    @_(r'\d+')
    def NUMBER(self,t):
        if self.state == 'INITIAL':
            msg = f"Warning: Número {t.value} sin sufijo (línea {self.lineno})"
            print(msg)
            return None
    
    # Caracteres ilegales
    def error(self, t):
        if self.state == 'INITIAL':
            msg = f"Warning: Carácter ilegal '{t.value[0]}' (línea {self.lineno})"
            print(msg)
            self.index += 1  # Avanza solo un carácter para continuar
       
    # --- EOF para detectar un comentario sin cerrar ---

# def eof(self):
#         # El estado actual es solo el string (e.g., 'comment'), no la clase.
#         if self.state == 'comment':
#             msg = (f"{Fore.YELLOW}Warning:{Style.RESET_ALL} Comentario abierto '##' en línea "
#                    f"{self.comment_start_lineno} no fue cerrado. Cerrado implícitamente por EOF.")
#             print(msg)
#             return None
#         return None
    
