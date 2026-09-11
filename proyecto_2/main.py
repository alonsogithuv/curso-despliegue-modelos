
from contextlib import asynccontextmanager
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from inferencia import pronosticar
from esquema import SolicitudPronostico

NOMBRE_BUNDLE= "modelo_demanda.joblib"

estado_servicio = {"bundle":None}

@asynccontextmanager
async def lifespan (app:FastAPI):

    estado_servicio["bundle"] = joblib.load(NOMBRE_BUNDLE)
    print("Bundle cargado correctamente")
    yield
    estado_servicio["bundle"]= None

app = FastAPI(
    title = "API - Servicio de Pronóstico de Demanda",
    description = "Pronóstico de demanda por un Forecast",
    version = "1.0.0",
    lifespan = lifespan
    )

@app.get("/")
def estado ():
    return {

        "servicio":"API - Servicio de Predicción de demanda",

        "modelo_cargado": estado_servicio["bundle"] is not None
    }


@app.post ("/predecir")
def predecir (datos:SolicitudPronostico): 
    store= datos.store
    item= datos.item
    horizonte= datos.horizonte
    registros= datos.historial

    historial = pd.DataFrame (
        {
            "date":pd.to_datetime ([r.fecha for r in registros]),
            "store": store,
            "item": item,
            "sales": [r.unidades for r in registros]
        }
    )

    bundle = estado_servicio["bundle"]

    pronostico = pronosticar(bundle,historial,horizonte)

    return {
        "store": store,
        "item": item,
        "pronostico": pronostico
    }