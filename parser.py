from sly import Parser
from tablaSimbolos import SymbolTable
from lexer import MyLexer
from tercetos import GeneradorTercetos

class MyParser(Parser):
    
    tokens = MyLexer.tokens

    def __init__(self, symbol_table, error_manager):
        self.symbol_table = symbol_table
        self.error_manager = error_manager
        self.tercetos = GeneradorTercetos(symbol_table,error_manager)
        self.tercetos_antes = 0

    
    precedence = (
        ('nonassoc', ELSE),
        ('nonassoc', EQ, NE, '>', LE, '<', GE),
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('right', UMINUS),
    )

    def get_type_of_value(self, value):
        """
        Determina el tipo de dato ('INT', 'FLOAT', etc.) de un operando:
        ID, CONSTANTE, o índice de terceto ([T#]).
        """
        # si es un índice de un terceto
        if isinstance(value, str) and value.startswith('[') and value.endswith(']'):
            terceto_index = int(value.strip('[]'))
            return self.tercetos.get_result_type(terceto_index) 

        # es un ID o una constante
        elif isinstance(value, (str, float, int)):
            value_str = str(value) 
            
            entry = self.symbol_table.get_token(value_str)
            if entry:
                return entry.get("data_type", None)
        return None
    
    def verifica_return(self, ID, type, start_index, end_index):
        """
        Verificar que si existe una instrucción RETURN dentro del cuerpo de la función, 
        el tipo de dato que retorna sea compatible con el tipo de retorno declarado para 
        la función.
        Insertar un RETURN por defecto si la función no contiene explícitamente ninguna 
        instrucción RETURN (tipos int y float)
        """ 
        tiene_return = False  
        expected_type = type    
        
        skip_level = 0 # Nivel de anidamiento actual, 0 significa la función que estamos verificando
        # Recorremos el rango de índices del cuerpo de la función
        for i in range(start_index, end_index):
            terceto = self.tercetos.tercetos[i] 
            
            if terceto.operador == 'FUNC':
                # Entra en una función anidada, incrementamos el nivel de anidamiento
                skip_level += 1
                continue
            
            elif terceto.operador == 'END_FUNC':
                if skip_level > 0:
                    skip_level -= 1
                    continue
                # Si skip_level es 0, es el END_FUNC de la función actual.
                
            # Si estamos dentro de una función anidada (skip_level > 0), saltamos la verificación.
            if skip_level > 0:
                continue
            
            if terceto.operador == 'RETURN':
                return_type = self.get_type_of_value(terceto.op1)
                
                if return_type and return_type != expected_type:
                    msg = f"Error semántico: Tipo de retorno incompatible en función '{ID}'. Se esperaba '{expected_type}', pero se obtuvo '{return_type}'."
                    self.error_manager.add(terceto.lineno, msg, source="parser")
                
                tiene_return = True
                return None 

        if not tiene_return: # Lógica de inserción del RETURN por defecto
            # Validación de tipo y valor por defecto
            if expected_type == 'int':
                default_value = '0'
                self.symbol_table.add_token('0', 'CONST_INT')
            elif expected_type == 'float':
                default_value = '0.0'
                self.symbol_table.add_token('0.0', 'CONST_FLOAT')
            else:
                return None 
            msg = f"Warning: La función '{ID}' no tiene una instrucción RETURN. Return por defecto {default_value}."
            self.error_manager.add(None, msg, source="parser")
            
            # 2. Generar RETURN(valor_defecto, None)
            # 3. Moverlo a justo antes de END_FUNC (índice 'end_index')
            idx_return = self.tercetos.nuevo('RETURN', default_value, None)
            
            return int(idx_return.strip('[]'))
