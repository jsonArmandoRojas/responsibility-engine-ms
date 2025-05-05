#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuración y gestión de logging.
"""

import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import sys
from datetime import datetime

# Configuración global
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DIR = os.environ.get('LOG_DIR', 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'responsabilidad.log')

# Asegurar que existe el directorio de logs
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def setup_logging():
    """Configura el sistema de logging."""
    # Configurar el formato
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Configurar el handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configurar el handler para archivo con rotación
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Configurar el handler para archivo con rotación diaria
    daily_handler = TimedRotatingFileHandler(
        LOG_FILE, when='midnight', interval=1, backupCount=30
    )
    daily_handler.setFormatter(formatter)
    daily_handler.suffix = "%Y-%m-%d"
    
    # Configurar el logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    
    # Limpiar handlers existentes
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Añadir los handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(daily_handler)
    
    # Logger para arranque
    root_logger.info(f"Logging configurado: nivel={LOG_LEVEL}, archivo={LOG_FILE}")
    return root_logger

def get_logger(name):
    """
    Obtiene un logger configurado para un módulo específico.
    
    Args:
        name (str): Nombre del módulo/componente
        
    Returns:
        logging.Logger: Logger configurado
    """
    return logging.getLogger(name)