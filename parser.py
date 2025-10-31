from sly import Parser
from tablaSimbolos import SymbolTable
from lexer import MyLexer
from tercetos import GeneradorTercetos

class MyParser(Parser):
    
    tokens = MyLexer.tokens

    def __init__(self, symbol_table,error_manager):
        self.symbol_table = symbol_table
        self.error_manager = error_manager
        self.tercetos = GeneradorTercetos()
    
    precedence = (
        ('nonassoc', ELSE),
        ('nonassoc', EQ, NE, '>', LE, '<', GE),
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('right', UMINUS),
    )

# ===================================== PROGRAMA =====================================================

    @_('PROGRAMA "{" statement_list "}"')
    def program(self, p):
        # Se genera un terceto de inicio de programa
        self.tercetos.nuevo('START_PROGRAM', None)
        
        # Se genera el terceto de fin de programa
        self.tercetos.nuevo('END_PROGRAM', None, None) 

        return ('program', p.statement_list) 
    
    @_('error "{" statement_list "}"')
    def program(self, p):
        self.errok() 
        lineno = p.error.lineno if p.error else 1 
        msg = "Error: El programa debe comenzar con la palabra clave PROGRAMA, seguida del cuerpo entre llaves."
        self.error_manager.add(lineno, msg, source="parser")

        return ('program_error', p.statement_list)
    
    # @_('statement_list')
    # def program(self, p):
    #     return ('stament_list', p.statement_list)
    
    #====================================== BLOCKS ====================================================

    @_('"{" statement_list "}"')
    def block(self, p):
        return p.statement_list
    
    # @_('error statement_list "}"')
    # def block(self, p):
    #     msg = "Error: falta { al inicio del bloque"
    #     self.error_manager.add(p.lineno, msg, source="parser")
        
    # @_('"{" statement_list error')
    # def block(self, p):
    #     msg = "Error: falta { al final del bloque"
    #     self.error_manager.add(p.lineno, msg, source="parser")

    @_('statement')
    def block(self, p):
        return [p.statement]
    
    #============================================ STATEMENT ===============================================
 
    @_('statement_list statement')
    def statement_list(self, p):
        return p.statement_list + [p.statement]

    @_('statement')
    def statement_list(self, p):
        return [p.statement]

    #return
    @_('RETURN "(" expr ")" ";"')
    def statement(self, p):
        temp = self.tercetos.nuevo('RETURN', p.expr, None) 
        
    #error en la expresion del return
    @_('RETURN "(" error ")" ";"')
    def statement(self, p):
        self.errok()
        msg = "Error dentro de la expresion del return"
        self.error_manager.add(p.lineno, msg, source="parser")

    #falta ; al final del return
    @_('RETURN "(" expr ")" error')
    def statement(self, p):
        self.errok()
        msg = "Error: falta ; al final del return"
        self.error_manager.add(p.lineno, msg, source="parser")

    #Asignacion
    @_('ID "=" expr ";"')
    def statement(self, p):
        temp = self.tercetos.nuevo('=', p.ID, p.expr)
    
    #error en la expresion de la asignacion
    @_('ID "=" error ";"')
    def statement(self, p):
        self.errok()
        msg = "Error en la asignacion"
        self.error_manager.add(p.lineno, msg, source="parser")
    
    #falta ; en la asignacion
    @_('ID "=" expr error')
    def statement(self, p):
        self.errok()
        msg = "Error: falta ; al final de la asignacion"
        self.error_manager.add(p.lineno, msg, source="parser")

    # Declaraciones
    @_('type id_list ";"')
    def statement(self, p):
        for var in p.id_list:
            ref = self.tercetos.nuevo('DECL', p.type, var)
    
    #error en la expresion de la asignacion
    @_('type id_list_error ";"')
    def statement(self, p):
        self.errok()
        msg = "Error: faltó identificador después de ','"
        self.error_manager.add(p.lineno, msg, source="parser")
    
    #falta ; al final de la declaracion
    @_('type id_list error')
    def statement(self, p):
        self.errok()
        msg = "Error: falta ; al final de la declaracion"
        self.error_manager.add(p.lineno, msg, source="parser")
    
    #Prints
    @_('PRINT "(" expr ")" ";"')
    def statement(self, p):
        self.tercetos.nuevo('PRINT', p.expr, None)

    @_('PRINT "(" STRING ")" ";"')
    def statement(self, p):
        self.tercetos.nuevo('PRINT', p.STRING, None)
    
    #falta ; al final del print
    @_('PRINT "(" expr ")" error')
    def statement(self, p):
        self.errok()
        msg = "Error: falta ; al final del print"
        self.error_manager.add(p.lineno, msg, source="parser")

    @_('PRINT "(" STRING ")" error')
    def statement(self, p):
        self.errok()
        msg = "Error: falta ; al final del print"
        self.error_manager.add(p.lineno, msg, source="parser")
    
    #error en la expresion del print
    @_('PRINT "(" error ")" ";"')
    def statement(self, p):
        self.errok()
        msg = "Error dentro del print"
        self.error_manager.add(p.lineno, msg, source="parser")
    
    #error comillas mal cerradas
    @_('PRINT "(" error ')
    def statement(self, p):
        self.errok()
        msg = "Warning: cadena sin cierre antes de salto de línea"
        self.error_manager.add(p.lineno, msg, source="parser")
        
    # 1. IF-ELSE statement
    @_('IF "(" expr ")" block ELSE block ENDIF ";"')
    def statement(self, p): 

        # Crear tercetos de control y obtener sus índices
        index_BF = int(self.tercetos.nuevo('BF', p.expr, self.tercetos.PENDIENTE).strip('[]'))
        index_BI = int(self.tercetos.nuevo('BI', self.tercetos.PENDIENTE, None).strip('[]'))
        index_end = int(self.tercetos.nuevo('FUERA_DEL_IF', None, None).strip('[]'))

        # Índices auxiliares
        expr_indice = int(p.expr.strip('[]'))                         # último terceto de la condición
        index_else_last = (expr_indice + 1) + (len(p.block0) + 1)     # para mover BI a su posicion
        index_else_first = expr_indice + len(p.block0) + 1            # para hacer backpatch de BF

        # Backpatch del BF → apunta al inicio del bloque ELSE
        self.tercetos.backpatch([f"[{index_BF}]"], index_else_first)

        # Backpatch del BI → apunta al FUERA_DEL_IF
        self.tercetos.backpatch([f"[{index_BI}]"], index_end)

        # Mover el BF justo después de la condición
        self.tercetos.mover_terceto(index_BF, expr_indice + 1)

        # Mover el BI justo antes del bloque ELSE
        self.tercetos.mover_terceto(index_BI, index_else_last)

    #Error en la comparacion del if
    @_('IF "(" error ")" block ELSE block ENDIF ";"')
    def statement(self, p):
        self.errok()
        msg = "Error en la condicion de endif"
        self.error_manager.add(p.lineno, msg, source="parser")
    
    @_('IF "(" expr ")" block ELSE block ENDIF error')
    def statement(self, p):
        self.errok()
        msg = "Error: falta ; al final del endif"
        self.error_manager.add(p.lineno, msg, source="parser")

    @_('IF "(" expr ")" block ELSE block error ";"')
    def statement(self, p):
        self.errok()
        msg = "Error: falta endif al final del if"
        self.error_manager.add(p.lineno, msg, source="parser")
        
    # @_('IF "(" expr ")" statement ELSE block ENDIF ";"')
    # def statement(self, p):
    #     self.errok()
    #     msg = "Error: el bloque 'if' debe estar entre llaves {}"
    #     self.error_manager.add(p.lineno, msg, source="parser")

    # 2. IF-only statement
    @_('IF "(" expr ")" block ENDIF ";" %prec ELSE')
    def statement(self, p):
        # Generar BF para saltar al ENDIF (sale del bloque si es FALSO).
        # El destino es temporal (PENDIENTE).
        salto_a_endif_ref = self.tercetos.nuevo('BF', p.expr, self.tercetos.PENDIENTE)

         # 2. Obtener índice del terceto de la condición
        expr_indice = int(p.expr.strip('[]')) 
                
        # Rellenar el BF para que salte a la siguiente instrucción (ENDIF).
        # El índice actual es la primera instrucción después del 'if'.
        etiqueta_endif = len(self.tercetos.tercetos) 
        self.tercetos.backpatch([salto_a_endif_ref], etiqueta_endif)
    
        self.tercetos.mover_terceto(int(salto_a_endif_ref.strip('[]')),expr_indice+1)

        self.tercetos.nuevo("FIN_IF", None, None)
            
    #Error en la comparacion del if
    @_('IF "(" error ")" block ENDIF ";" %prec ELSE')
    def statement(self, p):
        self.errok()
        msg = "Error en la condicion del if"
        self.error_manager.add(p.lineno, msg, source="parser")
    
    @_('IF "(" expr ")" block ENDIF error %prec ELSE')
    def statement(self, p):
        self.errok()
        msg = "Error: falta ; al final del if"
        self.error_manager.add(p.lineno, msg, source="parser")

    @_('IF "(" expr ")" block error ";" %prec ELSE')
    def statement(self, p):
        self.errok()
        msg = "Error: falta endif al final del if"
        self.error_manager.add(p.lineno, msg, source="parser")

    #Function statement
    @_('type ID "(" param_list ")" block ";"')
    def statement(self, p):
        self.symbol_table.add_function(p.ID, p.type, p.param_list)
        
        self.tercetos.nuevo('FUNC', p.ID, p.type)
        if p.type == 'int':
            msg = "Warning: función sin return, se usará valor por defecto 0"
            self.error_manager.add(p.lineno, msg, source="parser")
            default_value = '0'
            self.symbol_table.add_token('0', 'CONST_INT') # Asegura que '0' está en la TS
        elif p.type == 'float':
            msg = "Warning: función sin return, se usará valor por defecto 0.0"
            self.error_manager.add(p.lineno, msg, source="parser")
            default_value = '0.0'
            self.symbol_table.add_token('0.0', 'CONST_FLOAT') # Asegura que '0.0' está en la TS
        else:
            # Asumimos 'int' como valor por defecto si hay un tipo inesperado
            msg = "Warning: función sin return, se usará valor por defecto 0"
            self.error_manager.add(p.lineno, msg, source="parser")
            default_value = '0' 
            self.symbol_table.add_token('0', 'CONST_INT')
        
        self.tercetos.nuevo('END_FUNC', p.ID, None)
        
        return ('function', p.type, p.ID, p.param_list, p.block)
    
    #error en la expresion de la asignacion
    @_('type ID "(" param_list_error ")" block ";"')
    def statement(self, p):
        self.errok()
        msg = "Error: faltó identificador después de ','"
        self.error_manager.add(p.lineno, msg, source="parser")
    
    #falta ; al final de la funcion
    @_('type ID "(" param_list ")" block error')
    def statement(self, p):
        self.errok()
        msg = "Error: falta ; al final de la funcion"
        self.error_manager.add(p.lineno, msg, source="parser")

    #While statement
    @_('WHILE "(" expr ")" DO block ";"')
    def statement(self, p):
        # acá salta el programa para volver a evaluar la condición
        #Capturar el índice inicial de la condición, osea el terceto de la condicion final
        expr_indice = int(p.expr.strip('[]')) 
        
        t_cond = self.tercetos.tercetos[expr_indice]
    
        #Esto toma la el primer operando de la condicion while
        if isinstance(t_cond.op1, str) and t_cond.op1.startswith('['):
            etiqueta_condicion = int(t_cond.op1.strip('[]')) # apunta al primer terceto de la condicion
        else:
            etiqueta_condicion = expr_indice # fallback

        # Generar BF pendiente
        salto_a_salida_ref = self.tercetos.nuevo('BF', p.expr, self.tercetos.PENDIENTE)
        
        # vuelve a la condición del while
        self.tercetos.nuevo('BI', f"[{etiqueta_condicion}]", None)
        
        # índice del primer terceto después del bucle.
        etiqueta_salida = len(self.tercetos.tercetos)
        
        # Toma la instrucción de salto BF pendiente y rellena su campo PENDIENTE 
        self.tercetos.backpatch([salto_a_salida_ref], etiqueta_salida)
        
        self.tercetos.mover_terceto(int(salto_a_salida_ref.strip('[]')),expr_indice+1)

        self.tercetos.nuevo("FIN_WHILE", None, None)
        
    #error en la comparacion del while
    @_('WHILE "(" error ")" DO block ";"')
    def statement(self, p):
        self.errok()
        msg = "Error en la condicion del while"
        self.error_manager.add(p.lineno, msg, source="parser")

    #falta ; al final del while
    @_('WHILE "(" expr ")" DO block error')
    def statement(self, p):
        self.errok()
        msg = "Error: falta ; al final del while"
        self.error_manager.add(p.lineno, msg, source="parser")
    
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
        for arg in p.arg_list:
            if arg[0] == 'arrow':
                self.tercetos.nuevo('->', arg[1], arg[2])
    
        temp = self.tercetos.nuevo('CALL', p.ID, len(p.arg_list))
        return temp

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
        temp = self.tercetos.nuevo('+', p.expr0, p.expr1)
        return temp

    @_('expr "-" expr')
    def expr(self, p):
        temp = self.tercetos.nuevo('-', p.expr0, p.expr1)
        return temp

    @_('expr "*" expr')
    def expr(self, p):
        temp = self.tercetos.nuevo('*', p.expr0, p.expr1)
        return temp

    @_('expr "/" expr')
    def expr(self, p):
        temp = self.tercetos.nuevo('/', p.expr0, p.expr1)
        return temp
    
    @_('expr ">" expr')
    def expr(self, p):
        temp = self.tercetos.nuevo('>', p.expr0, p.expr1)
        return temp
    
    @_('expr "<" expr')
    def expr(self, p):
        temp = self.tercetos.nuevo('<', p.expr0, p.expr1)
        return temp
    
    @_('expr GE expr') # >=
    def expr(self, p): 
        temp = self.tercetos.nuevo('>=', p.expr0, p.expr1)
        return temp
    
    @_('expr LE expr') # <=
    def expr(self, p):
        temp = self.tercetos.nuevo('<=', p.expr0, p.expr1)
        return temp
    
    @_('expr EQ expr')# ==
    def expr(self, p):
        temp = self.tercetos.nuevo('==', p.expr0, p.expr1)
        return temp
    
    @_('expr NE expr') # !=
    def expr(self, p):
        temp = self.tercetos.nuevo('!=', p.expr0, p.expr1)
        return temp 

    #================================= Tipos =================================================================================================
    @_('INT')
    @_('FLOAT')
    def type(self, p):
        return p[0]

    #======================== Primitivas de expresiones (variables y constantes) ========================================================
    @_('ID')
    def expr(self, p):
        return (p.ID)

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
        
        return (final_value)
    
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
            
            return (str(value))
        else:
            self.symbol_table.delete_token(p.CONST_INT)
            self.symbol_table.add_token(str(value), "CONST_INT")
            return (str(value))

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
        
        return (final_value)
    
    @_('CONST_FLOAT')
    def expr(self, p):
        self.symbol_table.delete_token(p.CONST_FLOAT)
        self.symbol_table.add_token(p.CONST_FLOAT, "CONST_FLOAT")
        return (p.CONST_FLOAT)
    
    # ========================================== Manejo general de errores ================================================
    # Evita que el SLY escriba errores fuera del arbol  
    def error(self, p):
        if p:
        # Just discard the token and tell the parser it's okay.
            self.errok()
            return None
        else:
            return None