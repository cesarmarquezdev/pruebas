lista = {"notas": [{"titulo": "hola", "nota": "buenas tardes "}]}
print(lista["notas"])
print(lista["notas"][0]["titulo"])
lista["notas"][0]["title"] = lista["notas"][0].pop("titulo")
print(lista["notas"][0])
