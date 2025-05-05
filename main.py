#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Punto de entrada principal para el Motor de Responsabilidad.
"""

import uvicorn
import os
import argparse
from api.main import app
from config.settings import settings
from utils.logger import setup_logging

def parse_args():
    """Parsea argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(description='Motor de Responsabilidad Inteligente')
    parser.add_argument('--host', type=str, default=settings.HOST,
                        help=f'Host para servir la API (default: {settings.HOST})')
    parser.add_argument('--port', type=int, default=settings.PORT,
                        help=f'Puerto para servir la API (default: {settings.PORT})')
    parser.add_argument('--debug', action='store_true', default=settings.DEBUG,
                        help='Ejecutar en modo debug con recarga automática')
    parser.add_argument('--log-level', type=str, default=settings.LOG_LEVEL,
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help=f'Nivel de logging (default: {settings.LOG_LEVEL})')
    return parser.parse_args()

def main():
    """Función principal de entrada."""
    # Parsear argumentos
    args = parse_args()
    
    # Configurar logging
    logger = setup_logging()
    logger.info(f"Iniciando Motor de Responsabilidad: host={args.host}, port={args.port}, debug={args.debug}")
    
    # Crear directorios necesarios
    for folder in [settings.UPLOAD_DIR, settings.MODELS_DIR]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            logger.info(f"Directorio creado: {folder}")
    
    # Iniciar servidor
    uvicorn.run(
        "api.main:app",
        host=args.host,
        port=args.port,
        reload=args.debug,
        log_level=args.log_level.lower()
    )

if __name__ == "__main__":
    main()