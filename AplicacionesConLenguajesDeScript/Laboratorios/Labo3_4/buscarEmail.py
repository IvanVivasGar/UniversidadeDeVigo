def obtener_email(contactos, nombre):
    return contactos.get(nombre, None)

def introducir_contacto(contactos):
    nombre = input("Introduce el nombre: ")
    email = input("Introduce el e.mail: ")
    contactos[nombre] = email
    print("Contacto guardado.\n")

def borrar_contacto(contactos):
    nombre = input("Introduce el nombre a borrar: ")
    if nombre in contactos:
        del contactos[nombre]
        print("Contacto eliminado.\n")
    else:
        print("No se encontró el contacto.\n")

def buscar_contacto(contactos):
    nombre = input("Introduce el nombre a buscar: ")
    email = obtener_email(contactos, nombre)
    if email:
        print(f"E-mail de {nombre}: {email}\n")
    else:
        print("Contacto no encontrado.\n")

def listar_contactos(contactos):
    if contactos:
        print("Lista de contactos:")
        for nombre, email in contactos.items():
            print(f"{nombre}: {email}")
        print()
    else:
        print("No hay contactos guardados.\n")

def menu():
    contactos = {}
    while True:
        print("Menú principal:")
        print("1. Introducir contacto")
        print("2. Borrar contacto")
        print("3. Buscar contacto")
        print("4. Listar contactos")
        print("5. Salir")
        opcion = input("Elige una opción: ")

        if opcion == "1":
            introducir_contacto(contactos)
        elif opcion == "2":
            borrar_contacto(contactos)
        elif opcion == "3":
            buscar_contacto(contactos)
        elif opcion == "4":
            listar_contactos(contactos)
        elif opcion == "5":
            print("Saliendo del programa.")
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.\n")

if __name__ == "__main__":
    menu()