# ===================================== PROGRAMA =====================================================

    @_('ID "{" statement_list "}"')
    def program(self, p):

        self.symbol_table.add_token(p.ID, "PROGRAMA")

        # Se genera un terceto de inicio de programa
        self.tercetos.nuevo('START_PROGRAM', None, lineno=p.lineno)
        
        # Se genera el terceto de fin de programa
        self.tercetos.nuevo('END_PROGRAM', None, None,lineno=p.lineno)

        # Mover el START_PROGRAM (anteúltimo) al inicio (índice 0)
        index_origen = len(self.tercetos.tercetos) - 2  # anteúltimo
        index_destino = 0
        self.tercetos.mover_terceto(index_origen, index_destino)
        return p.statement_list
    
    @_(' "{" statement_list "}"')
    def program(self, p):
        
        # Se genera un terceto de inicio de programa
        self.tercetos.nuevo('START_PROGRAM', None,lineno=p.lineno)
        
        # Se genera el terceto de fin de programa
        self.tercetos.nuevo('END_PROGRAM', None, None,lineno=p.lineno)

        # Mover el START_PROGRAM (anteúltimo) al inicio (índice 0)
        index_origen = len(self.tercetos.tercetos) - 2  # anteúltimo
        index_destino = 0
        self.tercetos.mover_terceto(index_origen, index_destino)

        self.errok()
        msg = "Warning: falta inicio del programa"
        self.error_manager.add(p.lineno, msg, source="parser")

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
        idx = self.tercetos.nuevo('RETURN', p.expr, None,lineno=p.lineno)
        self.tercetos_antes = len(self.tercetos.tercetos)
        return int(idx.strip('[]')) + 1 # índice numérico 
        
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
        id_destino = p.ID
        expr_origen = p.expr
        
        type_destino = self.get_type_of_value(id_destino) # Tipo de la variable (ID)
        type_origen = self.get_type_of_value(expr_origen) # Tipo del resultado (expr, que puede ser un CALL)
        
        type_destino_norm = type_destino.upper() if type_destino else None
        type_origen_norm = type_origen.upper() if type_origen else None
        
        if type_destino_norm is None or type_origen_norm is None:
            msg = f"Error semántico: Variable sin declarar '{id_destino}'"
            if type_destino_norm is None:
                id_entry = self.symbol_table.get_token(id_destino)
                if not id_entry or id_entry.get("Uso") == "N/A":
                    msg = f"Error semántico: Variable '{id_destino}' no declarada."
                    
            #self.error_manager.add(p.lineno, msg, source="parser")
            idx = self.tercetos.nuevo('=', id_destino, expr_origen,lineno=p.lineno)
            return int(idx.strip('[]')) + 1

        final_expr_origen = expr_origen 
        
        if type_origen_norm == 'INT' and type_destino_norm == 'FLOAT':
            new_temp = self.tercetos.nuevo('CONV_I_F', expr_origen, None, 'FLOAT',lineno=p.lineno)
            final_expr_origen = new_temp
            
        elif type_origen_norm != type_destino_norm:
            msg = f"Error semántico: Asignación incompatible. No se puede asignar '{type_origen_norm}' a la variable '{id_destino}' de tipo '{type_destino_norm}'."
            self.error_manager.add(p.lineno, msg, source="parser")
            
        idx = self.tercetos.nuevo('=', id_destino, final_expr_origen,lineno=p.lineno)
        self.tercetos_antes = len(self.tercetos.tercetos)
        return int(idx.strip('[]')) + 1
    
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
        indices = []
        declaration_type = p.type
        declaration_type = p.type
        for var in p.id_list:
            self.symbol_table.update_variable_type(var, declaration_type)
            self.symbol_table.add_scope(var, data_type=p.type, uso="VARIABLE", scope="G")
            
            idx = self.tercetos.nuevo('DECL', p.type, var,lineno=p.lineno)
            indices.append(int(idx.strip('[]')))
        
        self.tercetos_antes = len(self.tercetos.tercetos)
        return indices[0] + 1
    
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
        idx = self.tercetos.nuevo('PRINT', p.expr, None,lineno=p.lineno)
        self.tercetos_antes = len(self.tercetos.tercetos)
        return int(idx.strip('[]')) + 1 # índice numérico

    @_('PRINT "(" STRING ")" ";"')
    def statement(self, p):
        idx = self.tercetos.nuevo('PRINT', p.STRING, None,lineno=p.lineno)
        self.tercetos_antes = len(self.tercetos.tercetos)
        return int(idx.strip('[]')) + 1 # índice numérico
    
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
        index_end = int(self.tercetos.nuevo('FIN_IF_ELSE', None, None).strip('[]'))

        # Índices auxiliares
        expr_indice = int(p.expr.strip('[]'))                         # último terceto de la condición
        index_else_first = expr_indice + len(p.block0) + 1            # para hacer backpatch de BF

        # Backpatch del BI → apunta al FUERA_DEL_IF
        self.tercetos.backpatch([f"[{index_BI}]"], index_end)

        # Mover el BF justo después de la condición
        self.tercetos.mover_terceto(index_BF, expr_indice + 1)

        # Mover el BI justo antes del bloque ELSE
        op = self.tercetos.tercetos[p.block1[0] ].operador
        if op == '=':
            i = p.block1[0] - 1
            op = self.tercetos.tercetos[i].operador
            while op == '+' or op == '-' or op == '*' or op == '/': 
                i = i - 1
                op = self.tercetos.tercetos[i].operador
            self.tercetos.mover_terceto(index_BI, i+1)
            self.tercetos.backpatch2(self.tercetos.tercetos[expr_indice+1],i+2)
        else:
            self.tercetos.mover_terceto(index_BI, p.block1[0])
            self.tercetos.backpatch2(self.tercetos.tercetos[expr_indice+1],p.block1[0]+1)

        #self.tercetos.mover_terceto(index_BI, index_else_last)

        self.tercetos_antes = len(self.tercetos.tercetos)
        return expr_indice + 1 # índice numérico

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

    #Falta el endif
    @_('IF "(" expr ")" block ELSE block error ";"')
    def statement(self, p):
        self.errok()
        msg = "Error: falta endif al final del if"
        self.error_manager.add(p.lineno, msg, source="parser")

    # 2. IF-only statement
    @_('IF "(" expr ")" block ENDIF ";" %prec ELSE')
    def statement(self, p):
        
        #Creamos el terceto BF y obtenemos su indice
        index_BF = self.tercetos.nuevo('BF', p.expr, self.tercetos.PENDIENTE,lineno=p.lineno)

        #Indices auxiliares
        expr_indice = int(p.expr.strip('[]'))       #ultimo terceto de la condicion
        index_endif = len(self.tercetos.tercetos)   #instruccion endif
        
        # Backpatch del BF → apunta al final del if
        self.tercetos.backpatch([index_BF], index_endif)
    
        #Movemos el terceto BF luego de la condicion del if
        self.tercetos.mover_terceto(int(index_BF.strip('[]')),expr_indice+1)

        #Etiqueta de fin del if
        self.tercetos.nuevo("FIN_IF", None, None,lineno=p.lineno)

        self.tercetos_antes = len(self.tercetos.tercetos)
        return expr_indice  # índice numérico
            
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

    #Falta el endif
    @_('IF "(" expr ")" block error ";" %prec ELSE')
    def statement(self, p):
        self.errok()
        msg = "Error: falta endif al final del if"
        self.error_manager.add(p.lineno, msg, source="parser")

    #====================================== FUNCTION ===================================================
    # Function statement
    @_('type ID "(" param_list ")" "{" statement_list "}" ";"')
    def statement(self, p):
        index_FUNC = self.tercetos.nuevo('FUNC', p.ID, p.type) # Generar terceto FUNC (en la posición temporal)
        
        # Generar terceto END_FUNC
        index_end = self.tercetos.nuevo('END_FUNC', p.ID, None)

        op = self.tercetos.tercetos[p.statement_list[0] - 1].operador
        if op == '=':
            i = p.statement_list[0] - 2
            op = self.tercetos.tercetos[i].operador
            while op == '+' or op == '-' or op == '*' or op == '/' or op == 'CONV_I_F': 
                i = i - 1
                op = self.tercetos.tercetos[i].operador
            self.tercetos.mover_terceto(int(index_FUNC.strip('[]')), i+1)
        else:
            self.tercetos.mover_terceto(int(index_FUNC.strip('[]')), p.statement_list[0] - 1)


        index_return = self.verifica_return(p.ID, p.type, p.statement_list[0], len(self.tercetos.tercetos)-1)
        if index_return is not None:
            end_func_idx = int(index_end.strip('[]'))
            self.tercetos.mover_terceto(index_return, end_func_idx)
        
        # Agrega ámbito a las variables de la función
        # Los nuevos tercetos de copia (COPY_VALOR/R) quedan ahora inmediatamente después de FUNC.
        self.symbol_table.actualizar_scope_bloque_automatica(p.ID, self.tercetos.tercetos, p.statement_list[0] -1, int(index_end.strip('[]')))

        self.symbol_table.add_function(p.ID, p.type, p.param_list)
        
        

        self.tercetos_antes = len(self.tercetos.tercetos)
        return p.statement_list[0] + 1
    
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
        
        #Capturar el índice inicial de la condición, osea el terceto de la condicion final
        expr_indice = int(p.expr.strip('[]')) 
        
        t_cond = self.tercetos.tercetos[expr_indice]
    
        #Esto toma la el primer operando de la condicion while
        if isinstance(t_cond.op1, str) and t_cond.op1.startswith('['):
            etiqueta_condicion = int(t_cond.op1.strip('[]')) # apunta al primer terceto de la condicion
        else:
            etiqueta_condicion = expr_indice 

        # Generar BF pendiente
        index_BF = self.tercetos.nuevo('BF', p.expr, self.tercetos.PENDIENTE,lineno=p.lineno)
        
        # Genera BI que salte al primer operando de la condicion del while
        self.tercetos.nuevo('BI', f"[{etiqueta_condicion}]", None,lineno=p.lineno)
        
        # índice del primer terceto después del bucle.
        index_end_while = len(self.tercetos.tercetos)
        
        # Toma la instrucción de salto BF pendiente y rellena su campo PENDIENTE 
        self.tercetos.backpatch([index_BF], index_end_while)
        
        self.tercetos.mover_terceto(int(index_BF.strip('[]')),expr_indice+1)

        self.tercetos.nuevo("FIN_WHILE", None, None,lineno=p.lineno)

        self.tercetos_antes = len(self.tercetos.tercetos)
        return expr_indice + 1  # índice numérico
        
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

    #falta do
    @_('WHILE "(" expr ")"  block ";"')
    def statement(self, p):
        self.errok()
        msg = "Error: falta el do despues del while"
        self.error_manager.add(p.lineno, msg, source="parser")
    
    #====================================== FUNCTION ===================================================

    # Lista de parametros
    @_('param_list "," param')
    def param_list(self, p):
        # Extraemos los nombres de los parámetros
        existing_names = [param[-1] for param in p.param_list]
        new_name = p.param[-1]

        # Verificamos si ya existe
        if new_name in existing_names:
            msg = f"Error: parametro repetido {new_name}"
            self.error_manager.add(p.lineno, msg, source="parser")
            return p.param_list  # Ignora el duplicado

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
    
    # Captura errores dentro del bloque
    @_('"{" error "}"')
    def block(self, p):
        self.errok()
        msg = "Error dentro del bloque"
        self.error_manager.add(p.lineno, msg, source="parser")

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
        func_id = p.ID # nombre de la función
        args_reales = p.arg_list # lista de argumentos reales: [('arrow', expr, ID_formal), ...]
        func_entry = self.symbol_table.get_token(func_id, uso_preferido="FUNCION") # buscar la función en la tabla de símbolos
        
        if not func_entry or func_entry.get("Uso") != "FUNCION": # función no declarada o no es funcion
            msg = f"Error: La función '{func_id}' no está declarada."
            self.error_manager.add(p.lineno, msg, source="parser")

            self.errok()
            return None
        
        params_formales_def = func_entry.get("parameters", []) # lista de parámetros formales definidos
        
        formal_map = {param[-1]: param[-2].upper() for param in params_formales_def} # diccionario con el parámetro formal y su tipo {ID_param_formal: Tipo_param_formal}
        
        if len(args_reales) != len(params_formales_def): # cantidad de argumentos no coincide
            msg = f"Error: La función '{func_id}' espera {len(params_formales_def)} argumentos, pero se proporcionaron {len(args_reales)}."
            self.error_manager.add(p.lineno, msg, source="parser")
            self.errok()
            return None
            
        processed_args = [None] * len(params_formales_def) # lista almacenará los argumentos en el orden de definición formal.
        arg_names_used = set() # conjunto para rastrear nombres de parámetros formales ya usados
        
        for arg_real in args_reales: # arg_real es ('arrow', expr, ID_formal)
            
            # Extraemos el nombre del parámetro formal que se está especificando:
            formal_name = arg_real[2] 
            
            if formal_name not in formal_map: 
                msg = f"Error: El parámetro formal '{formal_name}' no existe en la definición de la función '{func_id}'."
                self.error_manager.add(p.lineno, msg, source="parser")
                self.errok()
                return None
                
            if formal_name in arg_names_used:
                msg = f"Error: El parámetro formal '{formal_name}' fue especificado múltiples veces en la llamada a '{func_id}'."
                self.error_manager.add(p.lineno, msg, source="parser")
                self.errok()
                return None
            
            arg_names_used.add(formal_name)
            
            # busca la posición 'i' del parámetro formal en la definición
            i = next(j for j, param_def in enumerate(params_formales_def) if param_def[-1] == formal_name)
            
            param_formal_type = formal_map[formal_name] # Tipo esperado ('INT' o 'FLOAT')
            arg_real_value = arg_real[1]
            arg_real_type = self.get_type_of_value(arg_real_value) # Tipo real del argumento
            
            final_arg_value = arg_real_value # valor final del argumento (posible conversión)

            if arg_real_type is None:
                msg = f"Error: No se pudo determinar el tipo del argumento para el parámetro formal '{formal_name}' en la función '{func_id}'."
                self.error_manager.add(p.lineno, msg, source="parser")
                self.errok()
                continue

            # Coerción: INT a FLOAT (Segura)
            if arg_real_type.upper() == 'INT' and param_formal_type == 'FLOAT':
                new_temp = self.tercetos.nuevo('CONV_I_F', arg_real_value, None, 'FLOAT',lineno=p.lineno)
                final_arg_value = new_temp
                                
            # Incompatibilidad de Tipos
            elif arg_real_type.upper() != param_formal_type:
                msg = f"Error: Tipo de argumento incompatible para el parámetro formal '{formal_name}' en la función '{func_id}'. Se esperaba '{param_formal_type}', pero se recibió '{arg_real_type}'."
                self.error_manager.add(p.lineno, msg, source="parser")
                # Mantenemos el valor original
                
            # Almacenamos el argumento en la posición 'i' (ordenado según la definición formal)
            processed_args[i] = ('arrow', final_arg_value, formal_name)

        # Generar tercetos '->' y 'CALL' en el ORDEN FORMAL
        for arg in processed_args:
            if arg: 
                op1_val = arg[1] # El ID/Terceto con el valor
                op2_val = arg[2] # El ID del parámetro formal (W, Z, X, J)
                self.tercetos.nuevo('->', op1_val, op2_val,lineno=p.lineno) 
            
        call_result_type = func_entry.get("data_type")
        temp = self.tercetos.nuevo('CALL', func_id, len(processed_args), call_result_type.upper(),lineno=p.lineno)
        self.tercetos_antes = len(self.tercetos.tercetos)
        return temp # índice del terceto CALL

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
        type0 = self.get_type_of_value(p.expr0)
        type1 = self.get_type_of_value(p.expr1)

        if type0 == 'FLOAT' or type1 == 'FLOAT':
            result_type = 'FLOAT'
        else:
            result_type = 'INT'

        temp = self.tercetos.nuevo('+', p.expr0, p.expr1, result_type,lineno=p.lineno)
        return temp 

    @_('expr "-" expr')
    def expr(self, p):
        type0 = self.get_type_of_value(p.expr0)
        type1 = self.get_type_of_value(p.expr1)

        if type0 == 'FLOAT' or type1 == 'FLOAT':
            result_type = 'FLOAT'
        else:
            result_type = 'INT'

        temp = self.tercetos.nuevo('-', p.expr0, p.expr1, result_type,lineno=p.lineno)
        return temp 

    @_('expr "*" expr')
    def expr(self, p):
        type0 = self.get_type_of_value(p.expr0)
        type1 = self.get_type_of_value(p.expr1)

        if type0 == 'FLOAT' or type1 == 'FLOAT':
            result_type = 'FLOAT'
        else:
            result_type = 'INT'

        temp = self.tercetos.nuevo('*', p.expr0, p.expr1, result_type,lineno=p.lineno)
        return temp

    @_('expr "/" expr')
    def expr(self, p):
        type0 = self.get_type_of_value(p.expr0)
        type1 = self.get_type_of_value(p.expr1)

        if type0 == 'FLOAT' or type1 == 'FLOAT':
            result_type = 'FLOAT'
        else:
            result_type = 'INT'

        temp = self.tercetos.nuevo('/', p.expr0, p.expr1, result_type,lineno=p.lineno)
        return temp
    
    @_('expr ">" expr')
    def expr(self, p):
        # El resultado de una comparación es siempre booleano, representado como INT (1/0)
        result_type = 'INT' 
        temp = self.tercetos.nuevo('>', p.expr0, p.expr1, 'INT',lineno=p.lineno)
        return temp

    @_('expr "<" expr')
    def expr(self, p):
        temp = self.tercetos.nuevo('<', p.expr0, p.expr1, 'INT',lineno=p.lineno)
        return temp
    
    @_('expr GE expr') # >=
    def expr(self, p):  
        temp = self.tercetos.nuevo('>=', p.expr0, p.expr1, 'INT',lineno=p.lineno)
        return temp
    
    @_('expr LE expr') # <=
    def expr(self, p): 
        temp = self.tercetos.nuevo('<=', p.expr0, p.expr1, 'INT',lineno=p.lineno)
        return temp
    
    @_('expr EQ expr')# ==
    def expr(self, p): 
        temp = self.tercetos.nuevo('==', p.expr0, p.expr1, 'INT',lineno=p.lineno)
        return temp
    
    @_('expr NE expr') # !=
    def expr(self, p): 
        temp = self.tercetos.nuevo('!=', p.expr0, p.expr1, 'INT',lineno=p.lineno)
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