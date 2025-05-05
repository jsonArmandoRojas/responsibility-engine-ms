#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para extracción de texto de documentos PDF.
"""

import os
from typing import Optional, List
import PyPDF2
from utils.logger import get_logger

logger = get_logger(__name__)

class PDFReader:
    """
    Clase para extraer texto de documentos PDF.
    """
    
    def __init__(self):
        """Inicializa el lector de PDF."""
        logger.info("PDFReader inicializado")
    
    def extraer_texto(self, pdf_path: str) -> str:
        """
        Extrae el texto completo de un documento PDF.
        
        Args:
            pdf_path (str): Ruta al archivo PDF
            
        Returns:
            str: Texto extraído del PDF
        
        Raises:
            FileNotFoundError: Si el archivo no existe
            Exception: Para otros errores durante la extracción
        """
        if not os.path.exists(pdf_path):
            error_msg = f"El archivo PDF no existe: {pdf_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            texto_completo = ""
            
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_paginas = len(reader.pages)
                
                logger.info(f"Extrayendo texto de {num_paginas} páginas del PDF: {pdf_path}")
                
                for pagina_num in range(num_paginas):
                    pagina = reader.pages[pagina_num]
                    texto_pagina = pagina.extract_text()
                    
                    if texto_pagina:
                        texto_completo += texto_pagina + "\n\n"
            
            logger.info(f"Texto extraído correctamente, longitud: {len(texto_completo)} caracteres")
            return texto_completo
            
        except Exception as e:
            error_msg = f"Error al extraer texto del PDF {pdf_path}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def extraer_pagina(self, pdf_path: str, numero_pagina: int) -> Optional[str]:
        """
        Extrae el texto de una página específica de un PDF.
        
        Args:
            pdf_path (str): Ruta al archivo PDF
            numero_pagina (int): Número de página a extraer (0-indexed)
            
        Returns:
            Optional[str]: Texto de la página o None si hay error
        """
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                if 0 <= numero_pagina < len(reader.pages):
                    pagina = reader.pages[numero_pagina]
                    return pagina.extract_text()
                else:
                    logger.warning(f"Número de página fuera de rango: {numero_pagina}, PDF tiene {len(reader.pages)} páginas")
                    return None
        except Exception as e:
            logger.error(f"Error al extraer página {numero_pagina} del PDF {pdf_path}: {str(e)}")
            return None
    
    def extraer_metadatos(self, pdf_path: str) -> Optional[dict]:
        """
        Extrae los metadatos de un documento PDF.
        
        Args:
            pdf_path (str): Ruta al archivo PDF
            
        Returns:
            Optional[dict]: Diccionario de metadatos o None si hay error
        """
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                return reader.metadata
        except Exception as e:
            logger.error(f"Error al extraer metadatos del PDF {pdf_path}: {str(e)}")
            return None
    
    def obtener_num_paginas(self, pdf_path: str) -> Optional[int]:
        """
        Obtiene el número de páginas de un PDF.
        
        Args:
            pdf_path (str): Ruta al archivo PDF
            
        Returns:
            Optional[int]: Número de páginas o None si hay error
        """
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                return len(reader.pages)
        except Exception as e:
            logger.error(f"Error al obtener número de páginas del PDF {pdf_path}: {str(e)}")
            return None