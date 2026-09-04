#Ingenieria de variables

LAGS = [1, 7, 14, 28]
VENTANAS = [7, 28]
MIN_HISTORIAL = max(LAGS + VENTANAS)   # 28 dias

COLUMNAS = (["store", "item", "dia_semana", "dia_mes", "mes", "semana_anio",
             "dia_anio", "es_fin_semana"]
            + [f"lag_{l}" for l in LAGS]
            + [f"media_{v}" for v in VENTANAS]
            + [f"std_{v}" for v in VENTANAS])


def crear_calendario(df):
    """Variables derivadas solo de la fecha. No requieren historia."""
    df = df.copy()
    df["dia_semana"]    = df.date.dt.dayofweek
    df["dia_mes"]       = df.date.dt.day
    df["mes"]           = df.date.dt.month
    df["semana_anio"]   = df.date.dt.isocalendar().week.astype(int)
    df["dia_anio"]      = df.date.dt.dayofyear
    df["es_fin_semana"] = (df.dia_semana >= 5).astype(int)
    return df


def crear_lags(df, grupo=["store", "item"]):
    """Rezagos y estadisticas moviles por serie. Siempre desplazados: nunca usan el dia actual."""
    df = df.sort_values(grupo + ["date"]).copy()
    g = df.groupby(grupo)["sales"]
    for lag in LAGS:
        df[f"lag_{lag}"] = g.shift(lag)
    for v in VENTANAS:
        df[f"media_{v}"] = g.transform(lambda s: s.shift(1).rolling(v).mean())
        df[f"std_{v}"]   = g.transform(lambda s: s.shift(1).rolling(v).std())
    return df


def crear_features(df, grupo=["store", "item"]):
    """Punto de entrada unico. Se usa igual en entrenamiento y en inferencia."""
    return crear_lags(crear_calendario(df), grupo)