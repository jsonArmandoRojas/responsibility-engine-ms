#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Detector de daños en vehículos usando visión por computadora.
"""

import os
import cv2
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from utils.logger import get_logger

logger = get_logger(__name__)

class DamageDetector:
    """
    Detector de daños en vehículos mediante visión por computadora.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Inicializa el detector de daños.
        
        Args:
            model_path (Optional[str]): Ruta al modelo pre-entrenado
        """
        # En producción, cargaríamos un modelo pre-entrenado de detección de daños
        # Aquí simulamos el comportamiento
        self.model_loaded = False
        
        if model_path and os.path.exists(model_path):
            # Simular carga de modelo
            self.model_loaded = True
            logger.info(f"Modelo de detección de daños cargado desde: {model_path}")
        else:
            logger.warning("Usando detector de daños en modo simulado (sin modelo real)")
        
        # Inicializar detector de vehículos (Haar Cascade como ejemplo)
        cascade_path = cv2.data.haarcascades + 'haarcascade_car.xml'
        if os.path.exists(cascade_path):
            self.car_cascade = cv2.CascadeClassifier(cascade_path)
            logger.info("Detector de vehículos inicializado")
        else:
            self.car_cascade = None
            logger.warning("No se pudo cargar el detector de vehículos")
    
    def detectar_danos(self, imagen_path: str) -> Dict[str, Any]:
        """
        Detecta daños en una imagen de un vehículo.
        
        Args:
            imagen_path (str): Ruta a la imagen
            
        Returns:
            Dict[str, Any]: Resultados del análisis de daños
        """
        if not os.path.exists(imagen_path):
            error_msg = f"La imagen no existe: {imagen_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            logger.info(f"Analizando daños en imagen: {imagen_path}")
            
            # Cargar imagen
            imagen = cv2.imread(imagen_path)
            if imagen is None:
                raise Exception(f"No se pudo cargar la imagen: {imagen_path}")
            
            # Detectar vehículos
            vehiculos = self._detectar_vehiculos(imagen)
            
            if not vehiculos:
                logger.warning(f"No se detectaron vehículos en la imagen: {imagen_path}")
                return {
                    "vehiculos_detectados": 0,
                    "danos_detectados": 0,
                    "tiene_danos": False,
                    "confianza": 0.0,
                    "areas_dano": []
                }
            
            # Para cada vehículo detectado, analizar daños
            resultados = []
            
            for i, (x, y, w, h) in enumerate(vehiculos):
                # Recortar ROI del vehículo
                roi = imagen[y:y+h, x:x+w]
                
                # Analizar daños en el ROI
                resultado_vehiculo = self._analizar_danos_vehiculo(roi)
                resultado_vehiculo["posicion"] = {"x": x, "y": y, "width": w, "height": h}
                resultado_vehiculo["vehiculo_id"] = i + 1
                
                resultados.append(resultado_vehiculo)
            
            # Determinar resultado global
            tiene_danos = any(r["tiene_danos"] for r in resultados)
            confianza_promedio = sum(r["confianza"] for r in resultados) / len(resultados)
            
            return {
                "vehiculos_detectados": len(vehiculos),
                "danos_detectados": sum(r["danos_detectados"] for r in resultados),
                "tiene_danos": tiene_danos,
                "confianza": round(confianza_promedio, 2),
                "vehiculos": resultados
            }
            
        except Exception as e:
            error_msg = f"Error al analizar daños en {imagen_path}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def _detectar_vehiculos(self, imagen: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detecta vehículos en una imagen.
        
        Args:
            imagen (np.ndarray): Imagen en formato OpenCV
            
        Returns:
            List[Tuple[int, int, int, int]]: Lista de rectangulos (x, y, w, h)
        """
        if self.car_cascade is None:
            # Simular detección si no hay modelo
            height, width = imagen.shape[:2]
            return [(0, 0, width, height)]
        
        # Convertir a escala de grises
        gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        
        # Detectar vehículos
        vehiculos = self.car_cascade.detectMultiScale(
            gris, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(100, 100)
        )
        
        if len(vehiculos) == 0:
            # Si no se detecta nada, asumir que toda la imagen es un vehículo
            height, width = imagen.shape[:2]
            return [(0, 0, width, height)]
        
        return vehiculos
    
    def _analizar_danos_vehiculo(self, roi: np.ndarray) -> Dict[str, Any]:
        """
        Analiza daños en la región de interés de un vehículo.
        
        Args:
            roi (np.ndarray): Región de interés (recorte del vehículo)
            
        Returns:
            Dict[str, Any]: Resultados del análisis
        """
        # En producción, aquí usaríamos un modelo especializado de deep learning
        # Por ahora, simulamos el comportamiento con análisis básico de color/textura
        
        # 1. Convertir a espacio HSV para mejor análisis de color
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # 2. Buscar regiones con alto contraste (posibles abolladuras)
        gris = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        sobelx = cv2.Sobel(gris, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gris, cv2.CV_64F, 0, 1, ksize=3)
        magnitud = cv2.magnitude(sobelx, sobely)
        
        # Umbral para considerar alto contraste
        threshold = np.mean(magnitud) * 2
        mascara_contraste = (magnitud > threshold).astype(np.uint8) * 255
        
        # 3. Contar regiones de alto contraste
        num_componentes, etiquetas, stats, centroides = cv2.connectedComponentsWithStats(mascara_contraste)
        
        # Filtrar componentes pequeños (ruido)
        areas_dano = []
        for i in range(1, num_componentes):  # Ignorar componente 0 (fondo)
            if stats[i, cv2.CC_STAT_AREA] > 100:  # Área mínima
                x = stats[i, cv2.CC_STAT_LEFT]
                y = stats[i, cv2.CC_STAT_TOP]
                w = stats[i, cv2.CC_STAT_WIDTH]
                h = stats[i, cv2.CC_STAT_HEIGHT]
                areas_dano.append({
                    "posicion": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                    "area": int(stats[i, cv2.CC_STAT_AREA]),
                    "tipo": self._clasificar_tipo_dano(roi[y:y+h, x:x+w]),
                    "severidad": self._clasificar_severidad_dano(roi[y:y+h, x:x+w])
                })
        
        # 4. Determinar si hay daños
        danos_detectados = len(areas_dano)
        tiene_danos = danos_detectados > 0
        
        # 5. Estimar confianza
        if self.model_loaded:
            # Confianza basada en el modelo (simulado)
            confianza = 0.85 if tiene_danos else 0.75
        else:
            # Confianza baja en el modo simulado
            confianza = 0.60 if tiene_danos else 0.50
        
        return {
            "danos_detectados": danos_detectados,
            "tiene_danos": tiene_danos,
            "confianza": round(confianza, 2),
            "areas_dano": areas_dano
        }
    
    def _clasificar_tipo_dano(self, roi_dano: np.ndarray) -> str:
        """
        Clasifica el tipo de daño en una región.
        
        Args:
            roi_dano (np.ndarray): Región del daño
            
        Returns:
            str: Tipo de daño ('abolladura', 'rayón', etc.)
        """
        # Implementación simulada - en producción usaríamos un clasificador real
        # Análisis simple de forma para decidir
        altura, anchura = roi_dano.shape[:2]
        ratio = anchura / altura if altura > 0 else 0
        
        if ratio > 3:
            return "rayón"
        elif ratio < 0.5:
            return "rayón_vertical"
        else:
            return "abolladura"
    
    def _clasificar_severidad_dano(self, roi_dano: np.ndarray) -> str:
        """
        Clasifica la severidad del daño.
        
        Args:
            roi_dano (np.ndarray): Región del daño
            
        Returns:
            str: Severidad ('leve', 'moderado', 'grave')
        """
        # Implementación simulada - en producción usaríamos un clasificador real
        # Usamos el tamaño relativo como indicador simple de severidad
        area = roi_dano.shape[0] * roi_dano.shape[1]
        
        # Normalizar por tamaño de imagen (simulado)
        if area < 5000:
            return "leve"
        elif area < 15000:
            return "moderado"
        else:
            return "grave"