#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuración principal de la API FastAPI.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from api.middleware.auth import verify_token
from api.routes import siniestros, vehiculos, evidencias, reportes
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Motor de Responsabilidad API",
    description="API para el Motor de Responsabilidad Inteligente con IA para gestión de siniestros",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(siniestros.router, prefix="/api/v1")
app.include_router(vehiculos.router, prefix="/api/v1")
app.include_router(evidencias.router, prefix="/api/v1")
app.include_router(reportes.router, prefix="/api/v1")

@app.get("/api/health")
async def health_check():
    """Endpoint para verificar el estado de la API."""
    return {"status": "ok"}