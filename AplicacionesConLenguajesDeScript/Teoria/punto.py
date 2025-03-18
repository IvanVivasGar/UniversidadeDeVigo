class Punto:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self.x
    ...

    @property
    def y(self):
        return self.y
    ...

    def distancia_a(p: "Punto"):
        x = self.x - p.x
        y = self.y - p.y