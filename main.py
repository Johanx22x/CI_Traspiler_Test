#!/usr/bin/env python3
"""Transpilador de un lenguaje a Python"""

import sys
from utilidades.args import parse_args
from explorador.explorador import Explorador
from analizador.analizador import Analizador


class Transpilador:
    """Transpilador de un lenguaje a Python"""

    def __init__(self) -> None:
        """Inicializa el transpilador"""
        self.args = parse_args()

    def transpilar(self, cadena: str) -> None:
        """Transpila una cadena de texto"""
        tokens = Explorador(cadena).escanear()
        self.printd("Tokens:", tokens)

        arbol = Analizador(tokens).generar_asa()
        self.printd("Árbol:", arbol)

        with open("salida.py" if self.args.output is None else self.args.output, "w", encoding="utf-8") as archivo:
            archivo.write(arbol.generar())

    def printd(self, *args, **kwargs) -> None:
        """Imprime un mensaje si el modo depuración está activado"""
        if self.args.debug:
            print(*args, **kwargs)

    def run(self) -> None:
        """Ejecuta el transpilador"""
        try:
            with open(self.args.input_file, "r", encoding="utf-8") as archivo:
                cadena = archivo.read()
        except IndexError:
            print("ERROR: no se ha especificado un archivo de entrada.")
            sys.exit(-1)
        except FileNotFoundError:
            print("ERROR: no se ha encontrado el archivo de entrada.")
            sys.exit(-1)
        except:
            print("ERROR: no se puede leer el archivo de entrada.")
            sys.exit(-1)

        try:
            self.transpilar(cadena)
        except Exception as e:
            print(e.__class__.__name__ + ":", e)
            sys.exit(-1)


if __name__ == "__main__":
    Transpilador().run()
