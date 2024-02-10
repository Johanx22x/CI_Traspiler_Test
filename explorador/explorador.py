#!/usr/bin/env python3
"""Explorador de tokens."""

import re
import sys
from typing import List, Tuple
import pickle
from utilidades.errores import ErrorSintactico

TOKENS: List[Tuple[str, str]] = [
    ("COMENTARIO", r"//.*"),
    ("COMENTARIO_MULTILINEA", r"/\*(.|\n)*?\*/"),
    (
        "PALABRA_RESERVADA",
        r"(sino|si|fin_si|mientras|fin_mientras|para|funcion|fin_funcion|retornar)",
    ),
    ("TIPO_DATO", r"(entero|flotante|texto|booleano)"),
    ("BOOLEANO", r"(verdadero|falso)"),
    ("NUMERO_FLOTANTE", r"\d+\.\d+"),
    ("NUMERO_ENTERO", r"\d+"),
    ("CADENA", r'".*"'),
    ("COMPARADOR", r"(==|!=|<=|>=|<|>)"),
    ("ASIGNACION", r"="),
    ("OPERADOR", r"[+\-*/]"),
    ("PARENTESIS_IZQUIERDO", r"\("),
    ("PARENTESIS_DERECHO", r"\)"),
    ("LLAVE_IZQUIERDA", r"\{"),
    ("LLAVE_DERECHA", r"\}"),
    ("COMA", r","),
    ("PUNTO_Y_COMA", r";"),
    ("ESPACIO", r"\s+"),
    ("IDENTIFICADOR", r"[a-zA-Z][a-zA-Z0-9_]*"),
]


class Token:
    """Clase que representa un token.

    Atributos:
        nombre (str): Nombre del token.
        valor (str): Valor del token.
        inicio (int): Posición inicial del token.
        fin (int): Posición final del token.
        linea (int): Línea del token.
        columna (int): Columna del token.
    """

    def __init__(
        self, nombre: str, valor: str, inicio: int, fin: int, linea: int, columna: int
    ) -> None:
        """Constructor de la clase Token.

        Args:
            nombre (str): Nombre del token.
            valor (str): Valor del token.
            inicio (int): Posición inicial del token.
            fin (int): Posición final del token.
            linea (int): Línea del token.
            columna (int): Columna del token.
        """
        self.nombre = nombre
        self.valor = valor
        self.inicio = inicio
        self.fin = fin
        self.linea = linea
        self.columna = columna

    def generar(self) -> str:
        """Genera el código Python de un token.

        Returns:
            str: Código Python del token.
        """
        return f"{self.valor}"

    def __str__(self) -> str:
        """Convierte el token a una cadena de texto.

        Returns:
            str: Cadena de texto que representa el token.
        """
        return f"<{self.nombre}, {self.valor}, {self.inicio}, {self.fin}, {self.linea}, {self.columna}>"

    def __repr__(self) -> str:
        """Convierte el token a una cadena de texto.

        Returns:
            str: Cadena de texto que representa el token.
        """
        return self.__str__()


class Explorador:
    """Clase que representa un explorador de tokens.

    Atributos:
        cadena (str): Cadena de texto a explorar.
        pos (int): Posición actual en la cadena.
        tokens (List[Token]): Lista de tokens encontrados.
        fila (int): Fila actual en la cadena.
        columna (int): Columna actual en la cadena.
    """

    def __init__(self, cadena: str) -> None:
        """Constructor de la clase Explorador.

        Args:
            cadena (str): Cadena de texto a explorar.
        """
        self.cadena = cadena
        self.pos = 0
        self.tokens = []
        self.fila = 0
        self.columna = 0

    def obtener_fila_columna(self, pos: int) -> Tuple[int, int]:
        """Obtiene la fila y columna de un caracter en una cadena.

        Args:
            pos (int): Posición del caracter.

        Returns:
            Tuple[int, int]: Fila y columna del caracter.
        """
        fila = self.cadena[:pos].count("\n") + 1
        columna = pos - self.cadena[:pos].rfind("\n")
        return fila, columna

    def escanear(self) -> List[Token]:
        """Escanea una cadena de texto y devuelve una lista de tokens.

        Returns:
            List[Token]: Lista de tokens.
        """
        while self.pos < len(self.cadena):
            match = None
            self.fila, self.columna = self.obtener_fila_columna(self.pos)
            for nombre, patron in TOKENS:
                regex = re.compile(patron)
                match = regex.match(self.cadena, self.pos)
                if match:
                    valor = match.group(0)
                    # Ignorar espacios, comentarios y comentarios multilinea
                    if nombre not in ["ESPACIO", "COMENTARIO", "COMENTARIO_MULTILINEA"]:
                        self.tokens.append(
                            Token(
                                nombre,
                                valor,
                                self.pos,
                                match.end(0),
                                self.fila,
                                self.columna,
                            )
                        )
                    self.pos = match.end(0)
                    break
            if not match:
                inicio_linea = self.cadena[: self.pos].rfind("\n") + 1
                fin_linea = self.cadena.find("\n", self.pos)
                linea = self.cadena[inicio_linea:fin_linea]
                posicion_error = self.pos - inicio_linea
                raise ErrorSintactico(
                    f"\n\n\t{linea}\n\t{' ' * (posicion_error)}^\n", self.fila, self.columna
                )
        return self.tokens


def main() -> None:
    """Función principal del programa.

    Lee un archivo de texto, escanea su contenido y escribe los tokens en un archivo de salida.

    Returns:
        None
    """
    try:
        with open(sys.argv[1], "r", encoding="utf-8") as archivo:
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

    tokens = Explorador(cadena).escanear()

    try:
        # Guardar la estructura de tokens en un archivo binario
        with open("tokens.bin", "wb") as archivo:
            pickle.dump(tokens, archivo)
    except:
        print("ERROR: no se puede escribir el archivo de salida.")
        sys.exit(-1)

    print(tokens)


if __name__ == "__main__":
    main()
