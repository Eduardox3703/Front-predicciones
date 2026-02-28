import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import json
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# cargamos los datos desde la hoja de cálculo
print("cargando datos...")
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQfQk3w-DGkQ0KPncmhsJutMLIbvf0Aa1-qaLSNdPD_i_GOMqEcQUEuQUqrpftB8ysyoJAK9w9Mrrfy/pub?gid=2100603664&single=true&output=csv"
df = pd.read_csv(url)

# preparación de características (fechas, nuevos campos, encoders)
print("procesando características...")
df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
df['mes'] = df['Fecha'].dt.month
df['dia_semana'] = df['Fecha'].dt.dayofweek
df['dia_año'] = df['Fecha'].dt.dayofyear

# los artistas y lugares que estén vacíos se rellenan como desconocidos
df[['Artista', 'Lugar']] = df[['Artista', 'Lugar']].fillna('Desconocido')

# encoders que permiten manejar valores desconocidos usando -1
encoder_artista = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
encoder_lugar = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)

df['artista_encoded'] = encoder_artista.fit_transform(df[['Artista']])
df['lugar_encoded'] = encoder_lugar.fit_transform(df[['Lugar']])

# columnas principales que se van a usar en el modelo
columnas_modelo = [
    'Capacidad del Recinto (Confirmada/Estimada)', 'Asistencia (Confirmada/Estimada)',
    'Precio Mínimo Boleto (MXN)', 'Precio Máximo Boleto (MXN)', 
    'popularidad', 'seguidores', 'oyentes_mensuales', 
    'Seguidores Instagram', 'Seguidores facebook',
    'mes', 'dia_semana', 'dia_año',
    'artista_encoded', 'lugar_encoded'
]

# creamos un dataframe ordenado solo con esas columnas
df_clean = df.reindex(columns=columnas_modelo).copy()

# quitamos símbolos como $, puntos o comas para evitar errores
cols_precios = ['Precio Mínimo Boleto (MXN)', 'Precio Máximo Boleto (MXN)']
for col in cols_precios:
    df_clean[col] = df_clean[col].astype(str).str.replace(r'[$.]', '', regex=True)

cols_miles = ['Capacidad del Recinto (Confirmada/Estimada)', 'Asistencia (Confirmada/Estimada)', 'oyentes_mensuales']
for col in cols_miles:
    df_clean[col] = df_clean[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '', regex=False)

# convertimos toda la información a valores numéricos
for col in df_clean.columns:
    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

# agregamos el precio promedio, que normalmente ayuda mucho en la predicción
df_clean['precio_promedio'] = (df_clean['Precio Mínimo Boleto (MXN)'] + df_clean['Precio Máximo Boleto (MXN)']) / 2

# eliminamos filas sin datos de asistencia y rellenamos el resto con promedios
df_clean = df_clean.dropna(subset=['Asistencia (Confirmada/Estimada)'])
df_clean = df_clean.fillna(df_clean.mean())

# entrenamiento del modelo
print("entrenando modelo xgboost...")
y = df_clean['Asistencia (Confirmada/Estimada)']
X = df_clean.drop('Asistencia (Confirmada/Estimada)', axis=1)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# normalizamos los datos para que el modelo aprenda mejor
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model_xgb = xgb.XGBRegressor(
    n_estimators=500, learning_rate=0.05, max_depth=5,
    early_stopping_rounds=10, random_state=42, n_jobs=-1
)

model_xgb.fit(X_train_scaled, y_train, eval_set=[(X_test_scaled, y_test)], verbose=False)

# evaluación rápida del modelo ya entrenado
preds = model_xgb.predict(X_test_scaled)
print(f"r2 score: {r2_score(y_test, preds):.4f}")
print(f"mae: {mean_absolute_error(y_test, preds):.2f} personas")

# guardamos todo lo necesario para que la app pueda funcionar
print("guardando archivos del sistema...")
joblib.dump(model_xgb, 'modelo_asistencia.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(encoder_artista, 'encoder_artista.pkl')
joblib.dump(encoder_lugar, 'encoder_lugar.pkl')

# también guardamos el orden correcto de las columnas
with open('feature_names.json', 'w') as f:
    json.dump(X.columns.tolist(), f)

print("todo listo. los archivos fueron creados exitosamente.")
