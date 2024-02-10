"""Modulo para generar codigo Python a partir de un arbol sintactico abstracto"""

from analizador.analizador import Nodo


class Generador:
    """Generador de codigo Python"""

    def __init__(self, arbol: Nodo) -> None:
        """Inicializa el generador"""
        self.arbol = arbol

    def generar(self) -> str:
        """Genera codigo Python"""
        return self.arbol.generar()
