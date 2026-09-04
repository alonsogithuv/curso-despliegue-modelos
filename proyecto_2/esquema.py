
from pydantic import BaseModel, Field
from datetime import date 

class RegistroHistorico(BaseModel):
    fecha: date = Field(..., description="Fecha del registro histórico")
    unidades: float = Field(ge=0, description="Unidades vendidas ese dia, no puede ser negativo")

class SolicitudPronostico(BaseModel):
    store: int = Field(ge=1,le=10, description="El número de tiendas del 1 al 10")
    item: int = Field(ge=1,le=50, description="El número de producto del 1 al 50")
    horizonte: int = Field(default=14, ge=1,le=28, description="Número de períodos a pronosticar")
    historial: list[RegistroHistorico] = Field(min_length=28,max_length=365, 
                                               description="Histórico reciente de la serie, minimo 28 registros")