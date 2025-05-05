#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Validador de imágenes para evidencias de siniestros.
"""

import os
import cv2
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from typing import Dict, Any, Optional
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

class ImageValidator:
    """
    Validador de imágenes para verificar autenticidad y metadatos.
    """
    
    def __init__(self):
        """Inicializa el validador de imágenes."""
        logger.info("ImageValidator inicializado")
    
    def validar(
        self, 
        imagen_path: str,
        timestamp_esperado: Optional[datetime] = None,
        geolocalizacion_esperada: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Valida una imagen verificando autenticidad y metadatos.
        
        Args:
            imagen_path (str): Ruta a la imagen
            timestamp_esperado (Optional[datetime]): Timestamp esperado para validación
            geolocalizacion_esperada (Optional[Dict[str, float]]): Coordenadas esperadas
            
        Returns:
            Dict[str, Any]: Resultado de la validación
        """
        if not os.path.exists(imagen_path):
            error_msg = f"La imagen no existe: {imagen_path}"
            logger.error(error_msg)
            return {
                "valida": False,
                "mensaje": error_msg
            }
        
        try:
            logger.info(f"Validando imagen: {imagen_path}")
            
            # Validar formato de imagen
            formato_valido = self._validar_formato(imagen_path)
            if not formato_valido["valido"]:
                return {
                    "valida": False,
                    "mensaje": formato_valido["mensaje"]
                }
            
            # Extraer metadatos EXIF
            metadatos = self._extraer_metadatos(imagen_path)
            
            # Validar manipulación
            manipulacion = self._detectar_manipulacion(imagen_path)
            
            # Validar timestamp si se proporciona
            timestamp_valido = True
            mensaje_timestamp = ""
            if timestamp_esperado and "datetime" in metadatos:
                timestamp_valido, mensaje_timestamp = self._validar_timestamp(
                    metadatos["datetime"], timestamp_esperado
                )
            
            # Validar geolocalización si se proporciona
            geolocalizacion_valida = True
            mensaje_geolocalizacion = ""
            if geolocalizacion_esperada and "gps" in metadatos:
                geolocalizacion_valida, mensaje_geolocalizacion = self._validar_geolocalizacion(
                    metadatos["gps"], geolocalizacion_esperada
                )
            
            # Combinar resultados
            es_valida = formato_valido["valido"] and not manipulacion["detectada"]
            
            if timestamp_esperado:
                es_valida = es_valida and timestamp_valido
            
            if geolocalizacion_esperada:
                es_valida = es_valida and geolocalizacion_valida
            
            # Construir mensaje
            mensaje = "Imagen validada correctamente."
            if not formato_valido["valido"]:
                mensaje = formato_valido["mensaje"]
            elif manipulacion["detectada"]:
                mensaje = f"Se detectó posible manipulación: {manipulacion['mensaje']}"
            elif not timestamp_valido:
                mensaje = mensaje_timestamp
            elif not geolocalizacion_valida:
                mensaje = mensaje_geolocalizacion
            
            return {
                "valida": es_valida,
                "mensaje": mensaje,
                "metadatos": metadatos,
                "manipulacion": manipulacion
            }
            
        except Exception as e:
            error_msg = f"Error al validar imagen {imagen_path}: {str(e)}"
            logger.error(error_msg)
            return {
                "valida": False,
                "mensaje": error_msg
            }
    
    def _validar_formato(self, imagen_path: str) -> Dict[str, Any]:
        """
        Valida que el formato de la imagen sea aceptable.
        
        Args:
            imagen_path (str): Ruta a la imagen
            
        Returns:
            Dict[str, Any]: Resultado de la validación
        """
        try:
            # Verificar extensión
            extension = os.path.splitext(imagen_path)[1].lower()
            formatos_aceptados = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']
            
            if extension not in formatos_aceptados:
                return {
                    "valido": False,
                    "mensaje": f"Formato no aceptado: {extension}. Formatos permitidos: {', '.join(formatos_aceptados)}"
                }
            
            # Verificar que se pueda abrir la imagen
            imagen = Image.open(imagen_path)
            imagen.verify()  # Verifica que la imagen esté bien formada
            
            # Verificar tamaño mínimo
            with Image.open(imagen_path) as img:
                ancho, alto = img.size
            
            if ancho < 640 or alto < 480:
                return {
                    "valido": False,
                    "mensaje": f"Resolución insuficiente: {ancho}x{alto}. Mínimo requerido: 640x480"
                }
            
            return {
                "valido": True,
                "mensaje": "Formato válido",
                "dimension": f"{ancho}x{alto}",
                "formato": extension
            }
            
        except Exception as e:
            return {
                "valido": False,
                "mensaje": f"Error al validar formato: {str(e)}"
            }
    
    def _extraer_metadatos(self, imagen_path: str) -> Dict[str, Any]:
        """
        Extrae metadatos EXIF de una imagen.
        
        Args:
            imagen_path (str): Ruta a la imagen
            
        Returns:
            Dict[str, Any]: Metadatos extraídos
        """
        metadatos = {}
        
        try:
            with Image.open(imagen_path) as img:
                # Extraer datos EXIF si están disponibles
                exif_data = {}
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value
                    
                    # Extraer datos de fecha/hora
                    if 'DateTimeOriginal' in exif_data:
                        metadatos['datetime'] = exif_data['DateTimeOriginal']
                    elif 'DateTime' in exif_data:
                        metadatos['datetime'] = exif_data['DateTime']
                    
                    # Extraer datos GPS
                    if 'GPSInfo' in exif_data:
                        gps_info = {}
                        for gps_tag_id, value in exif_data['GPSInfo'].items():
                            gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                            gps_info[gps_tag] = value
                        
                        # Convertir coordenadas GPS
                        if 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
                            lat = self._convertir_coordenada_gps(gps_info['GPSLatitude'])
                            lng = self._convertir_coordenada_gps(gps_info['GPSLongitude'])
                            
                            # Ajustar por referencia (N/S, E/W)
                            if 'GPSLatitudeRef' in gps_info and gps_info['GPSLatitudeRef'] == 'S':
                                lat = -lat
                            if 'GPSLongitudeRef' in gps_info and gps_info['GPSLongitudeRef'] == 'W':
                                lng = -lng
                                
                            metadatos['gps'] = {
                                'latitude': lat,
                                'longitude': lng
                            }
                
                # Añadir información básica de la imagen
                metadatos['dimension'] = img.size
                metadatos['modo'] = img.mode
                metadatos['formato'] = img.format
                
            return metadatos
            
        except Exception as e:
            logger.warning(f"Error al extraer metadatos: {str(e)}")
            return metadatos
    
    def _convertir_coordenada_gps(self, coordenada) -> float:
        """
        Convierte una coordenada GPS del formato EXIF a decimal.
        
        Args:
            coordenada: Tupla de (grados, minutos, segundos)
            
        Returns:
            float: Coordenada en formato decimal
        """
        grados = float(coordenada[0])
        minutos = float(coordenada[1])
        segundos = float(coordenada[2])
        
        return grados + (minutos / 60.0) + (segundos / 3600.0)
    
    def _detectar_manipulacion(self, imagen_path: str) -> Dict[str, Any]:
        """
        Detecta posibles manipulaciones en la imagen.
        
        Args:
            imagen_path (str): Ruta a la imagen
            
        Returns:
            Dict[str, Any]: Resultado de la detección
        """
        # En producción, usaríamos algoritmos avanzados de detección de manipulación
        # Aquí implementamos una versión simplificada
        
        try:
            # Leer imagen
            imagen = cv2.imread(imagen_path)
            
            # Convertir a escala de grises
            gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
            
            # Detectar bordes con Canny
            bordes = cv2.Canny(gris, 100, 200)
            
            # Contar número de bordes (una medida simple)
            num_bordes = np.count_nonzero(bordes)
            
            # Análisis de Error Level Analysis (ELA) simplificado
            # En una implementación real, guardaríamos en JPEG con calidad conocida y compararíamos
            
            # Análisis de ruido
            ruido = cv2.fastNlMeansDenoising(gris, None, 10, 7, 21)
            diferencia_ruido = cv2.absdiff(gris, ruido)
            nivel_ruido = np.mean(diferencia_ruido)
            
            # Umbrales arbitrarios para demostración
            manipulacion_detectada = False
            mensaje = "No se detectó manipulación"
            
            if nivel_ruido < 2.0:
                manipulacion_detectada = True
                mensaje = "Posible manipulación: nivel de ruido anormalmente bajo"
            
            return {
                "detectada": manipulacion_detectada,
                "mensaje": mensaje,
                "metricas": {
                    "nivel_ruido": round(float(nivel_ruido), 2),
                    "num_bordes": int(num_bordes)
                }
            }
            
        except Exception as e:
            logger.warning(f"Error en detección de manipulación: {str(e)}")
            return {
                "detectada": False,
                "mensaje": f"No se pudo analizar manipulación: {str(e)}"
            }
    
    def _validar_timestamp(
        self, 
        timestamp_imagen: str, 
        timestamp_esperado: datetime
    ) -> tuple:
        """
        Valida que el timestamp de la imagen sea cercano al esperado.
        
        Args:
            timestamp_imagen (str): Timestamp extraído de la imagen (formato EXIF)
            timestamp_esperado (datetime): Timestamp esperado
            
        Returns:
            tuple: (es_valido, mensaje)
        """
        try:
            # Convertir timestamp EXIF a datetime
            # Formato típico: '2025:04:28 14:30:45'
            dt_imagen = datetime.strptime(timestamp_imagen, '%Y:%m:%d %H:%M:%S')
            
            # Calcular diferencia en segundos
            diferencia_segundos = abs((dt_imagen - timestamp_esperado).total_seconds())
            
            # Umbral: 5 minutos (300 segundos)
            if diferencia_segundos > 300:
                return False, f"Timestamp de imagen ({dt_imagen}) difiere del esperado ({timestamp_esperado}) por {diferencia_segundos} segundos"
            
            return True, f"Timestamp válido: {dt_imagen}"
            
        except Exception as e:
            logger.warning(f"Error al validar timestamp: {str(e)}")
            return False, f"Error al validar timestamp: {str(e)}"
    
    def _validar_geolocalizacion(
        self, 
        gps_imagen: Dict[str, float], 
        gps_esperado: Dict[str, float]
    ) -> tuple:
        """
        Valida que la geolocalización de la imagen sea cercana a la esperada.
        
        Args:
            gps_imagen (Dict[str, float]): Coordenadas extraídas de la imagen
            gps_esperado (Dict[str, float]): Coordenadas esperadas
            
        Returns:
            tuple: (es_valido, mensaje)
        """
        try:
            # Extraer coordenadas
            lat1 = gps_imagen.get('latitude', 0)
            lng1 = gps_imagen.get('longitude', 0)
            
            lat2 = gps_esperado.get('lat', 0)
            lng2 = gps_esperado.get('lng', 0)
            
            # Calcular distancia en kilómetros usando la fórmula de Haversine
            distancia = self._calcular_distancia_haversine(lat1, lng1, lat2, lng2)
            
            # Umbral: 100 metros (0.1 km)
            if distancia > 0.1:
                return False, f"Ubicación de imagen difiere de la esperada por {distancia:.2f} km"
            
            return True, f"Geolocalización válida: {lat1:.6f}, {lng1:.6f}"
            
        except Exception as e:
            logger.warning(f"Error al validar geolocalización: {str(e)}")
            return False, f"Error al validar geolocalización: {str(e)}"
    
    def _calcular_distancia_haversine(
        self, 
        lat1: float, 
        lon1: float, 
        lat2: float, 
        lon2: float
    ) -> float:
        """
        Calcula la distancia entre dos puntos geográficos usando la fórmula de Haversine.
        
        Args:
            lat1, lon1: Coordenadas del primer punto
            lat2, lon2: Coordenadas del segundo punto
            
        Returns:
            float: Distancia en kilómetros
        """
        import math
        
        # Radio de la Tierra en km
        R = 6371.0
        
        # Convertir grados a radianes
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Diferencias
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Fórmula de Haversine
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distancia = R * c
        
        return distancia