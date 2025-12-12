import os
import sys
from tablaSimbolos import SymbolTable
from lexer import MyLexer
from parser import MyParser
from errorManager import ErrorManager
from codeGenerator import CodeGenerator

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
file = "pruebas/test_v1.txt"
try:
    with open(file, "r", encoding="utf-8") as f:
        
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


if error.has_errors():
    print("\nSe encontraron ERRORES. El proceso se detiene.")
    print(str(error))
    sys.exit(1)
else:
    warnings = error.get_warnings()
    if warnings:
        print(f"\nAnálisis completado con {len(warnings)} advertencias. Continuando con la generación de código/tercetos.")
        
        print("\n--- ADVERTENCIAS DETECTADAS ---")
        for w in warnings:
             line_info = f"Línea {w['line']}" if w['line'] is not None else "Sin línea"
             print(f"[{w['source']}] {line_info}: {w['message']}")
        print("---------------------------------")
    else:
        print("\nAnálisis completado sin errores ni advertencias. Continuando con la generación de código/tercetos.")
        
    parser.tercetos.mostrar()

    code_gen = CodeGenerator(symbol_Table, parser.tercetos, error)
    
    # 1. Preparar/procesar la información para el ASM
    code_gen.prepare_asm_data() 
    
    # 2. Generar el código
    asm_code = code_gen.generate_code()
    
    nombre_base_con_extension = os.path.basename(file) 
    nombre_sin_extension, _ = os.path.splitext(nombre_base_con_extension)
    archivo_salida = nombre_sin_extension + ".asm"
 
    CARPETA_SALIDA = "archivos_asm" 
    if not os.path.exists(CARPETA_SALIDA):
        os.makedirs(CARPETA_SALIDA)

    nombre_base_con_extension = os.path.basename(file) 
    nombre_sin_extension, _ = os.path.splitext(nombre_base_con_extension)

    archivo_salida = os.path.join(CARPETA_SALIDA, nombre_sin_extension + ".asm")
    
    try:
        with open(archivo_salida, "w", encoding="utf-8") as f_asm:
            f_asm.write(asm_code)
        print(f"\nArchivo de código Assembler '{archivo_salida}' generado exitosamente.")
    except Exception as e:
        print(f"\n Error al escribir el archivo ASM: {e}")


    
#Tabla de simbolos
print("\nTabla de palabras reservadas:\n")
print(symbol_Table.keywords)
print("\n")
print(symbol_Table.show())


