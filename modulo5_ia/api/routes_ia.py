from fastapi import APIRouter, Query, BackgroundTasks
from modulo5_ia.ml.predecir import predecir_distritos, get_importancia_features, modelo_existe

router = APIRouter()

@router.get("/estado")
def estado_modelo():
    return {
        "modelo_entrenado": modelo_existe(),
        "mensaje": "Listo para predecir" if modelo_existe() else "Sube el modelo .pkl a GitHub"
    }

@router.post("/entrenar")
def entrenar_modelo(background_tasks: BackgroundTasks):
    def _entrenar():
        from modulo5_ia.ml.entrenar import entrenar
        entrenar()
    background_tasks.add_task(_entrenar)
    return {
        "mensaje": "Entrenamiento iniciado en segundo plano.",
        "instruccion": "Espera 30 segundos y llama a /api/ia/prediccion"
    }

@router.get("/prediccion")
def prediccion_riesgo(
    top: int = Query(20, ge=5, le=100)
):
    if not modelo_existe():
        return {"error": "Modelo no entrenado. Llama a POST /api/ia/entrenar primero."}
    data = predecir_distritos(top=top)
    return {
        "total": len(data),
        "descripcion": "Distritos ordenados por probabilidad de riesgo",
        "predicciones": data
    }

@router.get("/importancia-features")
def importancia_features():
    return {"importancia": get_importancia_features()}