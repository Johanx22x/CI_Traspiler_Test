#!/usr/bin/env python3
"""Analizador léxico y sintáctico"""

from more_itertools import peekable
from explorador.explorador import Token
from utilidades.errores import ErrorSintactico

""" FORMATO DEL ARBOL SINTACTICO ABSTRACTO
DECLARACION ::= TIPO_DATO IDENTIFICADOR ASIGNACION EXPRESION PUNTO_Y_COMA
ASIGNACION ::= IDENTIFICADOR OPERADOR EXPRESION PUNTO_Y_COMA
PARAMETROS ::= TIPO_DATO IDENTIFICADOR (COMA TIPO_DATO IDENTIFICADOR)*
LLAMADA_FUNCION ::= IDENTIFICADOR PARENTESIS_IZQUIERDO (PARAMETROS)* PARENTESIS_DERECHO (PUNTO_Y_COMA)?
EXPRESION ::= FACTOR ((OPERADOR | COMPARADOR) FACTOR)*
FACTOR ::= IDENTIFICADOR | NUMERO_ENTERO | NUMERO_FLOTANTE | CADENA | BOOLEANO | PARENTESIS_IZQUIERDO EXPRESION PARENTESIS_DERECHO | LLAMADA_FUNCION
BIFURCACION ::= si PARENTESIS_IZQUIERDO EXPRESION PARENTESIS_DERECHO LLAVE_IZQUIERDA (DECLARACION | ASIGNACION | CICLO | BIFURCACION | LLAMADA_FUNCION)* LLAVE_DERECHA (sino LLAVE_IZQUIERDA (DECLARACION | ASIGNACION | CICLO | LLAMADA_FUNCION)* LLAVE_DERECHA)?
CICLO ::= mientras PARENTESIS_IZQUIERDO EXPRESION PARENTESIS_DERECHO LLAVE_IZQUIERDA (DECLARACION | ASIGNACION | CICLO | BIFURCACION | LLAMADA_FUNCION)* LLAVE_DERECHA
DECLARACION_FUNCION ::= funcion IDENTIFICADOR PARENTESIS_IZQUIERDO (PARAMETROS)* PARENTESIS_DERECHO LLAVE_IZQUIERDA (DECLARACION | ASIGNACION | CICLO | BIFURCACION | LLAMADA_FUNCION | RETORNO)* LLAVE_DERECHA
RETORNO ::= retornar EXPRESION PUNTO_Y_COMA
PROGRAMA ::= { (DECLARACION | ASIGNACION | CICLO | BIFURCACION | DECLARACION_FUNCION | LLAMADA_FUNCION)* }
"""


