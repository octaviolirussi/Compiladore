from sly import Parser
from tablaSimbolos import SymbolTable
from lexer import MyLexer
from colorama import Fore, Style


class MyParser(Parser):
    
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table 
    
    tokens = MyLexer.tokens
        
    precedence = (
            ('nonassoc', ELSE),                            # arregla el conflicto del if-else, elige el if 2#                       # comparaciones no se pueden encadenar
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
    @_('IF "(" expr ")" block ELSE block ENDIF ";"')
    def statement(self, p): 
        if_body = p.block0
        else_body = (p.ELSE, p.block1) 
        
        return (f"Linea: {p.lineno} --> if_else_stmt:",p.IF,
                p.expr, if_body, else_body, p.ENDIF)

    # 2. IF-only statement (Handles single statement or block)
    @_('IF "(" expr ")" block ENDIF ";" %prec ELSE')
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
    
    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return ('uminus', p.expr) 
    
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
        return ('uminus', p.expr) 
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
            msg = f"Warning: Constante entera negativa {signed_value} fuera de rango (linea. Se usará el límite ({MIN_INT})."
            print(msg)
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
            msg = f"Warning: Constante entera positiva {value} fuera de rango. Se usará el límite ({MAX_INT})."
            print(msg)
            value = MAX_INT
            self.symbol_table.delete_token(p.CONST_INT)
            self.symbol_table.add_token(str(value), "CONST_INT")
            
            return ('num_int', str(value))
        else:       
            return ('num_int', str(value))

    # Regla para la negación de CONST_FLOAT (detecta unario)
    @_('"-" CONST_FLOAT %prec UMINUS')
    def expr(self, p):
        signed_value = -float(p.CONST_FLOAT)
        # Rango FLOAT (single precision)
        MIN_FLOAT_NEGATIVO = -3.40282347e38 # Número negativo más lejano al 0
        MAX_FLOAT_NEGATIVO = -1.17549435e-38 # Número negativo más cercano al 0
        
        if signed_value < MIN_FLOAT_NEGATIVO:
            msg = f"Warning: Constante flotante negativa {signed_value} fuera de rango. Se usará el límite ({MIN_FLOAT_NEGATIVO})."
            print(msg)
            final_value = MIN_FLOAT_NEGATIVO
            self.symbol_table.delete_token(p.CONST_FLOAT)
            self.symbol_table.add_token(str(final_value), "CONST_FLOAT")

        elif signed_value > MAX_FLOAT_NEGATIVO and signed_value != 0.0:
            msg = f"Warning: Constante flotante negativa {signed_value} fuera de rango. Se usará el límite ({MAX_FLOAT_NEGATIVO})."
            print(msg)
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
        return ('num_float', p.CONST_FLOAT)
    