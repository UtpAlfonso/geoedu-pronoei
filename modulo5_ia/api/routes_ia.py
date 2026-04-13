from fastapi import APIRouter, Query, BackgroundTasks
from modulo5_ia.ml.predecir import predecir_distritos, get_importancia_features, modelo_existe
from modulo5_ia.ml.entrenar import entrenar

router = APIRouter()

@router.get("/estado")
def estado_modelo():
    """Verifica si el modelo ya está entrenado."""
    return {
        "modelo_entrenado": modelo_existe(),
        "mensaje": "Listo para predecir" if modelo_existe() else "Ejecuta /api/ia/entrenar primero"
    }

@router.post("/entrenar")
def entrenar_modelo(background_tasks: BackgroundTasks):
    """
    Entrena el modelo Random Forest con los datos actuales de TiDB Cloud.
    Se ejecuta en segundo plano para no bloquear la API.
    """
    background_tasks.add_task(entrenar)
    return {
        "mensaje": "Entrenamiento iniciado en segundo plano.",
        "instruccion": "Espera 30 segundos y luego llama a /api/ia/prediccion"
    }

@router.get("/prediccion")
def prediccion_riesgo(
    top: int = Query(20, ge=5, le=100, description="Cantidad de distritos a retornar")
):
    """
    Retorna los distritos con mayor probabilidad de riesgo de baja cobertura
    según el modelo Random Forest entrenado.
    """
    if not modelo_existe():
        return {"error": "Modelo no entrenado. Llama a POST /api/ia/entrenar primero."}

    data = predecir_distritos(top=top)
    return {
        "total": len(data),
        "descripcion": "Distritos ordenados por probabilidad de riesgo de baja cobertura",
        "predicciones": data
    }

@router.get("/importancia-features")
def importancia_features():
    """
    Retorna qué variables son más importantes para el modelo
    al predecir el riesgo de baja cobertura.
    """
    return {"importancia": get_importancia_features()}