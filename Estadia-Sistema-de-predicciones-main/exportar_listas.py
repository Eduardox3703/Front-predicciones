import joblib
import json

# 1. Cargar los encoders que ya tienes de tu modelo original
encoder_artista = joblib.load('encoder_artista.pkl')
encoder_lugar = joblib.load('encoder_lugar.pkl')

# 2. Extraer las listas de categorías limpias
lista_artistas = list(encoder_artista.categories_[0])
lista_lugares = list(encoder_lugar.categories_[0])

# 3. Guardarlas en archivos JSON (con codificación utf-8 para que no se rompan los acentos)
with open('artistas.json', 'w', encoding='utf-8') as f:
    json.dump(lista_artistas, f, ensure_ascii=False, indent=4)

with open('lugares.json', 'w', encoding='utf-8') as f:
    json.dump(lista_lugares, f, ensure_ascii=False, indent=4)

print("¡Archivos artistas.json y lugares.json generados con éxito!")