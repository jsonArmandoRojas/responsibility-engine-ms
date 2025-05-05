#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuraciones globales de la aplicación.
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()

class Settings:
    """Configuraciones de la aplicación."""
    
    # Configuración de servidor
    HOST: str = os.environ.get('HOST', '0.0.0.0')
    PORT: int = int(os.environ.get('PORT', '8000'))
    DEBUG: bool = os.environ.get('DEBUG', 'false').lower() == 'true'
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Configuración de base de datos
    DB_PATH: str = os.environ.get('DB_PATH', 'responsabilidad.db')
    
    # Configuración de seguridad
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'clave_secreta_muy_segura_para_desarrollo')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
    
    # Configuración de CORS
    CORS_ORIGINS: List[str] = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Configuración de rutas
    UPLOAD_DIR: str = os.environ.get('UPLOAD_DIR', 'uploads')
    MODELS_DIR: str = os.environ.get('MODELS_DIR', 'models')
    
    # Configuración de modelos IA
    MODEL_DAMAGE_PATH: str = os.environ.get('MODEL_DAMAGE_PATH', os.path.join(MODELS_DIR, 'damage_detector.pth'))
    MODEL_RESPONSIBILITY_PATH: str = os.environ.get('MODEL_RESPONSIBILITY_PATH', os.path.join(MODELS_DIR, 'responsibility_model.pkl'))
    
    # Configuración de OCR
    TESSERACT_CMD: str = os.environ.get('TESSERACT_CMD', '')
    OCR_LANG: str = os.environ.get('OCR_LANG', 'spa')
    
    # Configuración de blockchain (simplificada)
    BLOCKCHAIN_ENABLED: bool = os.environ.get('BLOCKCHAIN_ENABLED', 'false').lower() == 'true'
    BLOCKCHAIN_URL: str = os.environ.get('BLOCKCHAIN_URL', 'http://localhost:8545')
    
    # Configuración de la matriz de responsabilidad
    MATRIZ_PATH: str = os.environ.get('MATRIZ_PATH', os.path.join('config', 'matriz_responsabilidad.json'))

# Crear instancia global de configuración
settings = Settings()