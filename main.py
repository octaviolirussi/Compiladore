from tablaSimbolos import SymbolTable
from analisisLexico import MyLexer

symbol_Table = SymbolTable()
symbol_Table.load_keyword()

lexer = MyLexer()

# Abrimos el archivo en modo lectura ('r')
with open("Compiladore/Pruebas/test_rangos.txt", "r", encoding="utf-8") as f:
    text = f.read()  # lee todo el contenido
    for tok in lexer.tokenize(text):
        print('type=%r, value=%r' % (tok.type, tok.value))

print("\n")
print(symbol_Table.keywords)
print("\n")
print(symbol_Table.show())