import pymysql
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

def get_connection():
    return pymysql.connect(
        host=os.getenv("TIDB_HOST"),
        port=int(os.getenv("TIDB_PORT", "4000")),
        user=os.getenv("TIDB_USER"),
        password=os.getenv("TIDB_PASSWORD"),
        database=os.getenv("TIDB_DB", "educacion_inicial"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        ssl_verify_cert=True,
        ssl_verify_identity=True,
    )

def test_connection():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION() AS version")
            result = cursor.fetchone()
            cursor.execute("SELECT COUNT(*) AS total FROM pronoei_programas")
            total = cursor.fetchone()
        return {
            "estado": "conectado",
            "mysql_version": result["version"],
            "total_registros": total["total"],
        }
    finally:
        conn.close()