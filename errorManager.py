class ErrorManager:
    def __init__(self):
        self.errors = []

    def add(self, lineno, message, source="parser"):
        self.errors.append({
            "source": source,   # 'lexer' o 'parser'
            "line": lineno,
            "message": message
        })

    def has_errors(self):
        return len(self.errors) > 0

    def __str__(self):
        # Ordenamos los errores por número de línea (los que no tienen línea van al final)
        sorted_errors = sorted(
            self.errors,
            key=lambda e: e['line'] if e['line'] is not None else float('inf')
        )

        out = []
        for e in sorted_errors:
            line_info = f"Línea {e['line']}" if e['line'] is not None else "Sin línea"
            out.append(f"[{e['source']}] {line_info}: {e['message']}")

        return "\n".join(out)