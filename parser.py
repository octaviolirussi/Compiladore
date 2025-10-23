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
        ('nonassoc', ELSE),                     # para resolver if-else
        ('nonassoc', EQ, NE, '>', LE, '<', GE), # comparaciones (menor precedencia)
        ('left', '+', '-'),                     # suma y resta
        ('left', '*', '/'),                     # multiplicación y división
        ('right', UMINUS),                      # unario negativo
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
        # p.expr es la referencia [N] del terceto que calcula la condición (ej. [0]: (>, A, B)).
        
        # Generar BF que sale del IF-bloque al ELSE-bloque.
        # El destino es temporal (PENDIENTE).
        salto_a_else_ref = self.tercetos.nuevo('BF', p.expr, self.tercetos.PENDIENTE)
    
        # Genero BI que sale del IF-bloque al ENDIF.
        # Este salto garantiza que no ejecutaremos el bloque ELSE si el IF fue verdadero.
        salto_a_endif_ref = self.tercetos.nuevo('BI', self.tercetos.PENDIENTE, None)
        
        # Rellenar el BF (el primer salto) para que salte al inicio del ELSE.
        etiqueta_else = len(self.tercetos.tercetos) # El índice del terceto que sigue es el inicio del ELSE.
        print(etiqueta_else) #TODO no salta al else, salta al final de todo el bloque if-else CORREGIR
        self.tercetos.backpatch([salto_a_else_ref], etiqueta_else) 
        
        # 6. La instrucción actual (final del ELSE) es la etiqueta ENDIF.
        etiqueta_endif = len(self.tercetos.tercetos)   
        
        # 7. Rellenar el BI (salto_a_endif_ref) para ir a la etiqueta ENDIF.
        self.tercetos.backpatch([salto_a_endif_ref], etiqueta_endif)
        
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


    # 2. IF-only statement
    @_('IF "(" expr ")" block ENDIF ";" %prec ELSE')
    def statement(self, p):    
        # Generar BF para saltar al ENDIF (sale del bloque si es FALSO).
        # El destino es temporal (PENDIENTE).
        salto_a_endif_ref = self.tercetos.nuevo('BF', p.expr, self.tercetos.PENDIENTE)
                
        # Rellenar el BF para que salte a la siguiente instrucción (ENDIF).
        etiqueta_endif = len(self.tercetos.tercetos) # El índice actual es la primera instrucción después del 'if'.
        print(etiqueta_endif) #TODO hace mal los saltos
        self.tercetos.backpatch([salto_a_endif_ref], etiqueta_endif)
            
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
        etiqueta_condicion = len(self.tercetos.tercetos)
        
        # crea la instrucción de salto a la salida. self.tercetos.PENDIENTE indica
        # que el destino es aún desconocido
        salto_a_salida_ref = self.tercetos.nuevo('BF', p.expr, self.tercetos.PENDIENTE)
        
        # vuelve a la condición del while
        self.tercetos.nuevo('BI', f"[{etiqueta_condicion}]", None)
        
        # índice del primer terceto después del bucle.
        etiqueta_salida = len(self.tercetos.tercetos)
        
        # Toma la instrucción de salto BF pendiente y rellena su campo PENDIENTE 
        # con la dirección correcta (etiqueta_salida, del paso 5).
        self.tercetos.backpatch([salto_a_salida_ref], etiqueta_salida)
        
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
    
    @_('expr GE expr')  # >=
    def expr(self, p):  
        temp = self.tercetos.nuevo('>=', p.expr0, p.expr1)    
        return temp
    
    @_('expr LE expr') # <=
    def expr(self, p):
        temp = self.tercetos.nuevo('<=', p.expr0, p.expr1)
        return temp
    
    @_('expr EQ expr')  # ==
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
