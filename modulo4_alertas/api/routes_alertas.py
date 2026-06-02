from fastapi import APIRouter, Query
from modulo4_alertas.api.queries_alertas import (
    get_programas_inactivos,
    get_resumen_alertas,
    get_conteo_alertas,
)

router = APIRouter()


@router.get("/inactivos")
def listar_inactivos(meses: int = Query(6, ge=1, le=36)):
    try:
        data = get_programas_inactivos(meses=meses)

        return {
            "meses_umbral": meses,
            "total": len(data),
            "programas": data
        }

    except Exception as e:
        import traceback

        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }
    """
    Lista programas que no han sido actualizados en más de N meses.
    Máximo 500 resultados, ordenados por más antiguos primero.
    """
    data = get_programas_inactivos(meses=meses)
    return {"meses_umbral": meses, "total": len(data), "programas": data}


@router.get("/resumen")
def resumen_alertas():
    """
    Resumen de programas inactivos (+6 meses) agrupado por
    departamento y UGEL/DRE.
    """
    data = get_resumen_alertas()
    return {"total_ugeles": len(data), "data": data}


@router.get("/conteo")
def conteo_alertas():
    """Número total de programas inactivos (más de 6 meses sin actualizar)."""
    return get_conteo_alertas()