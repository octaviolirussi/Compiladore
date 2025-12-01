class ErrorManager:
    def __init__(self):
        self.errors = []

    def add(self, lineno, message, source="parser", msg_type="Error"):
        self.errors.append({
            "source": source,
            "line": lineno,
            "message": message,
            "type": msg_type  # "Error" o "Warning"
        })

    def has_errors(self):
        return any(e['type'] == 'Error' for e in self.errors)
    
    def get_warnings(self):
        return [e for e in self.errors if e['type'] == 'Warning']

    def __str__(self):
        # Ordenamos los mensajes por número de línea
        sorted_errors = sorted(
            self.errors,
            key=lambda e: e['line'] if e['line'] is not None else float('inf')
        )

        out = []
        for e in sorted_errors:
            line_info = f"Línea {e['line']}" if e['line'] is not None else "Sin línea"
            out.append(f"[{e['type']}][{e['source']}] {line_info}: {e['message']}")

        return "\n".join(out)