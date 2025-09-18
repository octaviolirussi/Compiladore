import os
from tablaSimbolos import SymbolTable
from analisisLexico import MyLexer

symbol_Table = SymbolTable()
symbol_Table.load_keyword()

lexer = MyLexer()

# Obtener la carpeta donde está main.py
base_path = os.path.dirname(os.path.abspath(__file__))

# Pedir al usuario el nombre del archivo (por ejemplo: "prueba_2.txt")
nombre_archivo = input("Ingresa el nombre del archivo dentro de la carpeta Pruebas: ")

# Construir la ruta al archivo de pruebas
file_path = os.path.join(base_path, "Pruebas", nombre_archivo)

# Abrimos el archivo en modo lectura ('r')
try:
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()  # lee todo el contenido
        for tok in lexer.tokenize(text):
            print('type=%r, value=%r' % (tok.type, tok.value))
except FileNotFoundError:
    print(f"No se encontró el archivo en: {file_path}")

print("\n")
print(symbol_Table.keywords)
print("\n")
print(symbol_Table.show())