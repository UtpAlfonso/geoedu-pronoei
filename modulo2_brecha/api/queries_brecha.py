import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.db import get_connection


def get_ranking_brecha(top: int = 50):
    """
    Calcula el índice de brecha por distrito.
    Score = distritos con pocos programas + alta proporción rural + registros antiguos.
    Ordena de mayor a menor brecha (más críticos primero).
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    D_DPTO,
                    D_PROV,
                    D_DIST,
                    COUNT(*)                                         AS total_programas,
                    SUM(CASE WHEN DAREACENSO = 'Rural' THEN 1 ELSE 0 END) AS programas_rural,
                    SUM(CASE WHEN DAREACENSO = 'Urbana' THEN 1 ELSE 0 END) AS programas_urbana,
                    ROUND(
                        SUM(CASE WHEN DAREACENSO = 'Rural' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1
                    )                                                AS pct_rural,
                    MIN(FECHA_ACT)                                   AS actualizacion_mas_antigua,
                    MAX(FECHA_ACT)                                   AS actualizacion_mas_reciente
                FROM pronoei_programas
                GROUP BY D_DPTO, D_PROV, D_DIST
                ORDER BY total_programas ASC, pct_rural DESC
                LIMIT %s
            """, (top,))
            return cursor.fetchall()
    finally:
        conn.close()


def get_detalle_distrito(distrito: str, provincia: str = None):
    """Retorna todos los programas de un distrito específico."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT
                    COD_MOD, CEN_EDU, D_TIPOPROG,
                    DAREACENSO, D_COD_TUR,
                    D_DPTO, D_PROV, D_DIST,
                    FECHAREG, FECHA_ACT
                FROM pronoei_programas
                WHERE D_DIST = %s
            """
            params = [distrito.upper()]
            if provincia:
                sql += " AND D_PROV = %s"
                params.append(provincia.upper())
            sql += " ORDER BY CEN_EDU"
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()


def get_resumen_brecha_por_dpto():
    """
    Promedio de programas por distrito agrupado por departamento.
    Útil para ver qué departamentos tienen distritos con menor cobertura.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    D_DPTO,
                    COUNT(DISTINCT D_DIST)          AS total_distritos,
                    COUNT(*)                         AS total_programas,
                    ROUND(COUNT(*) / COUNT(DISTINCT D_DIST), 1) AS promedio_por_distrito,
                    SUM(CASE WHEN DAREACENSO = 'Rural' THEN 1 ELSE 0 END) AS total_rural
                FROM pronoei_programas
                GROUP BY D_DPTO
                ORDER BY promedio_por_distrito ASC
            """)
            return cursor.fetchall()
    finally:
        conn.close()