
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from config.db import get_connection

# Ruta donde se guarda el modelo entrenado
MODELO_PATH = os.path.join(os.path.dirname(__file__), "modelo_rf.pkl")
ENCODERS_PATH = os.path.join(os.path.dirname(__file__), "encoders.pkl")

def cargar_datos():
    """Carga y prepara los datos desde TiDB Cloud."""
    conn = get_connection()
    try:
        query = """
            SELECT
                D_DPTO,
                D_PROV,
                D_DIST,
                DAREACENSO,
                D_TIPOPROG,
                COUNT(*)                                                          AS total_programas,
                SUM(CASE WHEN DAREACENSO = 'Rural' THEN 1 ELSE 0 END)            AS programas_rural,
                ROUND(
                    SUM(CASE WHEN DAREACENSO = 'Rural' THEN 1 ELSE 0 END) * 100.0
                    / COUNT(*), 1
                )                                                                 AS pct_rural,
                COUNT(DISTINCT D_TIPOPROG)                                        AS variedad_programas
            FROM pronoei_programas
            GROUP BY D_DPTO, D_PROV, D_DIST, DAREACENSO, D_TIPOPROG
        """
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()

def preparar_features(df):
    """Prepara las variables para el modelo."""
    encoders = {}

    # Codificar variables categóricas
    for col in ["D_DPTO", "DAREACENSO"]:
        le = LabelEncoder()
        df[col + "_enc"] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

    # Variable objetivo: riesgo de baja cobertura
    # 1 = en riesgo (pocos programas y alta ruralidad)
    # 0 = cobertura aceptable
    df["en_riesgo"] = (
        (df["total_programas"] <= 2) &
        (df["pct_rural"] >= 60)
    ).astype(int)

    features = [
        "total_programas",
        "programas_rural",
        "pct_rural",
        "variedad_programas",
        "D_DPTO_enc",
        "DAREACENSO_enc",
    ]

    X = df[features]
    y = df["en_riesgo"]

    return X, y, encoders, df

def entrenar():
    """Entrena el modelo y lo guarda en disco."""
    print("Cargando datos desde TiDB Cloud...")
    df = cargar_datos()
    print(f"Registros cargados: {len(df)}")

    X, y, encoders, df_completo = preparar_features(df)

    print(f"Distribución: en riesgo={y.sum()} / total={len(y)}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    modelo = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight="balanced",
    )
    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)
    print("\n=== Reporte de clasificación ===")
    print(classification_report(y_test, y_pred))

    # Guardar modelo y encoders
    joblib.dump(modelo, MODELO_PATH)
    joblib.dump(encoders, ENCODERS_PATH)
    print(f"\nModelo guardado en: {MODELO_PATH}")

    return modelo, encoders

if __name__ == "__main__":
    entrenar()