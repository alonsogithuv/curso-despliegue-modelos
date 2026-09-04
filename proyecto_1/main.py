
from contextlib import asynccontextmanager
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

NOMBRE_BUNDLE= "modelo_bundle_e_cardiaca.pkl"

estado_servicio = {"bundle":None}

@asynccontextmanager
async def lifespan (app:FastAPI):

    estado_servicio["bundle"] = joblib.load(NOMBRE_BUNDLE)
    print("Bundle cargado correctamente")
    yield
    estado_servicio["bundle"]= None

app = FastAPI(
    title = "API de prediccion de enfermedad cardiaca",
    description = "Recibe datos clinicos de un paciente y predice riesgo de cardiopatia coronaria (chd)",
    version = "1.0.0",
    lifespan = lifespan
    )

class PacienteImput(BaseModel):
    sbp: int = Field (..., description="Presion arterial sistolica"),
    Tabaco: float = Field (..., description="Tabaco acumuado (kg)"),
    ldl: float = Field(...,description="Colesterol LDL"),
    Adiposidad: float = Field(...,description="Adiposidad"),
    Familia: Literal['Presente',

                     'Ausente'] = Field(

                         ...,description="Antecendentes familiares de enfermedad cardíaca"),
    Tipo: int = Field(...,description="Comportamiento tipo-A"),
    Obesidad: float = Field(...,description="Obesidad"),
    Alcohol:float = Field(...,description="Consumo actual de alcohol"),
    Edad: int = Field (..., description="Edad")

class PacienteOutput(BaseModel):
    chd_predicho: int
    probabilidad: float
    riesgo: str

@app.get ("/")
def estado ():
    return {
        "servcio": "API de prediccion de enfermedad cardiaca",
        "modelo_cargado": estado_servicio["bundle"] is not None
    }

#Predecir
@app.post("/predecir", response_model=PacienteOutput)
def predecir (paciente: PacienteImput):

    #validar modelo
    bundle = estado_servicio["bundle"]

    if bundle is None:
        raise HTTPException (status_code= 503, detail= "El modelos aun no esta cargado")

    fila = paciente.model_dump()

    fila["Familia"] = bundle ["mapeo_familia"][fila["Familia"]]
    
    X_nuevo = pd.DataFrame([fila])[bundle["columnas"]]
    
    prediccion = bundle["pipeline"].predict(X_nuevo)[0]
    probabilidad = bundle["pipeline"].predict_proba(X_nuevo)[0,1]

    "Devolver resultados"
    return PacienteOutput (
        chd_predicho= prediccion,
        probabilidad= round(probabilidad,4),
        riesgo= "Alto" if prediccion == 1 else "Bajo"
    )

