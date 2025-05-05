#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para OCR de imágenes y documentos escaneados.
"""

import os
from typing import Optional, List, Tuple
import pytesseract
from PIL import Image
import cv2
import numpy as np
from utils.logger import get_logger

logger = get_logger(__name__)

class OCREngine:
    """
    Motor OCR para procesar imágenes y documentos escaneados.
    """
    
    def __init__(self, tesseract_cmd: Optional[str] = None, lang: str = 'spa'):
        """
        Inicializa el motor OCR.
        
        Args:
            tesseract_cmd (Optional[str]): Ruta al ejecutable de Tesseract
            lang (str): Idioma para el OCR (por defecto 'spa' para español)
        """
        # Configurar Tesseract si se proporciona una ruta personalizada
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        self.lang = lang
        logger.info(f"OCREngine inicializado con idioma: {self.lang}")
    
    def procesar_imagen(self, imagen_path: str) -> str:
        """
        Procesa una imagen para extraer texto.
        
        Args:
            imagen_path (str): Ruta a la imagen
            
        Returns:
            str: Texto extraído de la imagen
            
        Raises:
            FileNotFoundError: Si la imagen no existe
            Exception: Para otros errores durante el procesamiento
        """
        if not os.path.exists(imagen_path):
            error_msg = f"La imagen no existe: {imagen_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            logger.info(f"Procesando imagen con OCR: {imagen_path}")
            
            # Cargar la imagen
            imagen = cv2.imread(imagen_path)
            if imagen is None:
                raise Exception(f"No se pudo cargar la imagen: {imagen_path}")
            
            # Preprocesamiento
            imagen_procesada = self._preprocesar_imagen(imagen)
            
            # OCR con Tesseract
            texto = pytesseract.image_to_string(imagen_procesada, lang=self.lang)
            
            logger.info(f"OCR completado, longitud del texto: {len(texto)} caracteres")
            return texto
            
        except Exception as e:
            error_msg = f"Error en OCR para imagen {imagen_path}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def procesar_documento(self, documento_path: str) -> str:
        """
        Procesa un documento (puede ser PDF o imagen) y extrae texto.
        
        Args:
            documento_path (str): Ruta al documento
            
        Returns:
            str: Texto extraído del documento
        """
        extension = os.path.splitext(documento_path)[1].lower()
        
        if extension in ['.pdf']:
            # Convertir PDF a imágenes y procesar
            return self._procesar_pdf(documento_path)
        elif extension in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.gif']:
            # Procesar imagen directamente
            return self.procesar_imagen(documento_path)
        else:
            error_msg = f"Formato de documento no soportado: {extension}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def _procesar_pdf(self, pdf_path: str) -> str:
        """
        Procesa un PDF convirtiéndolo a imágenes y aplicando OCR.
        
        Args:
            pdf_path (str): Ruta al PDF
            
        Returns:
            str: Texto extraído del PDF
        """
        try:
            import pdf2image
            import tempfile
            
            texto_completo = ""
            
            # Convertir PDF a imágenes
            with tempfile.TemporaryDirectory() as path:
                imagenes = pdf2image.convert_from_path(pdf_path)
                
                logger.info(f"Convertido PDF a {len(imagenes)} imágenes para OCR")
                
                for i, imagen in enumerate(imagenes):
                    temp_img_path = os.path.join(path, f'pagina_{i}.png')
                    imagen.save(temp_img_path, 'PNG')
                    
                    # Procesar la imagen
                    texto_pagina = self.procesar_imagen(temp_img_path)
                    texto_completo += texto_pagina + "\n\n"
            
            return texto_completo
            
        except Exception as e:
            error_msg = f"Error en OCR para PDF {pdf_path}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def _preprocesar_imagen(self, imagen: np.ndarray) -> np.ndarray:
        """
        Preprocesa una imagen para mejorar resultados de OCR.
        
        Args:
            imagen (np.ndarray): Imagen en formato OpenCV
            
        Returns:
            np.ndarray: Imagen preprocesada
        """
        # Convertir a escala de grises
        gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        
        # Aplicar umbral adaptativo
        umbral = cv2.adaptiveThreshold(
            gris, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Reducción de ruido
        kernel = np.ones((1, 1), np.uint8)
        umbral = cv2.morphologyEx(umbral, cv2.MORPH_CLOSE, kernel)
        
        return umbral