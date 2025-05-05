#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Implementación de la matriz de responsabilidad y reglas de negocio.
"""

from typing import Dict, Any, List, Tuple
from utils.logger import get_logger

logger = get_logger(__name__)

class MatrizResponsabilidad:
    """
    Implementa la matriz de responsabilidad de 15x15 según el manual FASECOLDA.
    """
    
    def __init__(self):
        """Inicializa la matriz de responsabilidad con los 225 casos posibles."""
        # Cargar la matriz desde una constante o archivo de configuración
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
        
        # Mapeo de códigos a significados
        self.codigos = {
            "A": "responsable_vehiculo_a",
            "B": "responsable_vehiculo_b",
            "C": "responsabilidad_compartida",
            "NA": "no_aplica",
            "NRD": "no_se_puede_determinar"
        }
        
        logger.info("Matriz de responsabilidad inicializada con 225 situaciones")
    
    def determinar_responsabilidad(
        self, 
        circunstancia_a: int, 
        circunstancia_b: int
    ) -> Dict[str, Any]:
        """
        Determina la responsabilidad según las circunstancias de los vehículos.
        
        Args:
            circunstancia_a (int): Circunstancia del vehículo A (1-15)
            circunstancia_b (int): Circunstancia del vehículo B (1-15)
            
        Returns:
            Dict[str, Any]: Resultado de la determinación de responsabilidad
        """
        # Validar que las circunstancias estén en el rango correcto
        if not (1 <= circunstancia_a <= 15 and 1 <= circunstancia_b <= 15):
            logger.error(f"Circunstancias fuera de rango: A={circunstancia_a}, B={circunstancia_b}")
            return {
                "responsable": "error",
                "mensaje": "Las circunstancias deben estar entre 1 y 15"
            }
        
        # Ajustar índices (la matriz está 0-indexed, pero las circunstancias son 1-indexed)
        codigo = self.matriz[circunstancia_a - 1][circunstancia_b - 1]
        
        # Interpretar el código de la matriz
        resultado = self._interpretar_codigo(codigo, circunstancia_a, circunstancia_b)
        
        logger.info(f"Responsabilidad determinada: {resultado['responsable']} (A={circunstancia_a}, B={circunstancia_b})")
        return resultado
    
    def _interpretar_codigo(
        self, 
        codigo: str, 
        circunstancia_a: int, 
        circunstancia_b: int
    ) -> Dict[str, Any]:
        """
        Interpreta el código de la matriz y genera un resultado estructurado.
        
        Args:
            codigo (str): Código de la matriz (A, B, C, NA, NRD)
            circunstancia_a (int): Circunstancia del vehículo A
            circunstancia_b (int): Circunstancia del vehículo B
            
        Returns:
            Dict[str, Any]: Resultado estructurado
        """
        # Información de circunstancias
        info_circunstancias = self._obtener_info_circunstancias(circunstancia_a, circunstancia_b)
        
        if codigo == "A":
            return {
                "responsable": "vehiculo_a",
                "porcentaje_a": 100,
                "porcentaje_b": 0,
                "justificacion": f"El vehículo A es responsable por: {info_circunstancias[0]}",
                "codigo_matriz": "A"
            }
        elif codigo == "B":
            return {
                "responsable": "vehiculo_b",
                "porcentaje_a": 0,
                "porcentaje_b": 100,
                "justificacion": f"El vehículo B es responsable por: {info_circunstancias[1]}",
                "codigo_matriz": "B"
            }
        elif codigo == "C":
            return {
                "responsable": "compartida",
                "porcentaje_a": 50,
                "porcentaje_b": 50,
                "justificacion": f"Responsabilidad compartida: Vehículo A ({info_circunstancias[0]}) y Vehículo B ({info_circunstancias[1]})",
                "codigo_matriz": "C"
            }
        elif codigo == "NA":
            return {
                "responsable": "no_aplica",
                "mensaje": "No es posible determinar responsabilidad bajo estas circunstancias",
                "codigo_matriz": "NA"
            }
        elif codigo == "NRD":
            return {
                "responsable": "indeterminado",
                "mensaje": "Se requiere información adicional para determinar responsabilidad",
                "codigo_matriz": "NRD"
            }
        else:
            return {
                "responsable": "error",
                "mensaje": f"Código desconocido en la matriz: {codigo}",
                "codigo_matriz": codigo
            }
    
    def _obtener_info_circunstancias(
        self, 
        circunstancia_a: int, 
        circunstancia_b: int
    ) -> Tuple[str, str]:
        """
        Obtiene información descriptiva sobre las circunstancias.
        
        Args:
            circunstancia_a (int): Circunstancia del vehículo A
            circunstancia_b (int): Circunstancia del vehículo B
            
        Returns:
            Tuple[str, str]: Descripciones de las circunstancias
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
        
        return (
            descripciones.get(circunstancia_a, f"Circunstancia desconocida ({circunstancia_a})"),
            descripciones.get(circunstancia_b, f"Circunstancia desconocida ({circunstancia_b})")
        )