"""Modulo para el manejo de errores"""

class ErrorSintactico(Exception):
    """Error sintáctico"""
    def __init__(self, mensaje, linea, columna):
        super().__init__(f"error sintáctico en la línea {linea}, columna {columna}: {mensaje}")
        self.linea = linea
        self.columna = columna
