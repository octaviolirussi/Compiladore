from sly import Parser
from tablaSimbolos import SymbolTable
from lexer import MyLexer

class MyParser(Parser):
    tokens = MyLexer.tokens
        
    precedence = (
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('right', UMINUS),
        )

# ===================================== PROGRAMA =====================================================

    @_('statement_list')
    def program(self, p):
        return ('program', p.statement_list)

    @_('statement_list statement')
    def statement_list(self, p):
        return p.statement_list + [p.statement]

    @_('statement')
    def statement_list(self, p):
        return [p.statement]
    

    #============================================ STATEMENT ===============================================

    #return
    @_('RETURN "(" expr ")" ";"')
    def statement(self, p):
        return (f"Linea {p.lineno} --> return", p.expr)

    #Asignacion
    @_('ID "=" expr ";"')
    def statement(self, p):
        return (f"Linea {p.lineno} --> assign", p.ID, p.expr)
    
    # Expresión como sentencia
    @_('expr ";"')
    def statement(self, p):
        return (f"Linea {p.lineno} --> expr_stmt", p.expr)
    
    # Declaraciones
    @_('type id_list ";"')
    def statement(self, p):
        return (f"Linea {p.lineno} --> declaration", p.type, p.id_list)
    
    #Prints
    @_('PRINT "(" expr ")" ";"')
    def statement(self, p):
        return (f"Linea: {p.lineno} --> print_expr", p.expr)
    
    @_('PRINT "(" STRING ")" ";"')
    def statement(self, p):
        return (f"Linea: {p.lineno} --> print_string", p.STRING)
    
    # 1. IF-ELSE statement (Handles single statement or block in both branches)
    @_('IF "(" expr ")" block ELSE  block ENDIF ";"')
    def statement(self, p): 
        if_body = p.block0
        else_body = (p.ELSE, p.block1) 
        
        return (f"Linea: {p.lineno} --> if_else_stmt:",p.IF,
                p.expr, if_body, else_body, p.ENDIF)

    # 2. IF-only statement (Handles single statement or block)
    @_('IF "(" expr ")" block ENDIF ";"')
    def statement(self, p): 
        return (f"Linea: {p.lineno} --> if_stmt:",p.IF, p.expr, p.block, p.ENDIF)
    
    #Function statement
    @_('type ID "(" param_list ")" block ')
    def statement(self, p):
        return (f"Linea: {p.lineno} --> func_stmt:", p.type, p.ID,p.param_list,p.block)
    
    #While statement
    @_('WHILE "(" expr ")" DO block')
    def statement(self, p):
        return (f"Linea: {p.lineno} --> while_stmt:", p.WHILE, p.expr, p.DO, p.block)
    
    #====================================== FUNCTION ===================================================

    # Lista de parametros
    @_('param_list "," param')
    def param_list(self, p):
        return p.param_list + [p.param]

    @_('param')
    def param_list(self, p):
        return [p.param]
    
    # Item individual: con o sin modificador
    @_('CV type ID')
    def param(self, p):
        return ('param', p.CV, p.type, p.ID)

    @_('type ID')
    def param(self, p):
        return ('param', None, p.type, p.ID)
    
    #====================================== BLOCKS ====================================================

    @_('"{" statement_list "}"')
    def block(self, p):
        return p.statement_list 

    @_('statement')
    def block(self, p):
        return [p.statement]
    
    #====================================== LISTS ======================================================

    # Lista de IDs
    @_('id_list "," ID')
    def id_list(self, p):
        return p.id_list + [p.ID]

    @_('ID')
    def id_list(self, p):
        return [p.ID]
    
    #======================================== FUNC CALL ===================================================
    #invocacion funcion
    @_('ID "(" arg_list ")"')
    def expr(self, p):
        return ('func_call', p.ID, p.arg_list)

    # Lista de argumentos
    @_('arg_list "," arg')
    def arg_list(self, p):
        return p.arg_list + [p.arg]

    @_('arg')
    def arg_list(self, p):
        return [p.arg]
    
    # Argumento tipo expr -> ID
    @_('expr ARROW ID')
    def arg(self, p):
        return ('arrow', p.expr, p.ID)
    
    # ===================================== EXPRESIONES =================================================

    @_('expr "+" expr')
    def expr(self, p):
        return ('suma', p.expr0, p.expr1)

    @_('expr "-" expr')
    def expr(self, p):
        return ('resta', p.expr0, p.expr1)

    @_('expr "*" expr')
    def expr(self, p):
        return ('multiplicacion', p.expr0, p.expr1)

    @_('expr "/" expr')
    def expr(self, p):
        return ('division', p.expr0, p.expr1)
    
    @_('expr ">" expr')
    def expr(self, p):
        return ('mayor', p.expr0, p.expr1)
    
    @_('expr "<" expr')
    def expr(self, p):
        return ('menor', p.expr0, p.expr1)
    
    @_('expr GE expr')  # >=
    def expr(self, p):  
        return ('mayor_igual', p.expr0, p.expr1)
    
    @_('expr LE expr') # <=
    def expr(self, p):
        return ('menor_igual', p.expr0, p.expr1)
    
    @_('expr EQ expr')  # ==
    def expr(self, p):  
        return ('igual', p.expr0, p.expr1)
    
    @_('expr NE expr') # !=
    def expr(self, p):
        return ('distinto', p.expr0, p.expr1)    
    
    @_('expr ARROW ID')
    def expr(self, p):
        return 'arg', p.expr, p.ID

    #================================= Tipos =================================================================================================
    @_('INT')
    @_('FLOAT')
    def type(self, p):
        return p[0]

    #======================== Primitivas de expresiones (variables y constantes) ========================================================
    @_('ID')
    def expr(self, p):
        return ('var', p.ID)

    @_('CONST_INT')
    def expr(self, p):
        
        return ('num_int', p.CONST_INT)
    
    # Manejo de enteros negativos con verificación de rango
    @_('UMINUS CONST_INT')
    def expr(self, p):
        signed_value = -int(p.CONST_INT)
        
        # Rango INT (16 bits): [-32768, 32767]
        MIN_INT = -32768 
        
        if signed_value < MIN_INT:
            # TODO son errores, no debe seguir ejecutando?
            msg = f"Error: Constante entera negativa {signed_value} fuera de rango (Línea {self.lineno}). Se usará el límite ({MIN_INT})."
            self.print_color(msg)
            final_value = MIN_INT
        else:
            final_value = signed_value

        # 3. Modificación de la Tabla de Símbolos. Registrar el valor negativo.
        symbol_Table.update_token(p.CONST_INT, str(final_value))
        
        return ('num_int', final_value)

    @_('CONST_FLOAT')
    def expr(self, p):
        return ('num_float', p.CONST_FLOAT)
    
    # Regla para la negación de CONST_FLOAT (detecta unario)
    @_('MINUS CONST_FLOAT')
    def expr(self, p):        
        # Obtenemos el valor de la magnitud
        try:
            magnitude = float(p.CONST_FLOAT)
        except ValueError:
            # Manejo de error si el valor del token es inválido
            return ('num_float', 0.0) 

        signed_value = -magnitude
        
        # Rango FLOAT (single precision)
        MIN_FLOAT = -3.40282347e38
        
        if signed_value < MIN_FLOAT:
            msg = f"Warning: Constante flotante negativa {signed_value} fuera de rango (underflow). Se usará el límite ({MIN_FLOAT})."
            self.print_color(msg)
            final_value = MIN_FLOAT
        else:
            final_value = signed_value
            
        # Modificación de la Tabla de Símbolos
        
        return ('num_float', final_value)