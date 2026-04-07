import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.db import test_connection
from modulo1_mapa.api.routes_mapa    import router as router_mapa
from modulo2_brecha.api.routes_brecha import router as router_brecha
from modulo3_dashboard.api.routes_stats import router as router_stats
from modulo4_alertas.api.routes_alertas  import router as router_alertas


app = FastAPI(
    title="GeoEdu PRONOEI API",
    description="API para análisis de programas no escolarizados de educación inicial en Perú",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_mapa,    prefix="/api/mapa",    tags=["Módulo 1 — Mapa"])
app.include_router(router_brecha, prefix="/api/brecha", tags=["Módulo 2 — Brecha"])
app.include_router(router_stats, prefix="/api/dashboard", tags=["Módulo 3 — Dashboard"])
app.include_router(router_alertas,  prefix="/api/alertas",   tags=["Módulo 4 — Alertas"])

@app.get("/", tags=["Estado"])
def home():
    return {
        "proyecto": "GeoEdu PRONOEI",
        "version": "1.0.0",
        "estado": "activo",
        "docs": "http://127.0.0.1:8000/docs",
    }

@app.get("/api/ping", tags=["Estado"])
def ping_db():
    return test_connection()