from sly import Parser
from lexer import MyLexer

class MyParser(Parser):
    tokens = MyLexer.tokens
    
    precedence = (
        ('left', 'EQ', 'NE', 'GE', 'LE', '>', '<'),
        ('left', '+', '-'),
        ('left', '*', '/'),
    )   

    #Regla de programa
    @_('statement_list')
    def program(self, p):
        return ('program', p.statement_list)

    # Otras reglas que program usa
    @_('statement_list statement')
    def statement_list(self, p):
        return p.statement_list + [p.statement]

    @_('statement')
    def statement_list(self, p):
        return [p.statement]
    
    # === SENTENCIAS =============================================================================================================================
   
    @_('expr ";"')
    def statement(self, p):
        return (f"Linea {p.lineno} --> expr_stmt:", p.expr)

    # asignación
    @_('ID "=" expr ";"')
    def statement(self, p):
        return (f"Linea: {p.lineno} --> assign", p.ID, p.expr)
    
    @_('INT id_list ";"')
    def statement(self, p):
        return (f"Linea: {p.lineno} --> declaration:", p.INT, p.id_list)
    
    @_('FLOAT id_list ";"')
    def statement(self, p):
        return (f"Linea: {p.lineno} --> declaration:", p.FLOAT, p.id_list)
    
    #Prints
    @_('PRINT "(" expr ")" ";"')
    def statement(self, p):
        return (f"Linea: {p.lineno} --> print_expr", p.expr)
    
    @_('PRINT "(" STRING ")" ";"')
    def statement(self, p):
        return (f"Linea: {p.lineno} --> print_string", p.STRING)
        
# === SENTENCIAS DE SELECCIÓN (if) ========================================================================================================================
    # Regla auxiliar para manejar tanto statement como statement_block
    @_('statement')
    @_('statement_block')
    def if_branch(self, p):
        return p[0]

    # 1. IF-ELSE statement (Handles single statement or block in both branches)
    @_('IF "(" expr ")" if_branch ELSE if_branch ENDIF ";"')
    def statement(self, p): 
        if_body = p.if_branch0
        else_body = ('else', p.if_branch1) 
        
        return (f"Linea: {p.lineno} --> if_else_stmt:",
                p.expr, if_body, else_body)

    # 2. IF-only statement (Handles single statement or block)
    @_('IF "(" expr ")" if_branch ENDIF ";"')
    def statement(self, p): 
        return (f"Linea: {p.lineno} --> if_stmt:", p.expr, p.if_branch)
   
    @_('"{" statement_list "}"')
    def statement_block(self, p):
        return p.statement_list
        
    # ===================================== LISTAS ====================================================

    # Lista de IDs
    @_('id_list "," ID')
    def id_list(self, p):
        return p.id_list + [p.ID]

    @_('ID')
    def id_list(self, p):
        return [p.ID]

    # Lista de argumentos
    @_('arg_list "," arg')
    def arg_list(self, p):
        return p.arg_list + [p.arg]

    @_('arg')
    def arg_list(self, p):
        return [p.arg]

    # ===================================== ARGUMENTOS =================================================

    @_('expr ARROW ID')
    def arg(self, p):
        return ('arg', p.expr, p.ID)

# === EXPRESIONES ARITMÉTICAS Y DE COMPARACIÓN===============================================================
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
    
    @_('ID "(" arg_list ")"')
    def expr(self, p):
        return ('func_call', p.ID, p.arg_list)

# Primitivas de expresiones (variables y constantes) ========================================================
    
    @_('ID')
    def expr(self, p):
        return ('var', p.ID)

    @_('CONST_INT')
    def expr(self, p):
        return ('num_int', p.CONST_INT)
    
    @_('CONST_FLOAT')
    def expr(self, p):
        return ('num_float', p.CONST_FLOAT)
    
    @_('INT') #son necesarias?
    def expr(self, p):
        return ('int',p.INT)
    
    @_('FLOAT') #son necesarias?
    def expr(self, p):
        return ('float',p.FLOAT)