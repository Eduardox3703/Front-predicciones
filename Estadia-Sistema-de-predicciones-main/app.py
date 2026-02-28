import streamlit as st
import joblib
import pandas as pd
import numpy as np
import json
import datetime

# configuración básica de la página
st.set_page_config(page_title="Predicción de Conciertos", page_icon="🎤")

# cargamos el modelo y los archivos necesarios
try:
    model = joblib.load('modelo_asistencia.pkl')
    scaler = joblib.load('scaler.pkl')
    encoder_artista = joblib.load('encoder_artista.pkl')
    encoder_lugar = joblib.load('encoder_lugar.pkl')
    with open('feature_names.json', 'r') as f:
        feature_names = json.load(f)
except FileNotFoundError:
    st.error("⚠️ error: faltan archivos. primero ejecuta 'entrenar_modelo.py'.")
    st.stop()

# obtener las listas que se usarán en los menús
try:
    lista_artistas = list(encoder_artista.categories_[0])
    lista_lugares = list(encoder_lugar.categories_[0])
except:
    st.error("error al leer los encoders.")
    st.stop()

# opciones especiales para casos en que el artista o recinto no existan aún
opcion_artista_nuevo = "[Artista Nuevo/Desconocido]"
opcion_lugar_nuevo = "[Recinto Nuevo/Desconocido]"
opciones_artistas_final = [opcion_artista_nuevo] + lista_artistas
opciones_lugares_final = [opcion_lugar_nuevo] + lista_lugares

# interfaz principal
st.title('🔮 Predicción de Asistencia a Eventos')
st.markdown("Ingresa los detalles del evento para estimar el éxito.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎤 Detalles del Artista")
    artista_input = st.selectbox("Nombre del Artista", options=opciones_artistas_final)
    popularidad = st.slider("Popularidad (0-100)", 0, 100, 50)
    seguidores = st.number_input("Seguidores", min_value=0, value=1000000)
    oyentes = st.number_input("Oyentes Mensuales", min_value=0, value=5000000)

with col2:
    st.subheader("🏟️ Detalles del Evento")
    lugar_input = st.selectbox("Nombre del Recinto", options=opciones_lugares_final)
    capacidad = st.number_input("Capacidad del Recinto", min_value=100, value=5000)
    fecha = st.date_input("Fecha del Evento", datetime.date.today())

st.subheader("🎟️ Boletos y Redes")
c1, c2, c3 = st.columns(3)
with c1:
    p_min = st.number_input("Precio Mínimo (MXN)", value=500)
with c2:
    p_max = st.number_input("Precio Máximo (MXN)", value=1500)
with c3:
    ig = st.number_input("Seguidores Instagram", value=100000)
    fb = st.number_input("Seguidores Facebook", value=100000)

# lógica para hacer la predicción
if st.button('¡Estimar Asistencia!', type="primary"):
    
    # identificamos si el artista o el lugar son nuevos
    if artista_input == opcion_artista_nuevo:
        id_artista = -1
    else:
        id_artista = encoder_artista.transform([[artista_input]])[0][0]

    if lugar_input == opcion_lugar_nuevo:
        id_lugar = -1
    else:
        id_lugar = encoder_lugar.transform([[lugar_input]])[0][0]

    # calculamos valores adicionales que ayudan a la predicción
    precio_prom = (p_min + p_max) / 2
    mes = fecha.month
    dia_sem = fecha.weekday()
    dia_anio = fecha.timetuple().tm_yday

    # armamos el dataframe respetando el orden original de las columnas
    data = {
        'Capacidad del Recinto (Confirmada/Estimada)': capacidad,
        'Precio Mínimo Boleto (MXN)': p_min,
        'Precio Máximo Boleto (MXN)': p_max,
        'popularidad': popularidad,
        'seguidores': seguidores,
        'oyentes_mensuales': oyentes,
        'Seguidores Instagram': ig,
        'Seguidores facebook': fb,
        'mes': mes,
        'dia_semana': dia_sem,
        'dia_año': dia_anio,
        'artista_encoded': id_artista,
        'lugar_encoded': id_lugar,
        'precio_promedio': precio_prom
    }
    
    df_input = pd.DataFrame([data])
    df_input = df_input[feature_names]

    # escalamos los datos y ejecutamos el modelo
    X_scaled = scaler.transform(df_input)
    prediccion = model.predict(X_scaled)[0]
    resultado = int(max(0, prediccion))

    # mostramos la predicción final
    st.success(f"## 📈 Asistencia Estimada: {resultado:,} personas")
    
    # análisis de ocupación sin usar globos
    ocupacion = (resultado / capacidad) * 100
    if ocupacion > 95:
        st.warning(f"posible sold out ({ocupacion:.1f}% de ocupación)")
    elif ocupacion < 50:
        st.info(f"ocupación baja estimada ({ocupacion:.1f}%). quizá valga la pena revisar precios o promoción.")
    else:
        st.write(f"ocupación estimada: **{ocupacion:.1f}%**")
