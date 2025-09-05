from tablaSimbolos import SymbolTable
from analisisLexico import MyLexer

lexer = MyLexer()

symbol_Table = SymbolTable()
symbol_Table.load_keyword()

# Abrimos el archivo en modo lectura ('r')
with open("caso1.txt", "r", encoding="utf-8") as f:
    text = f.read()  # lee todo el contenido
    for tok in lexer.tokenize(text):
        print('type=%r, value=%r' % (tok.type, tok.value))

