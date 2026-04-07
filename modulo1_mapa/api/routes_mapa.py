from fastapi import APIRouter, Query
from modulo1_mapa.api.queries_mapa import (
    get_programas,
    get_departamentos,
    get_resumen_por_dpto,
)

router = APIRouter()


@router.get("/programas")
def listar_programas(
    dpto: str = Query(None, description="Filtrar por departamento. Ej: PUNO"),
    area: str = Query(None, description="Filtrar por área: Rural o Urbana"),
    ciclo: str = Query(None, description="Filtrar por ciclo: Ciclo I o Ciclo II"),
):
    """
    Retorna lista de programas PRONOEI con filtros opcionales.
    Máximo 2000 registros por consulta.
    """
    data = get_programas(dpto=dpto, area=area, ciclo=ciclo)
    return {"total": len(data), "programas": data}


@router.get("/departamentos")
def listar_departamentos():
    """Retorna lista de los 25 departamentos para el selector del mapa."""
    data = get_departamentos()
    return {"departamentos": data}


@router.get("/resumen")
def resumen_por_departamento():
    """
    Resumen de programas por departamento con totales
    de zona rural y urbana. Útil para el mapa de calor.
    """
    data = get_resumen_por_dpto()
    return {"resumen": data}