import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.db import get_connection


def get_programas_inactivos(meses: int = 6):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT
                    COD_MOD,
                    CEN_EDU,
                    D_TIPOPROG,
                    DAREACENSO,
                    D_DPTO,
                    D_PROV,
                    D_DIST,
                    D_DREUGEL,
                    FECHA_ACT,
                    FECHAREG,
                    DATEDIFF(CURDATE(),
                        STR_TO_DATE(FECHAREG, '%d/%m/%Y')
                    ) AS dias_sin_actualizar
                FROM pronoei_programas
                WHERE
                    FECHAREG IS NOT NULL
                    AND FECHAREG != ''
                    AND STR_TO_DATE(FECHAREG, '%d/%m/%Y') IS NOT NULL
                    AND STR_TO_DATE(FECHAREG, '%d/%m/%Y') < DATE_SUB(CURDATE(), INTERVAL %s MONTH)
                ORDER BY dias_sin_actualizar DESC
                LIMIT 500
            """
            cursor.execute(sql, (meses,))
            return cursor.fetchall()
    finally:
        conn.close()


def get_resumen_alertas():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    D_DPTO,
                    D_DREUGEL,
                    COUNT(*) AS programas_inactivos
                FROM pronoei_programas
                WHERE
                    FECHAREG IS NOT NULL
                    AND STR_TO_DATE(FECHAREG, '%d/%m/%Y') < DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
                GROUP BY D_DPTO, D_DREUGEL
                ORDER BY programas_inactivos DESC
            """)
            return cursor.fetchall()
    finally:
        conn.close()


def get_conteo_alertas():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    COUNT(*) AS total_inactivos,
                    SUM(CASE WHEN DAREACENSO = 'Rural'  THEN 1 ELSE 0 END) AS rural_inactivos,
                    SUM(CASE WHEN DAREACENSO = 'Urbana' THEN 1 ELSE 0 END) AS urbana_inactivos
                FROM pronoei_programas
                WHERE
                    FECHAREG IS NOT NULL
                    AND STR_TO_DATE(FECHAREG, '%d/%m/%Y') < DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            """)
            return cursor.fetchone()
    finally:
        conn.close()