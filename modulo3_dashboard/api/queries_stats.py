import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.db import get_connection


def get_stats_por_region():
    """Total de programas agrupado por región DRE/GRE."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    D_REGION,
                    COUNT(*) AS total,
                    SUM(CASE WHEN DAREACENSO = 'Rural'  THEN 1 ELSE 0 END) AS rural,
                    SUM(CASE WHEN DAREACENSO = 'Urbana' THEN 1 ELSE 0 END) AS urbana
                FROM pronoei_programas
                GROUP BY D_REGION
                ORDER BY total DESC
            """)
            return cursor.fetchall()
    finally:
        conn.close()


def get_stats_por_ciclo():
    """Distribución de programas por tipo de programa/ciclo."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    D_TIPOPROG,
                    COUNT(*) AS total
                FROM pronoei_programas
                GROUP BY D_TIPOPROG
                ORDER BY total DESC
            """)
            return cursor.fetchall()
    finally:
        conn.close()


def get_stats_por_gestion():
    """Distribución por tipo de gestión (pública/privada)."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    D_GESTION,
                    COUNT(*) AS total
                FROM pronoei_programas
                GROUP BY D_GESTION
                ORDER BY total DESC
            """)
            return cursor.fetchall()
    finally:
        conn.close()


def get_stats_por_turno():
    """Distribución por turno (mañana/tarde)."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    D_COD_TUR,
                    COUNT(*) AS total
                FROM pronoei_programas
                GROUP BY D_COD_TUR
                ORDER BY total DESC
            """)
            return cursor.fetchall()
    finally:
        conn.close()


def get_resumen_general():
    """Números globales para las tarjetas del dashboard."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    COUNT(*)                                                        AS total_programas,
                    COUNT(DISTINCT D_DPTO)                                          AS total_dptos,
                    COUNT(DISTINCT D_DIST)                                          AS total_distritos,
                    SUM(CASE WHEN DAREACENSO = 'Rural'  THEN 1 ELSE 0 END)         AS total_rural,
                    SUM(CASE WHEN DAREACENSO = 'Urbana' THEN 1 ELSE 0 END)         AS total_urbana,
                    SUM(CASE WHEN D_TIPOPROG LIKE '%Ciclo I%'  THEN 1 ELSE 0 END)  AS ciclo_1,
                    SUM(CASE WHEN D_TIPOPROG LIKE '%Ciclo II%' THEN 1 ELSE 0 END)  AS ciclo_2
                FROM pronoei_programas
            """)
            return cursor.fetchone()
    finally:
        conn.close()