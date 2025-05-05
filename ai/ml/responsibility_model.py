#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelo para predicción de responsabilidad en siniestros.
"""

from typing import Dict, List, Any, Optional
import numpy as np
from utils.logger import get_logger

logger = get_logger(__name__)

class ResponsibilityModel:
    """
    Modelo para predicción de responsabilidad en siniestros viales.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Inicializa el modelo de predicción de responsabilidad.
        
        Args:
            model_path (Optional[str]): Ruta al modelo pre-entrenado
        """
        # En producción, cargaríamos un modelo ML real
        # Aquí simulamos el comportamiento
        self.model_loaded = False
        
        if model_path:
            # Simular carga de modelo
            self.model_loaded = True
            logger.info(f"Modelo de predicción cargado desde: {model_path}")
        else:
            logger.warning("Usando modelo de predicción en modo simulado")
        
        # Inicializar matriz de responsabilidad (basada en el documento)
        self._init_matriz_responsabilidad()
        
        logger.info("Modelo de predicción de responsabilidad inicializado")
    
    def _init_matriz_responsabilidad(self):
        """Inicializa la matriz de responsabilidad de 15x15."""
        # Matriz de responsabilidad según el documento
        self.matriz = [
            # 1   2    3    4    5    6    7    8    9    10   11   12   13   14   15
            ["NA", "B", "A", "B", "B", "A", "NA", "B", "B", "NA", "NA", "B", "B", "A", "B"],  # 1
            ["A", "NA", "A", "B", "NA", "A", "NA", "B", "NA", "A", "A", "A", "NA", "A", "A"],  # 2
            ["B", "B", "NA", "B", "NA", "B", "NA", "B", "B", "B", "B", "B", "B", "B", "NA"],  # 3
            ["A", "A", "A", "C", "C", "A", "A", "B", "B", "A", "A", "A", "B", "A", "B"],  # 4
            ["A", "NA", "NA", "C", "C", "A", "NA", "C", "NA", "A", "A", "A", "B", "NA", "A"],  # 5
            ["B", "B", "A", "B", "B", "NA", "NA", "B", "C", "B", "B", "B", "B", "A", "A"],  # 6
            ["NA", "NA", "NA", "B", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "A"],  # 7
            ["A", "A", "A", "A", "C", "A", "NA", "C", "A", "A", "A", "A", "B", "A", "A"],  # 8
            ["A", "NA", "A", "A", "NA", "C", "NA", "B", "C", "A", "A", "A", "B", "C", "A"],  # 9
            ["NA", "B", "A", "B", "B", "A", "NA", "B", "B", "C", "C", "A", "B", "A", "A"],  # 10
            ["NA", "B", "A", "B", "B", "A", "NA", "B", "B", "C", "NA", "A", "B", "A", "A"],  # 11
            ["A", "B", "A", "B", "B", "A", "NA", "B", "B", "B", "B", "NA", "B", "A", "A"],  # 12
            ["A", "NA", "A", "A", "A", "A", "NA", "A", "A", "A", "A", "A", "NA", "A", "A"],  # 13
            ["B", "B", "A", "B", "NA", "B", "NA", "B", "C", "B", "B", "B", "B", "C", "A"],  # 14
            ["B", "B", "NA", "A", "B", "B", "B", "B", "B", "B", "B", "B", "B", "B", "NA"],  # 15
        ]
    
    def predecir_circunstancia(
        self, 
        vehiculo: Dict[str, Any], 
        documentos: List[Dict[str, Any]], 
        evidencias: List[Dict[str, Any]]
    ) -> int:
        """
        Predice la circunstancia aplicable a un vehículo.
        
        Args:
            vehiculo (Dict[str, Any]): Datos del vehículo
            documentos (List[Dict[str, Any]]): Documentos procesados
            evidencias (List[Dict[str, Any]]): Evidencias procesadas
            
        Returns:
            int: Número de circunstancia (1-15)
        """
        logger.info(f"Prediciendo circunstancia para vehículo {vehiculo.get('placa', 'desconocido')}")
        
        if self.model_loaded:
            # Simulación de modelo real
            return self._predecir_con_modelo(vehiculo, documentos, evidencias)
        else:
            # Simulación simplificada
            return self._predecir_simplificado(vehiculo, documentos, evidencias)
    
    def predecir_responsabilidad(
        self, 
        vehiculo_a: Dict[str, Any], 
        vehiculo_b: Dict[str, Any],
        documentos: List[Dict[str, Any]], 
        evidencias: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Predice la responsabilidad entre dos vehículos.
        
        Args:
            vehiculo_a (Dict[str, Any]): Datos del vehículo A
            vehiculo_b (Dict[str, Any]): Datos del vehículo B
            documentos (List[Dict[str, Any]]): Documentos procesados
            evidencias (List[Dict[str, Any]]): Evidencias procesadas
            
        Returns:
            Dict[str, Any]: Resultado de la predicción
        """
        # Predecir circunstancias
        circunstancia_a = self.predecir_circunstancia(vehiculo_a, documentos, evidencias)
        circunstancia_b = self.predecir_circunstancia(vehiculo_b, documentos, evidencias)
        
        # Aplicar matriz de responsabilidad
        codigo = self.matriz[circunstancia_a - 1][circunstancia_b - 1]
        
        # Interpretar código
        resultado = self._interpretar_codigo(codigo, circunstancia_a, circunstancia_b)
        
        logger.info(f"Responsabilidad predicha: {resultado['responsable']} (A={circunstancia_a}, B={circunstancia_b})")
        return resultado
    
    def _predecir_con_modelo(
        self, 
        vehiculo: Dict[str, Any], 
        documentos: List[Dict[str, Any]], 
        evidencias: List[Dict[str, Any]]
    ) -> int:
        """
        Predice circunstancia usando un modelo ML.
        
        Args:
            vehiculo (Dict[str, Any]): Datos del vehículo
            documentos (List[Dict[str, Any]]): Documentos procesados
            evidencias (List[Dict[str, Any]]): Evidencias procesadas
            
        Returns:
            int: Número de circunstancia (1-15)
        """
        # Simulación de predicción con modelo
        
        # 1. Extraer características relevantes
        features = self._extraer_caracteristicas(vehiculo, documentos, evidencias)
        
        # 2. Simular predicción del modelo
        # En producción, aquí llamaríamos a model.predict(features)
        # Simulación simple: usar un vector de probabilidades aleatorio
        probabilidades = np.random.random(15)
        probabilidades = probabilidades / np.sum(probabilidades)  # Normalizar
        
        # 3. Determinar la clase con mayor probabilidad
        circunstancia = np.argmax(probabilidades) + 1  # +1 porque las circunstancias son 1-indexed
        
        # Simular confianza
        confianza = probabilidades[circunstancia - 1]
        logger.info(f"Circunstancia predicha por modelo: {circunstancia} (confianza: {confianza:.2f})")
        
        return circunstancia
    
    def _predecir_simplificado(
        self, 
        vehiculo: Dict[str, Any], 
        documentos: List[Dict[str, Any]], 
        evidencias: List[Dict[str, Any]]
    ) -> int:
        """
        Predice circunstancia usando reglas simples.
        
        Args:
            vehiculo (Dict[str, Any]): Datos del vehículo
            documentos (List[Dict[str, Any]]): Documentos procesados
            evidencias (List[Dict[str, Any]]): Evidencias procesadas
            
        Returns:
            int: Número de circunstancia (1-15)
        """
        # Implementación basada en reglas simples
        
        # Buscar pistas en las descripciones y clasificaciones
        pistas_circunstancias = {
            "sentido contrario": 1,
            "invad": 2,
            "giro": 3,
            "pare": 4,
            "velocidad": 5,
            "distancia": 6,
            "retroceso": 7,
            "ceder": 8,
            "cambio de carril": 9,
            "adelanta": 10,
            "estacionamiento": 11,
            "semáforo": 12,
            "embriaguez": 13,
            "falla": 14,
            "víctima": 15
        }
        
        # Recopilar todas las descripciones relevantes
        descripciones = []
        
        # De documentos
        for doc in documentos:
            if "texto" in doc:
                descripciones.append(doc["texto"].lower())
            if "entidades" in doc:
                for ent in doc.get("entidades", {}).get("vehiculos", []):
                    if ent.get("placa", "") == vehiculo.get("placa", ""):
                        descripciones.append(ent.get("version_doc", "").lower())
                        descripciones.append(ent.get("danos_descritos", "").lower())
        
        # Contar ocurrencias de pistas
        conteo_circunstancias = {i: 0 for i in range(1, 16)}
        
        for descripcion in descripciones:
            for pista, circunstancia in pistas_circunstancias.items():
                if pista in descripcion:
                    conteo_circunstancias[circunstancia] += 1
        
        # Determinar circunstancia más probable
        if max(conteo_circunstancias.values()) > 0:
            circunstancia = max(conteo_circunstancias, key=conteo_circunstancias.get)
        else:
            # Si no hay pistas claras, asignar una circunstancia aleatoria entre las más comunes
            circunstancias_comunes = [2, 4, 5, 6, 8, 12]  # Basado en estadísticas ficticias
            circunstancia = np.random.choice(circunstancias_comunes)
        
        logger.info(f"Circunstancia predicha por reglas simples: {circunstancia}")
        return circunstancia
    
    def _extraer_caracteristicas(
        self, 
        vehiculo: Dict[str, Any], 
        documentos: List[Dict[str, Any]], 
        evidencias: List[Dict[str, Any]]
    ) -> np.ndarray:
        """
        Extrae características para el modelo.
        
        Args:
            vehiculo (Dict[str, Any]): Datos del vehículo
            documentos (List[Dict[str, Any]]): Documentos procesados
            evidencias (List[Dict[str, Any]]): Evidencias procesadas
            
        Returns:
            np.ndarray: Vector de características
        """
        # En producción, implementaríamos una extracción de características sofisticada
        # Aquí simulamos un vector de características aleatorio
        return np.random.random(50)  # Vector de 50 características
    
    def _interpretar_codigo(
        self, 
        codigo: str, 
        circunstancia_a: int, 
        circunstancia_b: int
    ) -> Dict[str, Any]:
        """
        Interpreta el código de la matriz de responsabilidad.
        
        Args:
            codigo (str): Código de la matriz (A, B, C, NA, NRD)
            circunstancia_a (int): Circunstancia del vehículo A
            circunstancia_b (int): Circunstancia del vehículo B
            
        Returns:
            Dict[str, Any]: Resultado interpretado
        """
        # Descripción de circunstancias
        descripciones = {
            1: "Conduciendo en sentido contrario",
            2: "Invadiendo carril",
            3: "Haciendo giro indebido",
            4: "No respetando señal de pare",
            5: "Excediendo límite de velocidad",
            6: "No guardando distancia",
            7: "En retroceso",
            8: "No cediendo el paso",
            9: "Cambiando de carril",
            10: "Adelantamiento indebido",
            11: "Saliendo de estacionamiento",
            12: "No respetando semáforo",
            13: "Estado de embriaguez",
            14: "Falla mecánica",
            15: "Víctima de las circunstancias"
        }
        
        desc_a = descripciones.get(circunstancia_a, f"Circunstancia {circunstancia_a}")
        desc_b = descripciones.get(circunstancia_b, f"Circunstancia {circunstancia_b}")
        
        if codigo == "A":
            return {
                "responsable": "vehiculo_a",
                "porcentaje_a": 100,
                "porcentaje_b": 0,
                "justificacion": f"El vehículo A es responsable por: {desc_a}",
                "codigo_matriz": "A",
                "circunstancia_a": circunstancia_a,
                "circunstancia_b": circunstancia_b
            }
        elif codigo == "B":
            return {
                "responsable": "vehiculo_b",
                "porcentaje_a": 0,
                "porcentaje_b": 100,
                "justificacion": f"El vehículo B es responsable por: {desc_b}",
                "codigo_matriz": "B",
                "circunstancia_a": circunstancia_a,
                "circunstancia_b": circunstancia_b
            }
        elif codigo == "C":
            return {
                "responsable": "compartida",
                "porcentaje_a": 50,
                "porcentaje_b": 50,
                "justificacion": f"Responsabilidad compartida: Vehículo A ({desc_a}) y Vehículo B ({desc_b})",
                "codigo_matriz": "C",
                "circunstancia_a": circunstancia_a,
                "circunstancia_b": circunstancia_b
            }
        elif codigo == "NA":
            return {
                "responsable": "no_aplica",
                "mensaje": "No es posible determinar responsabilidad bajo estas circunstancias",
                "codigo_matriz": "NA",
                "circunstancia_a": circunstancia_a,
                "circunstancia_b": circunstancia_b
            }
        elif codigo == "NRD":
            return {
                "responsable": "indeterminado",
                "mensaje": "Se requiere información adicional para determinar responsabilidad",
                "codigo_matriz": "NRD",
                "circunstancia_a": circunstancia_a,
                "circunstancia_b": circunstancia_b
            }
        else:
            return {
                "responsable": "error",
                "mensaje": f"Código desconocido en la matriz: {codigo}",
                "codigo_matriz": codigo,
                "circunstancia_a": circunstancia_a,
                "circunstancia_b": circunstancia_b
            }