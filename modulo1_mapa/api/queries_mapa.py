import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.db import get_connection


def get_programas(dpto: str = None, area: str = None, ciclo: str = None):
    """Retorna programas con filtros opcionales para el mapa."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT
                    COD_MOD, CEN_EDU, D_FORMA,
                    D_TIPOPROG, D_COD_TUR,
                    D_DPTO, D_PROV, D_DIST, D_REGION,
                    DAREACENSO, DIR_CEN, CEN_POB,
                    CODGEO, FECHAREG, FECHA_ACT
                FROM pronoei_programas
                WHERE 1=1
            """
            params = []

            if dpto:
                sql += " AND D_DPTO = %s"
                params.append(dpto.upper())

            if area:
                sql += " AND DAREACENSO = %s"
                params.append(area.capitalize())

            if ciclo:
                sql += " AND D_TIPOPROG LIKE %s"
                params.append(f"%{ciclo}%")

            sql += " LIMIT 2000"

            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()


def get_departamentos():
    """Lista de departamentos únicos para el filtro del mapa."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT D_DPTO
                FROM pronoei_programas
                ORDER BY D_DPTO
            """)
            rows = cursor.fetchall()
            return [r["D_DPTO"] for r in rows]
    finally:
        conn.close()


def get_resumen_por_dpto():
    """Cantidad de programas por departamento para el mapa de calor."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    D_DPTO,
                    COUNT(*) AS total,
                    SUM(CASE WHEN DAREACENSO = 'Rural' THEN 1 ELSE 0 END) AS rural,
                    SUM(CASE WHEN DAREACENSO = 'Urbana' THEN 1 ELSE 0 END) AS urbana
                FROM pronoei_programas
                GROUP BY D_DPTO
                ORDER BY total DESC
            """)
            return cursor.fetchall()
    finally:
        conn.close()