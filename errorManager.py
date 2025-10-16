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
        # Ordenamos por número de línea
        sorted_errors = sorted(self.errors, key=lambda e: e['line'])
        out = []
        for e in sorted_errors:
            out.append(f"[{e['source']}] Línea {e['line']}: {e['message']}")
        return "\n".join(out)