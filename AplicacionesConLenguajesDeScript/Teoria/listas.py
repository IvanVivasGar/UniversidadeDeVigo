# Criba de Eratostenes
naturales = list(range(1, 100))

# Multiplos de 2
i = 3
while i < len(naturales):
    del naturales[i]
    i += 1

# Multiplos de 3
i = 5
while i < len(naturales):
    del naturales[i]
    i += 2

print(naturales)