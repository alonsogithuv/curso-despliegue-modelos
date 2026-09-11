"""Contratos de datos (Pydantic) para la API de cancelación de clientes.

Define el esquema de entrada que espera POST /predecir y el esquema de
salida que devuelve, en base a las columnas y la lógica de negocio
definidas en `entrenar_modelo.ipynb` (COLUMNAS_NUMERICAS + COLUMNAS_CATEGORICAS).
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Valores válidos, tal como aparecen en clientes.csv y en el pipeline entrenado.
PlanCliente = Literal["basico", "estandar", "premium"]
MetodoPago = Literal["tarjeta", "transferencia", "efectivo"]


class Cliente(BaseModel):
    """Datos de un cliente, con el mismo esquema que `COLUMNAS` en el notebook.

    Los 8 campos corresponden uno a uno con `COLUMNAS_NUMERICAS` +
    `COLUMNAS_CATEGORICAS`. El pipeline entrenado selecciona columnas por
    nombre, así que estos nombres tienen que coincidir exactamente.
    """

    antiguedad_meses: int = Field(..., ge=0, description="Meses que lleva como cliente")
    gasto_mensual: float = Field(..., ge=0, description="Cuánto paga por mes")
    visitas_ultimo_mes: int = Field(..., ge=0, description="Veces que usó el servicio en el último mes")
    dias_desde_ultima_visita: int = Field(..., ge=0, description="Días desde la última vez que usó el servicio")
    tickets_soporte: int = Field(..., ge=0, description="Reclamos de soporte abiertos en el último mes")
    descuento_activo: int = Field(..., ge=0, le=1, description="1 si hoy tiene un descuento aplicado, 0 si no")
    plan: PlanCliente = Field(..., description="Plan contratado")
    metodo_pago: MetodoPago = Field(..., description="Método de pago habitual")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "antiguedad_meses": 10,
                    "gasto_mensual": 14.0,
                    "visitas_ultimo_mes": 4,
                    "dias_desde_ultima_visita": 26,
                    "tickets_soporte": 1,
                    "descuento_activo": 0,
                    "plan": "basico",
                    "metodo_pago": "efectivo",
                }
            ]
        }
    )


class RespuestaPrediccion(BaseModel):
    """Contrato de salida de POST /predecir."""

    probabilidad: float = Field(..., ge=0, le=1, description="Probabilidad estimada de cancelación")
    prediccion: Literal["cancela", "sigue"] = Field(..., description="Predicción según el umbral de negocio")
    nivel_riesgo: Literal["Bajo", "Medio", "Alto"] = Field(..., description="Categoría de riesgo de negocio")
    umbral_usado: float = Field(..., description="Umbral de decisión aplicado")
