class Terceto:
    def __init__(self, operador, op1, op2):
        self.operador = operador
        self.op1 = op1
        self.op2 = op2

    def __repr__(self):
        return f"({self.operador}, {self.op1}, {self.op2})"

class GeneradorTercetos:
    # Constante para marcar que el destino de un salto es desconocido.
    PENDIENTE = '?' 
    
    def __init__(self):
        self.tercetos = []

    def nuevo(self, operador, op1, op2=None):
        indice = len(self.tercetos)
        self.tercetos.append(Terceto(operador, op1, op2))
        return f"[{indice}]"  # devuelve referencia al resultado del terceto

    def backpatch(self, lista_indices_ref, destino_indice):
        """
        Rellena el campo de destino (op2) de los tercetos listados.

        Args:
            lista_indices_ref (list): Lista de strings de referencia (ej. ['[1]', '[3]']).
            destino_indice (int): El índice numérico del terceto destino (etiqueta).
        """
        destino_ref = f"[{destino_indice}]" 

        for indice_ref in lista_indices_ref:
            indice = int(indice_ref.strip('[]'))
            
            if 0 <= indice < len(self.tercetos):
                t = self.tercetos[indice]
                
                if t.op2 == self.PENDIENTE: 
                    t.op2 = destino_ref
                else:
                    t.op1 = destino_ref
            else:
                pass 

    #FUNCION PARA MOVER UN TERCETO (BF)
    def mover_terceto(self, indice_origen, indice_destino):
        """
        Mueve un terceto de indice_origen a indice_destino.
        Ajusta automáticamente referencias internas a tercetos.
        """
        if indice_origen == indice_destino:
            return  # nada que hacer
        
        # Extraer el terceto
        t = self.tercetos.pop(indice_origen)
        
        # Insertar en nueva posición
        self.tercetos.insert(indice_destino, t)

        # Ajustar referencias internas de los demás tercetos
        for terceto in self.tercetos:
            for attr in ['op1', 'op2']:
                val = getattr(terceto, attr)
                if isinstance(val, str) and val.startswith('['):
                    idx = int(val.strip('[]'))
                    if indice_origen < indice_destino:  # se movió hacia adelante
                        if indice_origen < idx <= indice_destino:
                            setattr(terceto, attr, f"[{idx-1}]")
                        elif idx == indice_origen:
                            setattr(terceto, attr, f"[{indice_destino}]")
                    else:  # se movió hacia atrás
                        if indice_destino <= idx < indice_origen:
                            setattr(terceto, attr, f"[{idx+1}]")
                        elif idx == indice_origen:
                            setattr(terceto, attr, f"[{indice_destino}]")

    def mostrar(self):
        print("\n=== CÓDIGO INTERMEDIO (TERCETOS) ===")
        for i, t in enumerate(self.tercetos):
            op1_str = str(t.op1)
            op2_str = str(t.op2)
            
            print(f"{i:d}: ({t.operador}, {op1_str}, {op2_str})")