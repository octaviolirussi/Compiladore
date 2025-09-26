from sly import Parser
from lexer import MyLexer

class MyParser(Parser):
    tokens = MyLexer.tokens
    
    precedence = (
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

    @_('ID "=" expr ";"')
    def statement(self, p):
        return (f"Linea: {p.lineno} --> assign", p.ID, p.expr)
    
    @_('INT id_list ";"')
    def statement(self, p):
        return (f"Linea: {p.lineno} --> declaration:", p.INT, p.id_list)
    
    @_('FLOAT id_list ";"')
    def statement(self, p):
        return (f"Linea: {p.lineno} --> declaration:", p.FLOAT, p.id_list)
    
    # Regla recursiva para lista de IDs
    @_('id_list "," ID')
    def id_list(self, p):
        return p.id_list + [p.ID]
    

    # === EXPRESIONES ==========================================================================================================================
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
    
    @_('ID')
    def id_list(self, p):
        return [p.ID]
    
    @_('ID')
    def expr(self, p):
        return ('var', p.ID)

    @_('CONST_INT')
    def expr(self, p):
        return ('num_int', p.CONST_INT)
    
    @_('CONST_FLOAT')
    def expr(self, p):
        return ('num_float', p.CONST_FLOAT)
    
    @_('INT')
    def expr(self, p):
        return ('int',p.INT)
    
    @_('FLOAT')
    def expr(self, p):
        return ('float',p.FLOAT)