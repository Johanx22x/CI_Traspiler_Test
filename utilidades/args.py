"""Utilidades relacionadas a argumentos de linea de comando."""

import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Transpilador de un lenguaje a Python")
    parser.add_argument("-d", "--debug", action="store_true", help="Modo debug")
    parser.add_argument("-o", "--output", help="Archivo de salida")
    parser.add_argument("input_file", help="Archivo de entrada")
    return parser.parse_args()


def main():
    args = parse_args()
    print(args.debug)


if __name__ == "__main__":
    main()
