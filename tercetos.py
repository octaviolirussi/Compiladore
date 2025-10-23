class Terceto:
    def __init__(self, operador, op1, op2):
        self.operador = operador
        self.op1 = op1
        self.op2 = op2

    def __repr__(self):
        return f"({self.operador}, {self.op1}, {self.op2})"


class GeneradorTercetos:
    def __init__(self):
        self.tercetos = []

    def nuevo(self, operador, op1, op2):
        indice = len(self.tercetos)
        self.tercetos.append(Terceto(operador, op1, op2))
        return f"@{indice}"  # devuelve referencia al resultado del terceto

    def mostrar(self):
        print("\n=== CÓDIGO INTERMEDIO (TERCETOS) ===")
        for i, t in enumerate(self.tercetos):
            print(f"{i}: {t}")
