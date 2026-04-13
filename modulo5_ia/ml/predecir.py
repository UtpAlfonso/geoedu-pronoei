import os
import joblib
import numpy as np
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.db import get_connection

MODELO_PATH   = os.path.join(os.path.dirname(__file__), "modelo_rf.pkl")
ENCODERS_PATH = os.path.join(os.path.dirname(__file__), "encoders.pkl")

def modelo_existe():
    return os.path.exists(MODELO_PATH) and os.path.exists(ENCODERS_PATH)

def cargar_modelo():
    modelo   = joblib.load(MODELO_PATH)
    encoders = joblib.load(ENCODERS_PATH)
    return modelo, encoders

def predecir_distritos(top: int = 20):
    """
    Predice los distritos con mayor riesgo de baja cobertura.
    Retorna el top N ordenados por probabilidad de riesgo descendente.
    """
    if not modelo_existe():
        return {"error": "Modelo no entrenado. Ejecuta /api/ia/entrenar primero."}

    modelo, encoders = cargar_modelo()

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    D_DPTO,
                    D_PROV,
                    D_DIST,
                    DAREACENSO,
                    COUNT(*)                                                AS total_programas,
                    SUM(CASE WHEN DAREACENSO = 'Rural' THEN 1 ELSE 0 END) AS programas_rural,
                    ROUND(
                        SUM(CASE WHEN DAREACENSO = 'Rural' THEN 1 ELSE 0 END)
                        * 100.0 / COUNT(*), 1
                    )                                                       AS pct_rural,
                    COUNT(DISTINCT D_TIPOPROG)                              AS variedad_programas
                FROM pronoei_programas
                GROUP BY D_DPTO, D_PROV, D_DIST, DAREACENSO
                ORDER BY total_programas ASC
            """)
            rows = cursor.fetchall()
    finally:
        conn.close()

    resultados = []
    for row in rows:
        try:
            dpto_enc = encoders["D_DPTO"].transform([row["D_DPTO"]])[0]
            area_enc = encoders["DAREACENSO"].transform([row["DAREACENSO"]])[0]
        except Exception:
            continue

        features = np.array([[
            row["total_programas"],
            row["programas_rural"],
            row["pct_rural"] or 0,
            row["variedad_programas"],
            dpto_enc,
            area_enc,
        ]])

        prob_riesgo = modelo.predict_proba(features)[0][1]

        resultados.append({
            "D_DPTO":           row["D_DPTO"],
            "D_PROV":           row["D_PROV"],
            "D_DIST":           row["D_DIST"],
            "DAREACENSO":       row["DAREACENSO"],
            "total_programas":  row["total_programas"],
            "pct_rural":        row["pct_rural"],
            "prob_riesgo":      round(float(prob_riesgo) * 100, 1),
            "nivel_riesgo":     clasificar_riesgo(prob_riesgo),
        })

    resultados.sort(key=lambda x: x["prob_riesgo"], reverse=True)
    return resultados[:top]

def clasificar_riesgo(prob: float) -> str:
    if prob >= 0.75:
        return "Crítico"
    elif prob >= 0.50:
        return "Alto"
    elif prob >= 0.25:
        return "Medio"
    else:
        return "Bajo"

def get_importancia_features():
    """Retorna la importancia de cada variable del modelo."""
    if not modelo_existe():
        return {"error": "Modelo no entrenado."}

    modelo, _ = cargar_modelo()
    nombres = [
        "Total programas",
        "Programas rurales",
        "% Rural",
        "Variedad de programas",
        "Departamento",
        "Área",
    ]
    importancias = modelo.feature_importances_
    return [
        {"feature": n, "importancia": round(float(i) * 100, 1)}
        for n, i in sorted(
            zip(nombres, importancias),
            key=lambda x: x[1],
            reverse=True
        )
    ]