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

    # === SENTENCIAS ===
    # @_('CONST_INT ";"')
    # def statement(self, p):
    #     return ('num_stmt', p.CONST_INT)

    @_('expr ";"')
    def statement(self, p):
        return ('expr_stmt', p.expr)

    @_('ID "=" expr ";"')
    def statement(self, p):
        return ('assign', p.ID, p.expr)

    # === EXPRESIONES ===
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

    @_('CONST_INT')
    def expr(self, p):
        return ('num', p.CONST_INT)

    @_('ID')
    def expr(self, p):
        return ('var', p.ID)
