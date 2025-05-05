#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Endpoints relacionados con la gestión de siniestros.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import JSONResponse
from typing import List, Optional
from api.middleware.auth import verify_token
from api.schemas.siniestro import SiniestroCreate, SiniestroResponse, SiniestroUpdate
from core.engine import MotorPrincipal
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["Siniestros"])
motor = MotorPrincipal()

@router.post("/siniestros", response_model=SiniestroResponse, status_code=status.HTTP_201_CREATED)
async def crear_siniestro(
    siniestro: SiniestroCreate,
    token: str = Depends(verify_token)
):
    """Crea un nuevo registro de siniestro."""
    try:
        resultado = motor.procesar_siniestro(siniestro.dict())
        return resultado
    except Exception as e:
        logger.error(f"Error al procesar siniestro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar siniestro: {str(e)}"
        )

@router.get("/siniestros/{siniestro_id}", response_model=SiniestroResponse)
async def obtener_siniestro(
    siniestro_id: str,
    token: str = Depends(verify_token)
):
    """Obtiene los detalles de un siniestro específico."""
    try:
        # Consultar desde la base de datos
        return {"id": siniestro_id, "estado": "procesado"}
    except Exception as e:
        logger.error(f"Error al obtener siniestro {siniestro_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Siniestro no encontrado: {siniestro_id}"
        )

@router.post("/siniestros/{siniestro_id}/documentos")
async def subir_documento(
    siniestro_id: str,
    archivo: UploadFile = File(...),
    tipo_documento: str = Form(...),
    token: str = Depends(verify_token)
):
    """Sube un documento relacionado con un siniestro."""
    try:
        # Procesar el documento
        return {"mensaje": "Documento procesado correctamente"}
    except Exception as e:
        logger.error(f"Error al procesar documento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar documento: {str(e)}"
        )