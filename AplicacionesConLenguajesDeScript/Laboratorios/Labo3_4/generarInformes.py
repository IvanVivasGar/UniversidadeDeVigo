def generar_informe(entrada: str) -> str:
    lineas = entrada.strip().split("\n")
    nombres_empresas = lineas[0].split(", ")[::2]  # Extraer nombres de empresas
    datos = [linea.split(", ") for linea in lineas[1:]]

    informe = "Informe de Ventas\n===================\n"

    for fila in datos:
        empresa_id, fecha, *ventas = fila
        empresa_nombre = nombres_empresas[int(empresa_id) - 1]
        ventas = list(map(int, ventas))
        total_ventas = sum(ventas)
        promedio_ventas = total_ventas / len(ventas)

        informe += (f"Empresa: {empresa_nombre}\n"
                    f"Semana del: {fecha}\n"
                    f"Ventas diarias: {ventas}\n"
                    f"Total semanal: {total_ventas}\n"
                    f"Promedio diario: {promedio_ventas:.2f}\n"
                    f"-------------------------\n")

    return informe

# Ejemplo de uso:
datos = """Microsoft, 1, Apple, 2, Google, 3, Yahoo, 4
1, 2015-01-09, 120, 34, 256, 78, 93, 222, 5
2, 2015-01-09, 900, 346, 730, 456, 33, 345, 234
3, 2015-01-09, 934, 922, 866, 444, 235, 999, 789
4, 2015-01-09, 45, 56, 78, 23, 44, 90, 9"""

print(generar_informe(datos))