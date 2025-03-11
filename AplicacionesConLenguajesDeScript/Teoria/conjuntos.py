s0 = set()
s1 = {11}

for i in s1:
    print(i)

for i in range(len(s1)):
    print(s1[i])

primos_basicos = {2, 3, 5, 7, 11, 13}

# x = int(input("Dame un enntero: "))
x = 3

if x in primos_basicos:
    print("Es un primo basico")
else:
    print("No es un primo basico")

# conj1 = {x for x in range(2, 100) if x %2 != 0}
# conj2 = {x for x in range(100) if x %2 == 0}