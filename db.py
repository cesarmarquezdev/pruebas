import json
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent
DB_FILE = DB_PATH / "notas.json"


def cargar_db():
    print("Cargar db ")
    """Cargamos la base de datos
    si no hay nada la crea return {"notas": []}.
    si hay, la carga como un diccionario return json.loads(contenido).
    """
    # Si el archivo no existe, devolvemos la estructura inicial
    if not DB_FILE.exists():
        return {"notas": []}

    # read_text() abre, lee y cierra el archivo automáticamente
    contenido = DB_FILE.read_text(encoding="utf-8")
    return json.loads(contenido)


def guardar_db(datos: dict):
    print("Guardar nota.")
    # Convertimos el diccionario a texto JSON string
    contenido_json = json.dumps(datos, indent=4, ensure_ascii=False)

    # write_text() crea o sobrescribe el archivo, y lo cierra automáticamente
    DB_FILE.write_text(contenido_json, encoding="utf-8")
