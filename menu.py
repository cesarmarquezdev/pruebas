from db import cargar_db, guardar_db

# 1. Cargar la base de datos
db = cargar_db()

guardar_db(db)
print("¡Base de datos actualizada usando pathlib!")

"""Primer paso para hacer nuestro """


def menu() -> str:
    """Funcion que devuelve un string con la opciones"""
    menu_str = """
1 - Crear una nota nueva.
2 - Listar las notas recibidas.
3 - eliminar una nota.
4 - salir del Menu"""
    return menu_str


def opcion_correcta(numero: int):

    if numero < 1 or numero > 4:
        print("La opcion tiene que estar entre 1,2,3 o 4.")
        return False
    opciones = [1, 2, 3, 4]
    if numero in opciones:
        return True
    else:
        return False


def crear_nota(titulo: str, nota: str) -> dict[str, str]:
    return {"titulo": titulo, "nota": nota}


while True:
    print(menu())
    try:
        numero = int(input("Seleccione un una opcion: "))
    except ValueError:
        print("Introduzca una opcion Valida")
        continue
    if opcion_correcta(numero):
        if numero == 1:
            print("Opcion elegida: 1- Crear una nota: ")
            titulo = input("Ingrese el titulo de la nota: ")
            nota = input("Ingrese el cuero de la nota: ")
            db["notas"].append(crear_nota(titulo, nota))
        if numero == 2:
            print("Opcion elegida 2 _ Listar las notas: ")
            for i in db["notas"]:
                print(i)
        if numero == 3:
            print("Opcion elegida: 3- eliminar una nota: ")
            titulo = input("Introduzca el titulo de la nota que desea eliminar: ")
            total_antes = len(db["notas"])
            db["notas"] = [u for u in db["notas"] if u["titulo"] != titulo]
            if len(db["notas"]) < total_antes:
                print(f"¡Usuario con ID {titulo} borrado con éxito!")
            else:
                print(f"No se encontró ningún usuario con el ID {titulo}.")
        if numero == 4:
            break


guardar_db(db)
print("¡Base de datos actualizada usando pathlib!")
