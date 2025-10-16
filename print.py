from tablaSimbolos import SymbolTable


def print_ast(node, indent=0):
    prefix = "  " * indent
    symbol_Table = SymbolTable() 
    symbol_Table.load_keyword()

    COLOR_BLUE = "\033[34m"   # líneas normales
    COLOR_RED = "\033[31m"    # errores
    COLOR_RESET = "\033[0m"

    if node is None:
        # Si no hay información, mostramos error genérico
        print(f"{COLOR_RED}{prefix}Error (sin informacion){COLOR_RESET}")
        return
    
    # Caso 2: el nodo es una tupla con (lineno, None)
    if isinstance(node, tuple) and len(node) == 2 and node[1] is None and isinstance(node[0], int):
        print(f"{COLOR_RED}{prefix}Linea {node[0]} --> Error{COLOR_RESET}")
        return

    # Si es una tupla
    if isinstance(node, tuple):
        header = node[0]

        # 🔵 Línea normal
        if isinstance(header, str) and header.startswith("Linea"):
            #Error si contiene la palabra "Error"
            if "Error" in header:
                print(f"{COLOR_RED}{prefix}{header}{COLOR_RESET}")
            else:
                print(f"{COLOR_BLUE}{prefix}{header}{COLOR_RESET}")

            for elem in node[1:]:
                print_ast(elem, indent + 1)
            return

        # 🌿 Hoja simple tipo ('num_int', '3')
        if len(node) == 2 and not isinstance(node[1], (list, tuple)):
            tipo, valor = node
            if tipo == "ID" and valor in symbol_Table.keywords:
                print(f"{prefix}{valor}")
            else:
                print(f"{prefix}{tipo}: {valor}")
        else:
            print(f"{prefix}{node[0]}:")
            for elem in node[1:]:
                print_ast(elem, indent + 1)

    # Si es una lista
    elif isinstance(node, list):
        for elem in node:
            print_ast(elem, indent)

    # Si es un valor suelto (por ejemplo 'Z')
    else:
        if isinstance(node, str) and node in symbol_Table.keywords:
            print(f"{prefix}{node}")
        else:
            print(f"{prefix}ID: {node}")
