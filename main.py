import os
from tablaSimbolos import SymbolTable
from lexer import MyLexer
from parser import MyParser
from errorManager import ErrorManager
from print import print_ast

symbol_Table = SymbolTable()
symbol_Table.load_keyword()

error = ErrorManager()

lexer = MyLexer(symbol_Table,error)
parser = MyParser(symbol_Table,error)

# Obtener la carpeta donde está main.py
base_path = os.path.dirname(os.path.abspath(__file__))

# Pedir al usuario el nombre del archivo (por ejemplo: "prueba_2.txt")
#nombre_archivo = input("Ingresa el nombre del archivo dentro de la carpeta Pruebas: ")

# Construir la ruta al archivo de pruebas
#file_path = os.path.join(base_path, "Pruebas", nombre_archivo)

# Abrimos el archivo en modo lectura ('r')
try:
    with open("Pruebas/test_rangos.txt", "r", encoding="utf-8") as f:
        
        text = f.read()  # lee todo el contenido y muestra los tokens
        tokens = list(lexer.tokenize(text))

        print("\nLexer:\n")
        for tok in tokens:
            print('type=%r, value=%r' % (tok.type, tok.value))

        #Muestra el parser
        tokens_iter = iter(tokens)
        print("\nParser:\n")
        result = parser.parse(tokens_iter)
        print_ast(result)

except FileNotFoundError:
    print(f"No se encontró el archivo en: poner la ruta despues")

#errores
print("\nMuestra de Errores:\n")
if error.has_errors():
    print("Se encontraron errores:")
    print(error)
else:
    print("Análisis completado sin errores.")

#Tabla de simbolos
print("\nTabla de palabras reservadas:\n")
print(symbol_Table.keywords)
print("\n")
print(symbol_Table.show())
