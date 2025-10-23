from sly import Parser
from tablaSimbolos import SymbolTable
from lexer import MyLexer
from tercetos import GeneradorTercetos


class MyParser(Parser):
    
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table 
    
    tokens = MyLexer.tokens

    def __init__(self, symbol_table,error_manager):
        self.symbol_table = symbol_table
        self.error_manager = error_manager
        self.tercetos = GeneradorTercetos()
    
    precedence = (
        ('nonassoc', ELSE),                            # arregla el conflicto del if-else, elige el if 2#                       
        ('left', '+', '-'),                            # suma y resta son asociativas a izquierda
        ('left', '*', '/'),                            # multiplicación/división, más fuertes
        ('right', UMINUS),                             # resuelve el problema de signo negativo
        ('nonassoc', EQ, NE, '>', LE, '<', GE)         # comparaciones no se pueden encadenar
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
    
    #error en la expresion del return
    @_('RETURN "(" error ")" ";"')
    def statement(self, p):
        self.errok()
        msg = "Error dentro de la expresion del return"
        self.error_manager.add(p.lineno, msg, source="parser")
        return(p.lineno,None)

    #falta ; al final del return
    @_('RETURN "(" expr ")" error')
    def statement(self, p):
        self.errok()
        msg = "Error: falta ; al final del return"
        self.error_manager.add(p.lineno, msg, source="parser")
        return(p.lineno,None)

    #Asignacion
    @_('ID "=" expr ";"')
    def statement(self, p):
        self.tercetos.nuevo('=', p.ID, p.expr)
        return (f"Linea {p.lineno} --> assign", p.ID, p.expr)
    
    #error en la expresion de la asignacion
    @_('ID "=" error ";"')
    def statement(self, p):
        self.errok()
        msg = "Error en la asignacion"
        self.error_manager.add(p.lineno, msg, source="parser")
        return(p.lineno,None)
    
    #falta ; en la asignacion
    @_('ID "=" expr error')
    def statement(self, p):
        self.errok()
        msg = "Error: falta ; al final de la asignacion"
        self.error_manager.add(p.lineno, msg, source="parser")
        return(p.lineno,None)

    # Declaraciones
    @_('type id_list ";"')
    def statement(self, p):
        return (f"Linea {p.lineno} --> declaration", p.type, p.id_list)
    
    #error en la expresion de la asignacion
    @_('type id_list_error ";"')
    def statement(self, p):
        self.errok()
        msg = "Error: faltó identificador después de ','"
        self.error_manager.add(p.lineno, msg, source="parser")
        return(p.lineno,None)
    
    #falta ; al final de la declaracion
    @_('type id_list error')
    def statement(self, p):
        self.errok()
        msg = "Error: falta ; al final de la declaracion"
        self.error_manager.add(p.lineno, msg, source="parser")
        return(p.lineno,None)
    
    #Prints
    @_('PRINT "(" expr ")" ";"')
    def statement(self, p):
        return (f"Linea: {p.lineno} --> print_expr", p.expr)

    @_('PRINT "(" STRING ")" ";"')
    def statement(self, p):
        return (f"Linea: {p.lineno} --> print_string", p.STRING)
    
    #falta ; al final del print
    @_('PRINT "(" expr ")" error')
    def statement(self, p):
        self.errok()
        msg = "Error: falta ; al final del print"
        self.error_manager.add(p.lineno, msg, source="parser")
        return(p.lineno,None)

    @_('PRINT "(" STRING ")" error')
    def statement(self, p):
        self.errok()
        msg = "Error: falta ; al final del print"
        self.error_manager.add(p.lineno, msg, source="parser")
        return(p.lineno,None)
    
    #error en la expresion del print
    @_('PRINT "(" error ")" ";"')
    def statement(self, p):
        self.errok()
        msg = "Error dentro del print"
        self.error_manager.add(p.lineno, msg, source="parser")
        return(p.lineno,None)
    
    #error comillas mal cerradas
    @_('PRINT "(" error ')
    def statement(self, p):
        self.errok()
        msg = "Warning: cadena sin cierre antes de salto de línea"
        self.error_manager.add(p.lineno, msg, source="parser")
        return(p.lineno,None)

    # 1. IF-ELSE statement (Handles single statement or block in both branches)
    @_('IF "(" expr ")" block ELSE block ENDIF ";"')
    def statement(self, p): 
        if_body = p.block0
        else_body = (p.ELSE, p.block1) 
        
        return (f"Linea: {p.lineno} --> if_else_stmt:",p.IF,
                p.expr, if_body, else_body, p.ENDIF)
    
    #Error en la comparacion del if
    @_('IF "(" error ")" block ELSE block ENDIF ";"')
    def statement(self, p):
        self.errok()
        msg = "Error en la condicion de endif"
        self.error_manager.add(p.lineno, msg, source="parser")
        return(p.lineno,None)
    
    @_('IF "(" expr ")" block ELSE block ENDIF error')
    def statement(self, p):
        self.errok()
        msg = "Error: falta ; al final del endif"
        self.error_manager.add(p.lineno, msg, source="parser")
        return(p.lineno,None)

    # 2. IF-only statement (Handles single statement or block)
    @_('IF "(" expr ")" block ENDIF ";" %prec ELSE')
    def statement(self, p): 
        return (f"Linea: {p.lineno} --> if_stmt:",p.IF, p.expr, p.block, p.ENDIF)
    
    #Error en la comparacion del if
    @_('IF "(" error ")" block ENDIF ";" %prec ELSE')
    def statement(self, p):
        self.errok()
        msg = "Error en la condicion del if"
        self.error_manager.add(p.lineno, msg, source="parser")
        return(p.lineno,None)
    
    @_('IF "(" expr ")" block ENDIF error %prec ELSE')
    def statement(self, p):
        self.errok()
        msg = "Error: falta ; al final del if"
        self.error_manager.add(p.lineno, msg, source="parser")
        return(p.lineno,None)

    #Function statement
    @_('type ID "(" param_list ")" block ";"')
    def statement(self, p):
        return (f"Linea: {p.lineno} --> func_stmt:", p.type, p.ID,p.param_list,p.block)
    
    #error en la expresion de la asignacion
    @_('type ID "(" param_list_error ")" block ";"')
    def statement(self, p):
        self.errok()
        msg = "Error: faltó identificador después de ','"
        self.error_manager.add(p.lineno, msg, source="parser")
        return(p.lineno,None)
    
    #falta ; al final de la funcion
    @_('type ID "(" param_list ")" block error')
    def statement(self, p):
        self.errok()
        msg = "Error: falta ; al final de la funcion"
        self.error_manager.add(p.lineno, msg, source="parser")
        return(p.lineno,None)

    #While statement
    @_('WHILE "(" expr ")" DO block ";"')
    def statement(self, p):
        return (f"Linea: {p.lineno} --> while_stmt:", p.expr, p.DO, p.block)
    
    #error en la comparacion del while
    @_('WHILE "(" error ")" DO block ";"')
    def statement(self, p):
        self.errok()
        msg = "Error en la condicion del while"
        self.error_manager.add(p.lineno, msg, source="parser")
        return(p.lineno,None)

    #falta ; al final del while
    @_('WHILE "(" expr ")" DO block error')
    def statement(self, p):
        self.errok()
        msg = "Error: falta ; al final del while"
        self.error_manager.add(p.lineno, msg, source="parser")
        return(p.lineno,None)
    
    #====================================== FUNCTION ===================================================

    # Lista de parametros
    @_('param_list "," param')
    def param_list(self, p):
        return p.param_list + [p.param]

    @_('param')
    def param_list(self, p):
        return [p.param]
    
    # Manejo de error: coma seguida de algo inválido, para parametros
    @_('param_list "," error')
    def param_list_error(self, p):
        return None
    
    # Item individual: con o sin modificador
    @_('CV type ID')
    def param(self, p):
        return ('param', p.CV, p.type, p.ID)

    @_('type ID')
    def param(self, p):
        return ('param', p.type, p.ID)
    
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
    
    # Manejo de error: coma seguida de algo inválido
    @_('id_list "," error')
    def id_list_error(self, p):
        return None
    
    
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
        return ('arrow', p.expr,p.ID)
    
    # ===================================== EXPRESIONES =================================================

    @_('expr "+" expr')
    def expr(self, p):
        self.tercetos.nuevo('+', p.expr0, p.expr1)
        return ('suma', p.expr0, p.expr1)

    @_('expr "-" expr')
    def expr(self, p):
        self.tercetos.nuevo('-', p.expr0, p.expr1)
        return ('resta', p.expr0, p.expr1)

    @_('expr "*" expr')
    def expr(self, p):
        self.tercetos.nuevo('*', p.expr0, p.expr1)
        return ('multiplicacion', p.expr0, p.expr1)

    @_('expr "/" expr')
    def expr(self, p):
        self.tercetos.nuevo('/', p.expr0, p.expr1)
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

    #================================= Tipos =================================================================================================
    @_('INT')
    @_('FLOAT')
    def type(self, p):
        return p[0]

    #======================== Primitivas de expresiones (variables y constantes) ========================================================
    @_('ID')
    def expr(self, p):
        return ('var', p.ID)

    # Manejo de enteros negativos con verificación de rango
    @_('"-" CONST_INT %prec UMINUS')
    def expr(self, p):
        # Rango INT (16 bits): [-32768, 32767]
        MIN_INT = -32768
        signed_value = -int(p.CONST_INT)
             
        if signed_value < MIN_INT:
            msg = f"Error: Constante entera negativa {signed_value} fuera de rango. Se usará el límite ({MIN_INT})."
            self.error_manager.add(p.lineno, msg, source="parser")
            final_value = MIN_INT
            self.symbol_table.delete_token(p.CONST_INT) 
            self.symbol_table.add_token(str(final_value), "CONST_INT") 
        else:
            final_value = signed_value
            self.symbol_table.delete_token(p.CONST_INT) 
            self.symbol_table.add_token(str(final_value), "CONST_INT")
       
        return ('num_int', final_value) 
    
    @_('CONST_INT')
    def expr(self, p):
        MAX_INT = 32767 
        value = int(p.CONST_INT)
        if value > MAX_INT: 
            msg = f"Error: Constante entera positiva {value} fuera de rango. Se usará el límite ({MAX_INT})."
            self.error_manager.add(p.lineno, msg, source="parser")
            value = MAX_INT
            self.symbol_table.delete_token(p.CONST_INT)
            self.symbol_table.add_token(str(value), "CONST_INT")
            
            return ('num_int', str(value))
        else:
            self.symbol_table.delete_token(p.CONST_INT)
            self.symbol_table.add_token(str(value), "CONST_INT")       
            return ('num_int', str(value))

    # Regla para la negación de CONST_FLOAT (detecta unario)
    @_('"-" CONST_FLOAT %prec UMINUS')
    def expr(self, p):
        signed_value = -float(p.CONST_FLOAT)
        # Rango FLOAT (single precision)
        MIN_FLOAT_NEGATIVO = -3.40282347e38 # Número negativo más lejano al 0
        MAX_FLOAT_NEGATIVO = -1.17549435e-38 # Número negativo más cercano al 0
        
        if signed_value < MIN_FLOAT_NEGATIVO:
            msg = f"Error: Constante flotante negativa {signed_value} fuera de rango. Se usará el límite ({MIN_FLOAT_NEGATIVO})."
            self.error_manager.add(p.lineno, msg, source="parser")
            final_value = MIN_FLOAT_NEGATIVO
            self.symbol_table.delete_token(p.CONST_FLOAT)
            self.symbol_table.add_token(str(final_value), "CONST_FLOAT")

        elif signed_value > MAX_FLOAT_NEGATIVO and signed_value != 0.0:
            msg = f"Error: Constante flotante negativa {signed_value} fuera de rango. Se usará el límite ({MAX_FLOAT_NEGATIVO})."
            self.error_manager.add(p.lineno, msg, source="parser")
            final_value = MAX_FLOAT_NEGATIVO
            
            self.symbol_table.delete_token(p.CONST_FLOAT)
            self.symbol_table.add_token(str(final_value), "CONST_FLOAT")
            
        else:
            final_value = signed_value
        
        self.symbol_table.delete_token(p.CONST_FLOAT)
        self.symbol_table.add_token(str(final_value), "CONST_FLOAT")
        
        return ('num_float', final_value)
    
    @_('CONST_FLOAT')
    def expr(self, p):
        self.symbol_table.delete_token(p.CONST_FLOAT)
        self.symbol_table.add_token(p.CONST_FLOAT, "CONST_FLOAT")
        return ('num_float', p.CONST_FLOAT)
    
     # ========================================== Manejo general de errores ================================================
    # Evita que el SLY escriba errores fuera del arbol  
    def error(self, p):
        if p:
        # Just discard the token and tell the parser it's okay.
            self.errok()
            return None
        else:
            return None
