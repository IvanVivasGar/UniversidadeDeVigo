#
# Complete the 'print_full_name' function below.
#
# The function is expected to return a STRING.
# The function accepts following parameters:
#  1. STRING first
#  2. STRING last
#



def print_full_name(first, last):
    # Write your code here
    print(f'Hello {first} {last}! You just delved into python.')

if __name__ == '__main__':
    first_name = input()
    last_name = input()
    print_full_name(first_name, last_name)

#----------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    n = int(input())
    print(*range(1, n + 1), sep='')

#----------------------------------------------------------------------------------------------------------------------------

def mutate_string(string, position, character):
    l = list(string)
    l[position] = character
    string = ''.join(l)
    return string

if __name__ == '__main__':
    s = input()
    i, c = input().split()
    s_new = mutate_string(s, int(i), c)
    print(s_new)

#----------------------------------------------------------------------------------------------------------------------------



# Un formateador de números de teléfono básicamente agrupa los dígitos en grupos de tres,
# e ignora cualquier carácter que no sea un dígito. Por ejemplo, (988) 387001 se convertiría en 988 387 001.
# Además, el número puede estar precedido o no por el código de páis (dos dígitos),
# mediante el formato ‘+’ o ‘00’: +34 (988) 387001 o 0034 (988) 387001 deben convertirse en +34 988 387 001.
# Finalmente, pueden encontrarse letras de la a a la z en el número, que deben traducirse a dígitos
# siguiendo la convención: 2: a, b, c; 3: d, e, f; 4: g, h, i; 5: j, k, l; 6: m, n, o; 7: p, q, r, s; 8: t, u, v; y 9: w, y, z.
# Así, 900 ESI NFO sería 900 374 636.

def letra_digito(numero):
    l = list(numero)
    for i in range(len(l)):
        c = l[i].lower()
        if c in "abc":
            l[i] = "2"
        elif c in "def":
            l[i] = "3"
        elif c in "ghi":
            l[i] = "4"
        elif c in "jkl":
            l[i] = "5"
        elif c in "mno":
            l[i] = "6"
        elif c in "pqrs":
            l[i] = "7"
        elif c in "tuv":
            l[i] = "8"
        elif c in "wxyz":
            l[i] = "9"
    return "".join(l)

def codigo_pais(numero):
    if numero.startswith("+"):
        return numero[:3], numero[3:]
    if numero.startswith("00"):
        return "+" + numero[2:4], numero[4:]
    return "", numero

def formatear_telefono(numero):
    # Cambiar de letras a numeros
    numero = letra_digito(numero)

    # Extraer extension de pais
    extension, numero = codigo_pais(numero)

    # Extraer solo los dígitos restantes
    digitos = [c for c in numero if c.isdigit()]

    # Agrupar en bloques de tres
    numero_agrupado = " ".join("".join(digitos[i:i+3]) for i in range(0, len(digitos), 3))

    # Devolver el número formateado
    return f"{extension} {numero_agrupado}".strip()

# Ejemplo de uso
ejemplos = [
    "(988) 387001",
    "+34 (988) 387001",
    "0034 (988) 387001",
    "900 ESI NFO"
]

for ejemplo in ejemplos:
    print(formatear_telefono(ejemplo))