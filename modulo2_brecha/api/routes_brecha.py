from fastapi import APIRouter, Query
from modulo2_brecha.api.queries_brecha import (
    get_ranking_brecha,
    get_detalle_distrito,
    get_resumen_brecha_por_dpto,
)

router = APIRouter()


@router.get("/ranking")
def ranking_brecha(
    top: int = Query(50, ge=1, le=200, description="Cantidad de distritos a mostrar"),
):
    """
    Ranking de distritos con mayor brecha de cobertura.
    Ordenados de menor a mayor cantidad de programas (más críticos primero).
    """
    data = get_ranking_brecha(top=top)
    return {"total": len(data), "ranking": data}


@router.get("/distrito")
def detalle_distrito(
    distrito: str = Query(..., description="Nombre del distrito. Ej: HUANCANE"),
    provincia: str = Query(None, description="Nombre de la provincia (opcional)"),
):
    """Retorna todos los programas de un distrito específico."""
    data = get_detalle_distrito(distrito=distrito, provincia=provincia)
    return {"distrito": distrito, "total": len(data), "programas": data}


@router.get("/resumen-departamentos")
def resumen_por_departamento():
    """
    Resumen de cobertura por departamento:
    total de distritos, programas y promedio por distrito.
    """
    data = get_resumen_brecha_por_dpto()
    return {"resumen": data}