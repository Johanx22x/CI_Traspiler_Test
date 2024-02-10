variable_global = 10
pi = 3.1416
x = 5 + 7 * (7 + 1) * 712
def sumar(a: int, b: int):
	resultado = a + b
	if (resultado > 10):
		resultado = resultado + 10
	return resultado
resultado_suma = sumar((5 - 3), 7)

contador = 0
while (contador < 5):
	print("Iteración ", (contador + 1))
	contador = contador + 1
if (resultado_suma > 10):
	print("El resultado de la suma es mayor que 10.")
	if (True):
		print("Esta condición siempre se cumple.")
else:
	print("El resultado de la suma es menor o igual que 10.")
