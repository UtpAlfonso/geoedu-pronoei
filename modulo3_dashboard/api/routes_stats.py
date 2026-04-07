from fastapi import APIRouter
from modulo3_dashboard.api.queries_stats import (
    get_stats_por_region,
    get_stats_por_ciclo,
    get_stats_por_gestion,
    get_stats_por_turno,
    get_resumen_general,
)

router = APIRouter()


@router.get("/resumen")
def resumen_general():
    """Números globales: total programas, departamentos, distritos, rural/urbana."""
    return get_resumen_general()


@router.get("/por-region")
def stats_por_region():
    """Programas agrupados por región DRE/GRE con desglose rural/urbana."""
    data = get_stats_por_region()
    return {"total": len(data), "data": data}


@router.get("/por-ciclo")
def stats_por_ciclo():
    """Distribución por tipo de programa y ciclo de atención."""
    data = get_stats_por_ciclo()
    return {"total": len(data), "data": data}


@router.get("/por-gestion")
def stats_por_gestion():
    """Distribución por tipo de gestión (pública directa, privada, etc.)."""
    data = get_stats_por_gestion()
    return {"total": len(data), "data": data}


@router.get("/por-turno")
def stats_por_turno():
    """Distribución por turno de atención."""
    data = get_stats_por_turno()
    return {"total": len(data), "data": data}