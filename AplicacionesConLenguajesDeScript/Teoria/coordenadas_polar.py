# Coordenadas que soportan una distancia y un angulo
# @(5.0, 45.0)

class CoordenadaPolar:
    def __init__(self, dst: float, ang: float):
        self._dst = dst
        self._ang = ang

    def dst(self):
        return self._dst

    def ang(self):
        return self._ang

    def __str__(self):
        return f"({self._dst}, {self._ang})"