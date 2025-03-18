class Prestamo:
    def __init__(self, num_cuotas: int, importe: float, interes: float):
        self.total_pendiente = importe * (1 + interes / 100)  # Aplica el interés al importe total
        self.num_cuotas_inicial = num_cuotas
        self.num_cuotas = num_cuotas
        self.cuota = self.total_pendiente / num_cuotas  # Calcula el importe de cada cuota

    def paga_cuota(self):
        if self.num_cuotas > 0:
            self.total_pendiente -= self.cuota
            self.num_cuotas -= 1
        else:
            print("El préstamo ya está pagado.")

    def amortiza(self, x: float):
        self.total_pendiente -= x
        if self.num_cuotas > 0:
            self.cuota = self.total_pendiente / self.num_cuotas  # Recalcula la cuota
        else:
            self.cuota = 0

    def __str__(self):
        return f"Cuotas restantes: {self.num_cuotas}, Cuota actual: {self.cuota:.2f}, Importe pendiente: {self.total_pendiente:.2f}"

# Casos de prueba
if __name__ == "__main__":
    print("Caso 1: Préstamo estándar")
    prestamo1 = Prestamo(10, 1000, 5)
    print(prestamo1)
    prestamo1.paga_cuota()
    print(prestamo1)
    prestamo1.amortiza(200)
    print(prestamo1)

    print("\nCaso 2: Pago completo anticipado")
    prestamo2 = Prestamo(5, 500, 10)
    print(prestamo2)
    prestamo2.amortiza(prestamo2.total_pendiente)
    print(prestamo2)

    print("\nCaso 3: Pago de todas las cuotas")
    prestamo3 = Prestamo(3, 300, 15)
    print(prestamo3)
    for _ in range(3):
        prestamo3.paga_cuota()
        print(prestamo3)

    print("\nCaso 4: Pago adicional con saldo ya liquidado")
    prestamo4 = Prestamo(2, 200, 5)
    print(prestamo4)
    prestamo4.paga_cuota()
    prestamo4.paga_cuota()
    prestamo4.paga_cuota()  # Extra
    print(prestamo4)
