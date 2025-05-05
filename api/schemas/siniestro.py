#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Esquemas Pydantic para la validación de datos de siniestros.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

class Ubicacion(BaseModel):
    direccion: str
    localidad: Optional[str] = None
    ciudad: str
    coordenadas: Optional[Dict[str, float]] = None

class Vehiculo(BaseModel):
    placa: str
    marca: str
    modelo: str
    año: int
    conductor: str
    poliza_numero: Optional[str] = None
    aseguradora: Optional[str] = None

class Evidencia(BaseModel):
    tipo: str  # "foto", "video", "documento", etc.
    url: str
    timestamp: datetime
    geolocalizacion: Optional[Dict[str, float]] = None
    hash: Optional[str] = None  # Para verificación blockchain

class SiniestroCreate(BaseModel):
    fecha: datetime = Field(default_factory=datetime.now)
    ubicacion: Ubicacion
    vehiculo_a: Vehiculo
    vehiculo_b: Vehiculo
    descripcion: Optional[str] = None
    evidencias: Optional[List[Evidencia]] = []
    disputa: bool = False
    generar_acta: bool = True

    class Config:
        schema_extra = {
            "example": {
                "fecha": "2025-05-01T14:23:45",
                "ubicacion": {
                    "direccion": "Calle 85 #15-23",
                    "localidad": "Chapinero",
                    "ciudad": "Bogotá",
                    "coordenadas": {"lat": 4.6486, "lng": -74.0598}
                },
                "vehiculo_a": {
                    "placa": "ABC123",
                    "marca": "Toyota",
                    "modelo": "Corolla",
                    "año": 2023,
                    "conductor": "Juan Pérez",
                    "poliza_numero": "POL-2025-01234",
                    "aseguradora": "Seguros Bolívar"
                },
                "vehiculo_b": {
                    "placa": "XYZ789",
                    "marca": "Mazda",
                    "modelo": "3",
                    "año": 2024,
                    "conductor": "María Gómez",
                    "poliza_numero": "POL-2024-56789",
                    "aseguradora": "Seguros Bolívar"
                },
                "descripcion": "Colisión en intersección",
                "evidencias": [],
                "disputa": False,
                "generar_acta": True
            }
        }

class SiniestroUpdate(BaseModel):
    descripcion: Optional[str] = None
    estado: Optional[str] = None
    disputa: Optional[bool] = None

class ResponsabilidadResult(BaseModel):
    responsable: str  # "vehiculo_a", "vehiculo_b", "compartida", "no_aplica", "indeterminado"
    porcentaje_a: Optional[int] = None
    porcentaje_b: Optional[int] = None
    justificacion: Optional[str] = None
    mensaje: Optional[str] = None

class Indemnizacion(BaseModel):
    monto: float
    moneda: str = "COP"
    receptor: str  # "vehiculo_a", "vehiculo_b", etc.
    deducible: Optional[float] = None
    factor_cobertura: float = 1.0

class SiniestroResponse(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    fecha: datetime
    estado: str  # "procesando", "procesado", "disputado", "resuelto", etc.
    vehiculo_a: Vehiculo
    vehiculo_b: Vehiculo
    responsabilidad: Optional[ResponsabilidadResult] = None
    indemnizacion: Optional[Indemnizacion] = None
    acta_url: Optional[str] = None
    creado_en: datetime = Field(default_factory=datetime.now)
    actualizado_en: Optional[datetime] = None