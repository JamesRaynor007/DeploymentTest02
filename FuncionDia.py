from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import pandas as pd
import os

# Definir la ruta del archivo CSV
file_path = os.path.join(os.path.dirname(__file__), 'PeliculasPorDiaListo.csv')

# Cargar el dataset
try:
    df = pd.read_csv(file_path)
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error al cargar el archivo: {str(e)}")

# Verificar que las columnas necesarias están en el DataFrame
if 'title' not in df.columns or 'day_of_week' not in df.columns:
    raise HTTPException(status_code=500, detail="El DataFrame no contiene las columnas esperadas.")

# Crear un diccionario para mapear dias en español
dias_map = {
    'lunes': 'Monday',
    'martes': 'Tuesday',
    'miercoles': 'Wednesday',
    'jueves': 'Thursday',
    'viernes': 'Friday',
    'sabado': 'Saturday',
    'domingo': 'Sunday',
}

app = FastAPI()

@app.get("/", response_model=dict)
def read_root(request: Request):
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    return {
        "message": "Bienvenido a la API de películas.",
        "instructions": "Usa el endpoint /peliculas/?dia=nombre_del_dia para obtener datos.",
        "links": [{"dia": dia, "url": f"{base_url}/peliculas/?dia={dia}"} for dia in dias_map.keys()]
    }

@app.get("/peliculas/")
def get_peliculas(dia: str):
    # Convertir el dia a minúsculas para evitar problemas de mayúsculas
    dia = dia.lower()

    # Verificar si el dia está en el diccionario
    if dia not in dias_map:
        raise HTTPException(status_code=400, detail="Día no válido. Por favor ingrese un día en español.")

    # Filtrar el DataFrame para contar películas estrenadas ese día
    cantidad = df[df['day_of_week'].str.lower() == dia].shape[0]  # Contar las filas donde el día coincide

    return {
        "dia": dia,
        "cantidad de películas que fueron estrenadas": cantidad
    }

# Endpoint para obtener la cantidad de películas por cada día de la semana
@app.get("/peliculas/cantidad_por_dia")
def get_cantidad_por_dia():
    resultados = {}
    for dia in dias_map.keys():
        cantidad = df[df['day_of_week'].str.lower() == dia].shape[0]
        resultados[dia] = cantidad
    return resultados