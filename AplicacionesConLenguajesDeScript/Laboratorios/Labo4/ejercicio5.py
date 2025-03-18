class Contacto:
    def __init__(self, nombre, email):
        self.nombre = nombre
        self.email = email

    def __str__(self):
        return f"Nombre: {self.nombre}, Email: {self.email}"

class Amigo(Contacto):
    pass

class Trabajo(Contacto):
    def __init__(self, nombre, email, email_empresa):
        super().__init__(nombre, email)
        self.email_empresa = email_empresa

    def __str__(self):
        return f"Nombre: {self.nombre}, Email personal: {self.email}, Email empresa: {self.email_empresa}"

class GestorContactos:
    def __init__(self):
        self.contactos = {}

    def insertar(self, contacto):
        self.contactos[contacto.nombre] = contacto

    def borrar(self, nombre):
        if nombre in self.contactos:
            del self.contactos[nombre]
            print(f"Contacto '{nombre}' eliminado.")
        else:
            print("Contacto no encontrado.")

    def buscar(self, nombre):
        return self.contactos.get(nombre, "Contacto no encontrado.")

    def listar(self):
        for contacto in self.contactos.values():
            print(contacto)

# Menú de interacción
if __name__ == "__main__":
    gestor = GestorContactos()
    while True:
        print("\nMenú Principal")
        print("1. Insertar contacto")
        print("2. Borrar contacto")
        print("3. Buscar contacto")
        print("4. Listar contactos")
        print("5. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            tipo = input("Tipo (amigo/trabajo): ").strip().lower()
            nombre = input("Nombre: ")
            email = input("Email: ")
            if tipo == "trabajo":
                email_empresa = input("Email de empresa: ")
                contacto = Trabajo(nombre, email, email_empresa)
            else:
                contacto = Amigo(nombre, email)
            gestor.insertar(contacto)

        elif opcion == "2":
            nombre = input("Nombre a borrar: ")
            gestor.borrar(nombre)

        elif opcion == "3":
            nombre = input("Nombre a buscar: ")
            print(gestor.buscar(nombre))

        elif opcion == "4":
            gestor.listar()

        elif opcion == "5":
            break

        else:
            print("Opción no válida.")