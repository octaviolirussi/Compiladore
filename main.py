import os
import sys
from tablaSimbolos import SymbolTable
from lexer import MyLexer
from parser import MyParser
from errorManager import ErrorManager


error = ErrorManager()

symbol_Table = SymbolTable(error)
symbol_Table.load_keyword()
lexer = MyLexer(symbol_Table,error)
parser = MyParser(symbol_Table,error)

# if len(sys.argv) != 2:
#     print(f"Uso: python {sys.argv[0]} <ruta_del_txt>")
#     sys.exit(1)

# ruta_txt = sys.argv[1]

# Abrimos el archivo en modo lectura ('r')
try:
    with open("pruebas/test.txt", "r", encoding="utf-8") as f:
        
        text = f.read()  # lee todo el contenido y muestra los tokens
        tokens = list(lexer.tokenize(text))

        #Muestra el parser
        tokens_iter = iter(tokens)
        result = parser.parse(tokens_iter)

except FileNotFoundError:
    print(f"No se encontró el archivo en la ruta especificada.")


symbol_Table.eliminar(parser.tercetos.tercetos)
symbol_Table.correccion_scope(parser.tercetos.tercetos)
parser.tercetos.correcciones()



#errores
# print("\nMuestra de Errores:\n")
if error.has_errors():
    print("\nSe encontraron ERRORES. El proceso se detiene.")
    print(str(error)) # Imprime todos los mensajes (incluidos warnings, si los hay)
    sys.exit(1)
else:
    # 2. Si no hay errores, verificar WARNINGS (no detienen la ejecución)
    warnings = error.get_warnings()
    if warnings:
        print(f"\nAnálisis completado con {len(warnings)} advertencias. Continuando con la generación de código/tercetos.")
        
        # Opcional: imprimir solo los warnings de forma separada
        print("\n--- ADVERTENCIAS DETECTADAS ---")
        for w in warnings:
             line_info = f"Línea {w['line']}" if w['line'] is not None else "Sin línea"
             print(f"[{w['source']}] {line_info}: {w['message']}")
        print("---------------------------------")
    else:
        print("\nAnálisis completado sin errores ni advertencias. Continuando con la generación de código/tercetos.")
        
    # Continuar la ejecución (Generación de Tercetos, etc.)
    parser.tercetos.mostrar()

#Tabla de simbolos
print("\nTabla de palabras reservadas:\n")
print(symbol_Table.keywords)
print("\n")
print(symbol_Table.show())