class Nodo:
    """Nodo de un árbol sintáctico abstracto"""

    def __init__(self, tipo, contenido, atributos=None):
        """Inicializa un nodo con un tipo, contenido y atributos"""
        self.tipo = tipo
        self.contenido = contenido
        self.atributos = atributos or {}

    def preorden(self) -> str:
        """Devuelve una representación en cadena del árbol en preorden"""
        cadena = f"<'{self.tipo}', '{self.contenido}', {self.atributos}>" + "\n"
        if "hijos" in self.atributos:
            for hijo in self.atributos["hijos"]:
                cadena += hijo.preorden()
        return cadena

    def generar(self, nivel=0) -> str:
        """Genera código Python a partir del árbol"""
        if self.tipo == "PROGRAMA":
            codigo = ""
            for hijo in self.atributos["hijos"]:
                codigo += hijo.generar()
            return codigo
        elif self.tipo == "DECLARACION":
            return "\t"*nivel + f"{self.atributos['identificador']} = {self.atributos['expresion'].generar()}\n"
        elif self.tipo == "ASIGNACION":
            return "\t"*nivel + f"{self.atributos['identificador']} = {self.atributos['expresion'].generar()}\n"
        elif self.tipo == "LLAMADA_FUNCION":
            parametros = ", ".join([param.generar() for param in self.atributos["parametros"] if param.tipo != "COMA"])
            if self.atributos["identificador"] == "imprimir":
                return "\t"*nivel + f"print({parametros})\n"
            return "\t"*nivel + f"{self.atributos['identificador']}({parametros})\n"
        elif self.tipo == "RETORNO":
            return "\t"*nivel + f"return {self.atributos['expresion'].generar()}\n"
        elif self.tipo == "EXPRESION":
            if self.atributos["parentesis"]:
                return f"({self.atributos['factor_izquierdo'].generar()} {self.atributos['operador']} {self.atributos['factor_derecho'].generar()})"
            return f"{self.atributos['factor_izquierdo'].generar()} {self.atributos['operador']} {self.atributos['factor_derecho'].generar()}"
        elif self.tipo in ["NUMERO_ENTERO", "NUMERO_FLOTANTE", "CADENA"]:
            return self.atributos["valor"]
        elif self.tipo == "BOOLEANO":
            if self.atributos["valor"] == "verdadero":
                return "True"
        elif self.tipo == "IDENTIFICADOR":
            return self.atributos["identificador"]
        elif self.tipo == "BIFURCACION":
            codigo = "\t"*nivel + f"if ({self.atributos['expresion'].generar()}):\n"
            for hijo in self.atributos["hijos"]:
                codigo += hijo.generar(nivel + 1)
            return codigo
        elif self.tipo == "BIFURCACION_SINO":
            codigo = "\t"*nivel + "else:\n"
            for hijo in self.atributos["hijos"]:
                codigo += hijo.generar(nivel + 1)
            return codigo
        elif self.tipo == "CICLO":
            codigo = "\t"*nivel + f"while ({self.atributos['expresion'].generar()}):\n"
            for hijo in self.atributos["hijos"]:
                codigo += hijo.generar(nivel + 1)
            return codigo
        elif self.tipo == "DECLARACION_FUNCION":
            codigo = "\t"*nivel + f"def {self.atributos['identificador']}("
            parametros = [param.generar() for param in self.atributos["parametros"] if param.nombre != "TIPO_DATO"]
            tipo_parametros = [param.generar() for param in self.atributos["parametros"] if param.nombre == "TIPO_DATO"]
            tipos_python = {
                "entero": "int",
                "flotante": "float",
                "cadena": "str",
                "booleano": "bool",
            }
            tipo_parametros = [tipos_python[tipo] for tipo in tipo_parametros]
            parametros = ", ".join([f"{param}: {tipo}" for tipo, param in zip(tipo_parametros, parametros)])
            codigo += f"{parametros}):\n"
            for hijo in self.atributos["hijos"]:
                codigo += hijo.generar(nivel + 1)
            return codigo
        else:
            return ""

    def __str__(self):
        """Devuelve una representación en cadena del nodo"""
        return f"<'{self.tipo}', '{self.contenido}', {self.atributos}>"

    def __repr__(self):
        """Devuelve una representación en cadena del nodo"""
        return str(self)


