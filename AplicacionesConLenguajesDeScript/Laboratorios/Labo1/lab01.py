import math

def ejercicio01():
    print("Hola Mundo!")


def ejercicio02_03():
    def pedirNombre():
        nombre = input("Ingresa tu nombre: ")
        return nombre

    def imprimirNombre(nombre):
        print(f"Hola {nombre}, Bienvenido")

    nombre = pedirNombre()
    imprimirNombre(nombre)


def ejercicio04():
    def calcularArea(radio):
        return math.pi * math.pow(radio, 2)

    def calcularPerimetro(radio):
        return math.pi * 2 * radio

    radio = float(input("Ingresa el radio de una circunferencia: "))

    print(f"Radio: {calcularArea(radio)}")
    print(f"Perimetro: {calcularPerimetro(radio)}")


def ejercicio05():
    def fmt_coordenadas(x: float, y: float):
        return f"({str(x)}, {str(y)})"

    coordenada_x = float(input("Ingrese la coordenada en X: "))
    coordenada_y = float(input("Ingrese la coordenada en Y: "))

    print(fmt_coordenadas(coordenada_x, coordenada_y))


def ejercicio06():
    def pedir_datos():
        primer_numero = float(input("Ingrese el primer numero: "))
        operador = input("Ingresa un operador de los siguientes: (+, -, *, /, ^) ")
        segundo_numero = float(input("Ingrese el segundo numero: "))
        return primer_numero, segundo_numero, operador

    def operacion(n1, n2, op):
        if op == "+":
            return n1 + n2
        elif op == "-":
            return n1 - n2
        elif op == "*":
            return n1 - n2
        elif op == "/":
            return n1 - n2
        else:
            return math.pow(n1, n2)

    primer, segundo, operador = pedir_datos()
    print(operacion(primer, segundo, operador))

ejercicio01()
ejercicio02_03()
ejercicio04()
ejercicio05()
ejercicio06()






# EJERCICIOS HACHERRANK
import math

def weird(n):
    if n % 2 != 0:
        print("Weird")
    elif n >= 2 and n < 6:
        print("Not Weird")
    elif n > 20:
        print("Not Weird")
    else:
        print("Weird")

weird(int(input()))

def loop():
    n = int(input())
    for i in range(n):
        print(int(math.pow(i, 2)))

def write_function():
    def is_leap(year):
        leap = False

        if year % 4 == 0:
            if year % 100 == 0:
                if year % 400 == 0:
                    leap = True
            else:
                leap = True

        return leap

    year = int(input())
    print(is_leap(year))