"""API REST para predecir la cancelación (churn) de clientes.

Carga el bundle generado en `entrenar_modelo.ipynb` (modelo entrenado +
metadatos) una sola vez al arrancar el servidor, y lo expone a través de
dos endpoints: GET / y POST /predecir.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException

from Tarea_1.esquemas import Cliente, RespuestaPrediccion

# Ruta absoluta relativa a este archivo: funciona sin importar desde qué
# directorio se lance `uvicorn`.
NOMBRE_BUNDLE =  "Tarea_1/modelo_churn.joblib"

# Se llena una sola vez en el lifespan y se lee en cada request.
# Evita releer el .joblib del disco (y recargar el modelo) en cada predicción.
estado: dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carga el bundle del modelo al arrancar el servidor (una sola vez).

    Si el archivo todavía no existe, falla rápido con un mensaje claro en
    vez de dejar que cada request explote más adelante con un KeyError.
    """
    try:
        estado["bundle"] = joblib.load(NOMBRE_BUNDLE)
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"No se encontró '{NOMBRE_BUNDLE.name}'. Corré la Parte 2 del "
            "notebook (guardado del bundle) antes de levantar la API."
        ) from exc
    yield
    estado.clear()


app = FastAPI(
    title="API de Predicción de Cancelación de Clientes",
    description=(
        "Recibe los datos de un cliente y estima la probabilidad de que "
        "cancele su suscripción, usando el modelo entrenado en el notebook entrenar_modelo."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


def calcular_nivel_riesgo(probabilidad: float) -> str:
    """Traduce una probabilidad a una categoría de riesgo de negocio.

    Bajo  : probabilidad < 0.4
    Medio : 0.4 <= probabilidad < 0.6
    Alto  : probabilidad >= 0.6

    Es independiente del `umbral` de decisión (0.5): el umbral define
    "cancela" vs "sigue"; el nivel de riesgo es una lectura más para
    priorizar a quién contactar primero, aunque caiga del lado "sigue".
    """
    if probabilidad < 0.4:
        return "Bajo"
    if probabilidad < 0.6:
        return "Medio"
    return "Alto"


@app.get("/")
async def raiz() -> dict[str, Any]:
    """Mensaje de bienvenida, estado del servicio y metadatos del bundle."""
    bundle = estado["bundle"]
    return {
        "mensaje": "API de predicción de cancelación de clientes",
        "estado": "activo",
        "fecha_entrenamiento": bundle.get("fecha_entrenamiento"),
        "versiones_entrenamiento": bundle.get("versiones"),
    }


@app.post("/predecir", response_model=RespuestaPrediccion)
async def predecir(cliente: Cliente) -> RespuestaPrediccion:
    """Predice si un cliente va a cancelar, a partir de sus datos."""
    bundle = estado["bundle"]
    modelo = bundle["modelo"]
    umbral = bundle["umbral"]

    entrada = pd.DataFrame([cliente.model_dump()])

    try:
        probabilidad = float(modelo.predict_proba(entrada)[0, 1])
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error al ejecutar el pipeline predictivo: {exc}",
        ) from exc

    prediccion = "cancela" if probabilidad >= umbral else "sigue"

    return RespuestaPrediccion(
        probabilidad=round(probabilidad, 4),
        prediccion=prediccion,
        nivel_riesgo=calcular_nivel_riesgo(probabilidad),
        umbral_usado=umbral,
    )