class Analizador:
    """Analizador léxico y sintáctico"""

    def __init__(self, tokens):
        """Inicializa el analizador con una lista de tokens"""
        self.tokens = peekable(tokens)

    def generar_asa(self) -> Nodo:
        """Genera un árbol sintáctico abstracto a partir de los tokens"""
        self.tokens = iter(self.tokens)
        return self.alcance()

    def alcance(self, padre=None) -> Nodo:
        """Analiza un alcance"""
        if padre is None:
            nodo = Nodo("PROGRAMA", "", {"hijos": []})
        else:
            nodo = padre
        nodo.atributos["hijos"] = []
        for token in self.tokens:
            if token.nombre == "LLAVE_DERECHA" and padre is not None:
                break
            if token.nombre == "PALABRA_RESERVADA":
                if token.valor == "funcion":
                    nodo.atributos["hijos"].append(self.declaracion_funcion())
                elif token.valor == "si":
                    nodo.atributos["hijos"].append(self.bifurcacion())
                elif token.valor == "sino":
                    nodo.atributos["hijos"].append(self.bifurcacion_sino())
                elif token.valor == "mientras":
                    nodo.atributos["hijos"].append(self.ciclo())
                elif padre is not None and token.valor == "retornar":
                    if padre.tipo == "DECLARACION_FUNCION":
                        nodo.atributos["hijos"].append(self.retorno())
                else:
                    raise ErrorSintactico(
                        f"Se esperaba una declaración, asignación, ciclo, bifurcación o declaración de función, pero se encontró '{token.valor}'",
                        token.linea,
                        token.columna,
                    )
            elif token.nombre == "TIPO_DATO":
                nodo.atributos["hijos"].append(self.declaracion(token))
            elif token.nombre == "IDENTIFICADOR":
                next_token = next(self.tokens)
                if next_token.nombre == "ASIGNACION":
                    nodo.atributos["hijos"].append(self.asignacion(token))
                elif next_token.nombre == "PARENTESIS_IZQUIERDO":
                    nodo.atributos["hijos"].append(self.llamada_funcion(token))
                else:
                    raise ErrorSintactico(
                        f"Se esperaba una asignación o llamada a función, pero se encontró '{token.valor}'",
                        token.linea,
                        token.columna,
                    )
            elif token.nombre == "PUNTO_Y_COMA":
                continue
            else:
                raise ErrorSintactico(
                    f"Se esperaba una declaración, asignación, ciclo, bifurcación o declaración de función, pero se encontró '{token.valor}'",
                    token.linea,
                    token.columna,
                )
        return nodo

    def declaracion(self, token) -> Nodo:
        """Analiza una declaración"""
        tipo = token.valor
        identificador = next(self.tokens).valor
        asignacion = next(self.tokens)
        if asignacion.nombre != "ASIGNACION":
            raise ErrorSintactico(
                f"Se esperaba un signo de igual, pero se encontró '{asignacion.valor}'",
                asignacion.linea,
                asignacion.columna,
            )
        expresion = self.expresion()
        return Nodo(
            "DECLARACION",
            "",
            {"tipo": tipo, "identificador": identificador, "expresion": expresion},
        )

    def asignacion(self, token) -> Nodo:
        """Analiza una asignación"""
        identificador = token.valor
        expresion = self.expresion()
        punto_y_coma = next(self.tokens)
        if punto_y_coma.nombre != "PUNTO_Y_COMA":
            raise ErrorSintactico(
                f"Se esperaba un punto y coma, pero se encontró '{punto_y_coma.valor}'",
                punto_y_coma.linea,
                punto_y_coma.columna,
            )
        return Nodo(
            "ASIGNACION", "", {"identificador": identificador, "expresion": expresion}
        )

    def llamada_funcion(self, token) -> Nodo:
        """Analiza una llamada a función"""
        identificador = token.valor
        parametros = []
        while True:
            token = self.tokens.peek()
            if token.nombre == "PARENTESIS_DERECHO":
                next(self.tokens)
                break
            parametros.append(self.expresion())
        punto_y_coma = next(self.tokens)
        if punto_y_coma.nombre != "PUNTO_Y_COMA":
            raise ErrorSintactico(
                f"Se esperaba un punto y coma, pero se encontró '{punto_y_coma.valor}'",
                punto_y_coma.linea,
                punto_y_coma.columna,
            )
        return Nodo(
            "LLAMADA_FUNCION",
            "",
            {"identificador": identificador, "parametros": parametros},
        )

    def expresion(self, parentesis=False) -> Nodo:
        """Analiza una expresión"""
        factor = self.factor()
        operador = self.tokens.peek()
        if operador.nombre == "COMA":
            return factor
        while operador.nombre in ["OPERADOR", "COMPARADOR"]:
            next(self.tokens)
            factor = Nodo(
                "EXPRESION",
                "",
                {
                    "operador": operador.valor,
                    "factor_izquierdo": factor,
                    "factor_derecho": self.factor(),
                    "parentesis": parentesis,
                },
            )
            operador = self.tokens.peek()
        return factor

    def factor(self) -> Nodo:
        """Analiza un factor"""
        token = next(self.tokens)
        if token.nombre == "IDENTIFICADOR":
            next_token = self.tokens.peek()
            if next_token.nombre == "PARENTESIS_IZQUIERDO":
                return self.referencia_funcion(token)
            return Nodo("IDENTIFICADOR", "", {"identificador": token.valor})
        elif token.nombre == "NUMERO_ENTERO":
            return Nodo("NUMERO_ENTERO", "", {"valor": token.valor})
        elif token.nombre == "NUMERO_FLOTANTE":
            return Nodo("NUMERO_FLOTANTE", "", {"valor": token.valor})
        elif token.nombre == "CADENA":
            return Nodo("CADENA", "", {"valor": token.valor})
        elif token.nombre == "BOOLEANO":
            return Nodo("BOOLEANO", "", {"valor": token.valor})
        elif token.nombre == "COMA":
            return Nodo("COMA", "", {"valor": token.valor})
        elif token.nombre == "PARENTESIS_IZQUIERDO":
            expresion = self.expresion(True)
            parentesis_derecho = next(self.tokens)
            if parentesis_derecho.nombre == "COMA":
                return expresion
            if parentesis_derecho.nombre != "PARENTESIS_DERECHO":
                raise ErrorSintactico(
                    f"Se esperaba un paréntesis derecho, pero se encontró '{parentesis_derecho.valor}'",
                    parentesis_derecho.linea,
                    parentesis_derecho.columna,
                )
            return expresion
        else:
            raise ErrorSintactico(
                f"Se esperaba un identificador, número entero, número flotante, cadena, booleano o paréntesis izquierdo, pero se encontró '{token.valor}'",
                token.linea,
                token.columna,
            )

    def referencia_funcion(self, token) -> Nodo:
        """Analiza una referencia a función"""
        identificador = token.valor
        parametros = []
        while True:
            token = self.tokens.peek()
            if token.nombre == "PARENTESIS_DERECHO":
                next(self.tokens)
                break
            if token.nombre == "COMA":
                next(self.tokens)
                continue
            parametros.append(self.expresion())
        return Nodo(
            "LLAMADA_FUNCION",
            "",
            {"identificador": identificador, "parametros": parametros},
        )

    def declaracion_funcion(self) -> Nodo:
        """Analiza una declaración de función"""
        identificador = next(self.tokens)
        if identificador.nombre != "IDENTIFICADOR":
            raise ErrorSintactico(
                f"Se esperaba un identificador, pero se encontró '{identificador.valor}'",
                identificador.linea,
                identificador.columna,
            )
        parentesis_izquierdo = next(self.tokens)
        if parentesis_izquierdo.nombre != "PARENTESIS_IZQUIERDO":
            raise ErrorSintactico(
                f"Se esperaba un paréntesis izquierdo, pero se encontró '{parentesis_izquierdo.valor}'",
                parentesis_izquierdo.linea,
                parentesis_izquierdo.columna,
            )
        parametros = []
        while True:
            token = next(self.tokens)
            if token.nombre == "PARENTESIS_DERECHO":
                break
            if token.nombre == "COMA":
                continue
            parametros.append(token)
        llave_izquierda = next(self.tokens)
        if llave_izquierda.nombre != "LLAVE_IZQUIERDA":
            raise ErrorSintactico(
                f"Se esperaba una llave izquierda, pero se encontró '{llave_izquierda.valor}'",
                llave_izquierda.linea,
                llave_izquierda.columna,
            )
        # Recursive descent parsing
        # Llamar a alcance con el padre como el nodo actual
        return self.alcance(
            Nodo(
                "DECLARACION_FUNCION",
                "",
                {"identificador": identificador.valor, "parametros": parametros},
            )
        )

    def bifurcacion(self) -> Nodo:
        """Analiza una bifurcación"""
        parentesis_izquierdo = next(self.tokens)
        if parentesis_izquierdo.nombre != "PARENTESIS_IZQUIERDO":
            raise ErrorSintactico(
                f"Se esperaba un paréntesis izquierdo, pero se encontró '{parentesis_izquierdo.valor}'",
                parentesis_izquierdo.linea,
                parentesis_izquierdo.columna,
            )
        expresion = self.expresion()
        parentesis_derecho = next(self.tokens)
        if parentesis_derecho.nombre != "PARENTESIS_DERECHO":
            raise ErrorSintactico(
                f"Se esperaba un paréntesis derecho, pero se encontró '{parentesis_derecho.valor}'",
                parentesis_derecho.linea,
                parentesis_derecho.columna,
            )
        llave_izquierda = next(self.tokens)
        if llave_izquierda.nombre != "LLAVE_IZQUIERDA":
            raise ErrorSintactico(
                f"Se esperaba una llave izquierda, pero se encontró '{llave_izquierda.valor}'",
                llave_izquierda.linea,
                llave_izquierda.columna,
            )
        # Recursive descent parsing
        # Llamar a alcance con el padre como el nodo actual
        return self.alcance(Nodo("BIFURCACION", "", {"expresion": expresion}))

    def bifurcacion_sino(self) -> Nodo:
        """Analiza un sino"""
        llave_izquierda = next(self.tokens)
        if llave_izquierda.nombre != "LLAVE_IZQUIERDA":
            raise ErrorSintactico(
                f"Se esperaba una llave izquierda, pero se encontró '{llave_izquierda.valor}'",
                llave_izquierda.linea,
                llave_izquierda.columna,
            )
        # Recursive descent parsing
        # Llamar a alcance con el padre como el nodo actual
        return self.alcance(Nodo("BIFURCACION_SINO", ""))

    def ciclo(self) -> Nodo:
        """Analiza un ciclo"""
        parentesis_izquierdo = next(self.tokens)
        if parentesis_izquierdo.nombre != "PARENTESIS_IZQUIERDO":
            raise ErrorSintactico(
                f"Se esperaba un paréntesis izquierdo, pero se encontró '{parentesis_izquierdo.valor}'",
                parentesis_izquierdo.linea,
                parentesis_izquierdo.columna,
            )
        expresion = self.expresion()
        parentesis_derecho = next(self.tokens)
        if parentesis_derecho.nombre != "PARENTESIS_DERECHO":
            raise ErrorSintactico(
                f"Se esperaba un paréntesis derecho, pero se encontró '{parentesis_derecho.valor}'",
                parentesis_derecho.linea,
                parentesis_derecho.columna,
            )
        llave_izquierda = next(self.tokens)
        if llave_izquierda.nombre != "LLAVE_IZQUIERDA":
            raise ErrorSintactico(
                f"Se esperaba una llave izquierda, pero se encontró '{llave_izquierda.valor}'",
                llave_izquierda.linea,
                llave_izquierda.columna,
            )
        # Recursive descent parsing
        # Llamar a alcance con el padre como el nodo actual
        return self.alcance(Nodo("CICLO", "", {"expresion": expresion}))

    def retorno(self) -> Nodo:
        """Analiza un retorno"""
        expresion = self.expresion()
        next(self.tokens)
        return Nodo("RETORNO", "", {"expresion": expresion})


def main():
    """Función principal"""
    tokens = [
        Token("PALABRA_RESERVADA", "funcion", 0, 7, 1, 1),
        Token("IDENTIFICADOR", "main", 8, 12, 1, 9),
        Token("PARENTESIS_IZQUIERDO", "(", 12, 13, 1, 13),
        Token("PARENTESIS_DERECHO", ")", 13, 14, 1, 14),
        Token("LLAVE_IZQUIERDA", "{", 15, 16, 1, 16),
        Token("PALABRA_RESERVADA", "entero", 17, 23, 2, 1),
        Token("IDENTIFICADOR", "a", 24, 25, 2, 8),
        Token("ASIGNACION", "=", 26, 27, 2, 10),
        Token("NUMERO_ENTERO", "5", 28, 29, 2, 12),
        Token("PUNTO_Y_COMA", ";", 29, 30, 2, 13),
        Token("LLAVE_DERECHA", "}", 31, 32, 3, 1),
    ]

    analizador = Analizador(tokens)
    asa = analizador.generar_asa()
    print(asa)


if __name__ == "__main__":
    main()
