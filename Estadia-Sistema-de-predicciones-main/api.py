from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import datetime
import json

app = FastAPI(title="API de Predicción de Asistencia a Conciertos")

# ✅ CORS (permite conexión con frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1️⃣ Cargar modelos al iniciar
try:
    model = joblib.load('modelo_asistencia.pkl')
    scaler = joblib.load('scaler.pkl')
    encoder_artista = joblib.load('encoder_artista.pkl')
    encoder_lugar = joblib.load('encoder_lugar.pkl')

    with open('feature_names.json', 'r') as f:
        feature_names = json.load(f)

    print("✅ Modelos cargados correctamente")

except Exception as e:
    print(f"❌ Error al cargar los modelos: {e}")


# 2️⃣ Endpoint raíz (evita 404)
@app.get("/")
def root():
    return {"mensaje": "API de Predicción funcionando correctamente 🚀"}


# 3️⃣ Endpoint dinámico de artistas (ACTUALIZADO)
@app.get("/artistas")
def obtener_artistas():
    try:
        artistas = encoder_artista.categories_[0].tolist()
        artistas.sort()
        artistas.insert(0, "[Artista Nuevo/Desconocido]")
        return {"artistas": artistas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 4️⃣ Endpoint dinámico de recintos
@app.get("/recintos")
def obtener_recintos():
    recintos = list(encoder_lugar.categories_[0])
    recintos.insert(0, "[Recinto Nuevo/Desconocido]")
    return recintos


# 5️⃣ Modelo de entrada
class DatosConcierto(BaseModel):
    capacidad_recinto: int
    precio_minimo: float
    precio_maximo: float
    precio_promedio: float
    popularidad: float
    seguidores: int
    oyentes_mensuales: int
    seguidores_ig: int
    seguidores_fb: int
    fecha: str
    artista: str
    lugar: str


# 6️⃣ Endpoint principal
@app.post("/predecir")
def predecir_asistencia(datos: DatosConcierto):
    try:
        fecha_obj = datetime.datetime.strptime(datos.fecha, "%Y-%m-%d")
        mes = fecha_obj.month
        dia_sem = fecha_obj.weekday()
        dia_anio = fecha_obj.timetuple().tm_yday

        # Codificar artista
        if datos.artista not in encoder_artista.categories_[0]:
            id_artista = -1
        else:
            id_artista = encoder_artista.transform([[datos.artista]])[0][0]

        # Codificar recinto
        if datos.lugar not in encoder_lugar.categories_[0]:
            id_lugar = -1
        else:
            id_lugar = encoder_lugar.transform([[datos.lugar]])[0][0]

        data = {
            'Capacidad del Recinto (Confirmada/Estimada)': datos.capacidad_recinto,
            'Precio Mínimo Boleto (MXN)': datos.precio_minimo,
            'Precio Máximo Boleto (MXN)': datos.precio_maximo,
            'popularidad': datos.popularidad,
            'seguidores': datos.seguidores,
            'oyentes_mensuales': datos.oyentes_mensuales,
            'Seguidores Instagram': datos.seguidores_ig,
            'Seguidores facebook': datos.seguidores_fb,
            'mes': mes,
            'dia_semana': dia_sem,
            'dia_año': dia_anio,
            'artista_encoded': id_artista,
            'lugar_encoded': id_lugar,
            'precio_promedio': datos.precio_promedio
        }

        df_input = pd.DataFrame([data])
        df_input = df_input[feature_names]

        X_scaled = scaler.transform(df_input)
        prediccion = model.predict(X_scaled)[0]
        resultado = int(max(0, prediccion))

        return {
            "asistencia_estimada": resultado,
            "porcentaje_ocupacion": round((resultado / datos.capacidad_recinto) * 100, 2)
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))