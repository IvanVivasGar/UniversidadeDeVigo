# DEVOLVER EL CAMBIO

# Una maquina expendedora debe devolver el cambio en euros, con monedas de 1, 5, 10, 20, 50, 100
# Asumimos que la maquina siempre tiene monedas suficientes.

def devuelve_cambio(c: int) -> list[int]:
    monedas = [100, 50, 20, 10, 5, 1]
    cambio = []
    while c >= 1:
        for i in monedas:
            if (c / i) >= 1:
                c = c - i
                cambio.append(i)
    return cambio


v = 65
print(f"Devolver cambio de {v}: {devuelve_cambio(v)}")