#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Implementación del algoritmo de negociación basado en teoría de juegos.
"""

from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)

class NegociadorResponsabilidad:
    """
    Implementa algoritmos de negociación para casos disputados.
    Utiliza técnicas de teoría de juegos y análisis histórico para
    proponer distribuciones de responsabilidad.
    """
    
    def __init__(self):
        """Inicializa el negociador de responsabilidad."""
        # Número máximo de iteraciones de negociación
        self.max_iteraciones = 5
        # Umbral de convergencia
        self.umbral_convergencia = 0.05  # 5%
        logger.info("Negociador de responsabilidad inicializado")
    
    def negociar(
        self, 
        circunstancia_a: int, 
        circunstancia_b: int,
        documentos: List[Dict[str, Any]],
        evidencias: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Ejecuta el algoritmo de negociación para determinar responsabilidad en caso de disputa.
        
        Args:
            circunstancia_a (int): Circunstancia del vehículo A
            circunstancia_b (int): Circunstancia del vehículo B
            documentos (List[Dict[str, Any]]): Documentos procesados
            evidencias (List[Dict[str, Any]]): Evidencias procesadas
            
        Returns:
            Dict[str, Any]: Resultado de la negociación
        """
        logger.info(f"Iniciando negociación para circunstancias: A={circunstancia_a}, B={circunstancia_b}")
        
        # Punto de partida: distribución inicial basada en pesos de circunstancias
        distribucion_actual = self._distribucion_inicial(
            circunstancia_a, 
            circunstancia_b
        )
        
        # Pesos de evidencias y documentos
        peso_evidencias = self._calcular_peso_evidencias(evidencias)
        peso_documentos = self._calcular_peso_documentos(documentos)
        
        # Proceso iterativo de negociación
        iteracion = 0
        while iteracion < self.max_iteraciones:
            distribucion_anterior = distribucion_actual.copy()
            
            # Ajustar distribución basada en evidencias
            distribucion_actual = self._ajustar_distribucion(
                distribucion_actual,
                peso_evidencias,
                peso_documentos
            )
            
            # Verificar convergencia
            if self._converge(distribucion_anterior, distribucion_actual):
                logger.info(f"Negociación convergió en iteración {iteracion}")
                break
                
            iteracion += 1
        
        # Construir resultado final
        if distribucion_actual["porcentaje_a"] >= 90:
            responsable = "vehiculo_a"
        elif distribucion_actual["porcentaje_b"] >= 90:
            responsable = "vehiculo_b"
        else:
            responsable = "compartida"
        
        resultado = {
            "responsable": responsable,
            "porcentaje_a": distribucion_actual["porcentaje_a"],
            "porcentaje_b": distribucion_actual["porcentaje_b"],
            "justificacion": self._generar_justificacion(
                distribucion_actual,
                circunstancia_a,
                circunstancia_b,
                peso_evidencias,
                peso_documentos
            ),
            "iteraciones": iteracion,
            "convergio": iteracion < self.max_iteraciones
        }
        
        logger.info(f"Negociación completada: {resultado['responsable']} (A={resultado['porcentaje_a']}%, B={resultado['porcentaje_b']}%)")
        return resultado
    
    def _distribucion_inicial(
        self, 
        circunstancia_a: int, 
        circunstancia_b: int
    ) -> Dict[str, float]:
        """
        Calcula la distribución inicial basada en pesos de circunstancias.
        
        Args:
            circunstancia_a (int): Circunstancia del vehículo A
            circunstancia_b (int): Circunstancia del vehículo B
            
        Returns:
            Dict[str, float]: Distribución inicial de responsabilidad
        """
        # Pesos de gravedad de cada circunstancia (ejemplo simplificado)
        pesos = {
            1: 9.5,  # Conduciendo en sentido contrario
            2: 8.0,  # Invadiendo carril
            3: 7.5,  # Haciendo giro indebido
            4: 9.0,  # No respetando señal de pare
            5: 8.5,  # Excediendo límite de velocidad
            6: 7.0,  # No guardando distancia
            7: 6.5,  # En retroceso
            8: 7.5,  # No cediendo el paso
            9: 6.0,  # Cambiando de carril
            10: 7.0, # Adelantamiento indebido
            11: 6.0, # Saliendo de estacionamiento
            12: 9.0, # No respetando semáforo
            13: 10.0, # Estado de embriaguez
            14: 5.0, # Falla mecánica
            15: 2.0  # Víctima de las circunstancias
        }
        
        peso_a = pesos.get(circunstancia_a, 5.0)
        peso_b = pesos.get(circunstancia_b, 5.0)
        
        # Distribución proporcional a la gravedad
        total_peso = peso_a + peso_b
        if total_peso > 0:
            porcentaje_a = round((peso_b / total_peso) * 100)
            porcentaje_b = round((peso_a / total_peso) * 100)
        else:
            porcentaje_a = 50
            porcentaje_b = 50
        
        # Ajustar para asegurar que suman 100%
        if porcentaje_a + porcentaje_b != 100:
            diferencia = 100 - (porcentaje_a + porcentaje_b)
            porcentaje_a += diferencia
        
        return {
            "porcentaje_a": porcentaje_a,
            "porcentaje_b": porcentaje_b
        }
    
    def _calcular_peso_evidencias(
        self, 
        evidencias: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calcula pesos basados en evidencias visuales.
        
        Args:
            evidencias (List[Dict[str, Any]]): Evidencias procesadas
            
        Returns:
            Dict[str, float]: Pesos de evidencias
        """
        # Implementación simplificada
        peso_a = 0.0
        peso_b = 0.0
        total_evidencias = 0
        
        for evidencia in evidencias:
            if not evidencia.get("procesada", False):
                continue
                
            total_evidencias += 1
            analisis = evidencia.get("analisis", {})
            
            # Dependiendo del análisis, ajustar pesos
            if "responsabilidad_sugerida" in analisis:
                if analisis["responsabilidad_sugerida"] == "vehiculo_a":
                    peso_b += analisis.get("confianza", 0.5)
                elif analisis["responsabilidad_sugerida"] == "vehiculo_b":
                    peso_a += analisis.get("confianza", 0.5)
                elif analisis["responsabilidad_sugerida"] == "compartida":
                    peso_a += analisis.get("confianza", 0.5) * 0.5
                    peso_b += analisis.get("confianza", 0.5) * 0.5
        
        if total_evidencias > 0:
            peso_a = peso_a / total_evidencias
            peso_b = peso_b / total_evidencias
        
        return {
            "peso_a": peso_a,
            "peso_b": peso_b,
            "total_evidencias": total_evidencias
        }
    
    def _calcular_peso_documentos(
        self, 
        documentos: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calcula pesos basados en documentos procesados.
        
        Args:
            documentos (List[Dict[str, Any]]): Documentos procesados
            
        Returns:
            Dict[str, float]: Pesos de documentos
        """
        # Implementación simplificada
        peso_a = 0.0
        peso_b = 0.0
        total_documentos = 0
        
        for documento in documentos:
            clasificacion = documento.get("clasificacion", {})
            confianza = clasificacion.get("confianza", 0.5)
            
            if confianza < 0.3:
                continue
                
            total_documentos += 1
            
            if "responsabilidad_sugerida" in clasificacion:
                if clasificacion["responsabilidad_sugerida"] == "vehiculo_a":
                    peso_b += confianza
                elif clasificacion["responsabilidad_sugerida"] == "vehiculo_b":
                    peso_a += confianza
                elif clasificacion["responsabilidad_sugerida"] == "compartida":
                    peso_a += confianza * 0.5
                    peso_b += confianza * 0.5
        
        if total_documentos > 0:
            peso_a = peso_a / total_documentos
            peso_b = peso_b / total_documentos
        
        return {
            "peso_a": peso_a,
            "peso_b": peso_b,
            "total_documentos": total_documentos
        }
    
    def _ajustar_distribucion(
        self, 
        distribucion: Dict[str, float],
        peso_evidencias: Dict[str, float],
        peso_documentos: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Ajusta la distribución basada en pesos de evidencias y documentos.
        
        Args:
            distribucion (Dict[str, float]): Distribución actual
            peso_evidencias (Dict[str, float]): Pesos de evidencias
            peso_documentos (Dict[str, float]): Pesos de documentos
            
        Returns:
            Dict[str, float]: Distribución ajustada
        """
        # Factores de influencia
        factor_evidencias = 0.3
        factor_documentos = 0.2
        factor_distribucion_actual = 1.0 - factor_evidencias - factor_documentos
        
        # Ajuste porcentual
        porcentaje_a = (
            distribucion["porcentaje_a"] * factor_distribucion_actual +
            peso_evidencias["peso_a"] * 100 * factor_evidencias +
            peso_documentos["peso_a"] * 100 * factor_documentos
        )
        
        porcentaje_b = (
            distribucion["porcentaje_b"] * factor_distribucion_actual +
            peso_evidencias["peso_b"] * 100 * factor_evidencias +
            peso_documentos["peso_b"] * 100 * factor_documentos
        )
        
        # Normalizar para asegurar que suman 100%
        total = porcentaje_a + porcentaje_b
        if total > 0:
            porcentaje_a = round((porcentaje_a / total) * 100)
            porcentaje_b = round((porcentaje_b / total) * 100)
        else:
            porcentaje_a = 50
            porcentaje_b = 50
        
        # Ajustar para asegurar que suman 100%
        if porcentaje_a + porcentaje_b != 100:
            diferencia = 100 - (porcentaje_a + porcentaje_b)
            porcentaje_a += diferencia
        
        return {
            "porcentaje_a": porcentaje_a,
            "porcentaje_b": porcentaje_b
        }
    
    def _converge(
        self, 
        anterior: Dict[str, float], 
        actual: Dict[str, float]
    ) -> bool:
        """
        Verifica si la negociación ha convergido.
        
        Args:
            anterior (Dict[str, float]): Distribución anterior
            actual (Dict[str, float]): Distribución actual
            
        Returns:
            bool: True si ha convergido
        """
        diferencia = abs(anterior["porcentaje_a"] - actual["porcentaje_a"])
        return diferencia <= self.umbral_convergencia
    
    def _generar_justificacion(
        self,
        distribucion: Dict[str, float],
        circunstancia_a: int,
        circunstancia_b: int,
        peso_evidencias: Dict[str, float],
        peso_documentos: Dict[str, float]
    ) -> str:
        """
        Genera una justificación textual para el resultado.
        
        Args:
            distribucion (Dict[str, float]): Distribución final
            circunstancia_a (int): Circunstancia del vehículo A
            circunstancia_b (int): Circunstancia del vehículo B
            peso_evidencias (Dict[str, float]): Pesos de evidencias
            peso_documentos (Dict[str, float]): Pesos de documentos
            
        Returns:
            str: Justificación del resultado
        """
        # Mapeo de circunstancias a descripciones (simplificado)
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
        
        # Crear justificación
        justificacion = f"Responsabilidad determinada mediante algoritmo de negociación. "
        
        if distribucion["porcentaje_a"] > distribucion["porcentaje_b"]:
            justificacion += f"El vehículo A tiene mayor responsabilidad ({distribucion['porcentaje_a']}%) "
            justificacion += f"por {desc_a}, mientras que el vehículo B tiene {distribucion['porcentaje_b']}% "
            justificacion += f"por {desc_b}."
        elif distribucion["porcentaje_b"] > distribucion["porcentaje_a"]:
            justificacion += f"El vehículo B tiene mayor responsabilidad ({distribucion['porcentaje_b']}%) "
            justificacion += f"por {desc_b}, mientras que el vehículo A tiene {distribucion['porcentaje_a']}% "
            justificacion += f"por {desc_a}."
        else:
            justificacion += f"Ambos vehículos comparten responsabilidad equitativamente (50% cada uno). "
            justificacion += f"El vehículo A por {desc_a} y el vehículo B por {desc_b}."
        
        # Añadir información sobre evidencias si hay suficientes
        if peso_evidencias["total_evidencias"] > 0:
            justificacion += f" El análisis se basó en {peso_evidencias['total_evidencias']} evidencias visuales"
            if peso_documentos["total_documentos"] > 0:
                justificacion += f" y {peso_documentos['total_documentos']} documentos."
            else:
                justificacion += "."
        elif peso_documentos["total_documentos"] > 0:
            justificacion += f" El análisis se basó en {peso_documentos['total_documentos']} documentos."
        
        return justificacion