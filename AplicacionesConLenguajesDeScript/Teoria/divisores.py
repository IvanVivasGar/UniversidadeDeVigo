num = input("Dame un numero entero: ")
div = 2
resto = num

while div <= num and resto != 1:
    if resto % div == 0:
        print(div)
        resto = resto / div
        div -= 1
    div += 1