# Mensaje

class Mensaje:
    def __init__(self, nombre, mensaje):
        self.__nombre = nombre
        self.__mensaje = mensaje
    ...

    @property
    def nombre(self):
        return self.__nombre
    ...

    @property
    def mensaje(self):
        return self.__mensaje
    ...

    def __str__(self):
        return f"{self.nombre}: {self.mensaje}"