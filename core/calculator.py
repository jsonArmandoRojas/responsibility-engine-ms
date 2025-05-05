#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Implementación del cálculo de indemnizaciones.
"""

from typing import Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class CalculadorIndemnizacion:
    """
    Implementa el cálculo de indemnizaciones basado en responsabilidad,
    daños y condiciones de pólizas.
    """
    
    def __init__(self):
        """Inicializa el calculador de indemnizaciones."""
        logger.info("Calculador de indemnizaciones inicializado")
    
    def calcular_indemnizacion(
        self,
        responsabilidad: Dict[str, Any],
        poliza_a: Dict[str, Any],
        poliza_b: Dict[str, Any],
        danos: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calcula la indemnización según la responsabilidad y daños.
        
        Args:
            responsabilidad (Dict[str, Any]): Resultado de responsabilidad
            poliza_a (Dict[str, Any]): Información de póliza del vehículo A
            poliza_b (Dict[str, Any]): Información de póliza del vehículo B
            danos (Dict[str, Any]): Información de daños
            
        Returns:
            Dict[str, Any]: Resultado del cálculo de indemnización
        """
        logger.info(f"Calculando indemnización para responsabilidad: {responsabilidad['responsable']}")
        
        # Extraer porcentajes de responsabilidad
        porcentaje_a = responsabilidad.get("porcentaje_a", 0)
        porcentaje_b = responsabilidad.get("porcentaje_b", 0)
        
        # Extraer montos de daños
        danos_a = danos.get("vehiculo_a", {}).get("monto", 0)
        danos_b = danos.get("vehiculo_b", {}).get("monto", 0)
        
        # Extraer factores de cobertura
        factor_cobertura_a = self._calcular_factor_cobertura(poliza_a)
        factor_cobertura_b = self._calcular_factor_cobertura(poliza_b)
        
        # Calcular indemnizaciones según la fórmula: Monto = (%Resp. × CostoRep.) × FactorCob.
        # Vehiculo A paga a B
        indemnizacion_a_b = (porcentaje_a / 100.0) * danos_b * factor_cobertura_a
        # Vehiculo B paga a A
        indemnizacion_b_a = (porcentaje_b / 100.0) * danos_a * factor_cobertura_b
        
        # Calcular deducibles
        deducible_a = self._calcular_deducible(poliza_a, indemnizacion_b_a)
        deducible_b = self._calcular_deducible(poliza_b, indemnizacion_a_b)
        
        # Aplicar deducibles
        indemnizacion_neta_a = max(0, indemnizacion_b_a - deducible_a)
        indemnizacion_neta_b = max(0, indemnizacion_a_b - deducible_b)
        
        # Preparar resultado
        resultado = {
            "indemnizaciones": [
                {
                    "pagador": "vehiculo_a",
                    "receptor": "vehiculo_b",
                    "monto_bruto": round(indemnizacion_a_b, 2),
                    "deducible": round(deducible_b, 2),
                    "monto_neto": round(indemnizacion_neta_b, 2),
                    "moneda": "COP",
                    "factor_cobertura": factor_cobertura_a
                },
                {
                    "pagador": "vehiculo_b",
                    "receptor": "vehiculo_a",
                    "monto_bruto": round(indemnizacion_b_a, 2),
                    "deducible": round(deducible_a, 2),
                    "monto_neto": round(indemnizacion_neta_a, 2),
                    "moneda": "COP",
                    "factor_cobertura": factor_cobertura_b
                }
            ],
            "resumen": {
                "total_danos_a": round(danos_a, 2),
                "total_danos_b": round(danos_b, 2),
                "porcentaje_responsabilidad_a": porcentaje_a,
                "porcentaje_responsabilidad_b": porcentaje_b
            }
        }
        
        logger.info(f"Indemnización calculada: A→B={indemnizacion_neta_b}, B→A={indemnizacion_neta_a}")
        return resultado
    
    def _calcular_factor_cobertura(self, poliza: Dict[str, Any]) -> float:
        """
        Calcula el factor de cobertura según la póliza.
        
        Args:
            poliza (Dict[str, Any]): Información de la póliza
            
        Returns:
            float: Factor de cobertura (0.0 - 1.0)
        """
        # Implementación simplificada
        tipo_cobertura = poliza.get("tipo_cobertura", "basica")
        
        if tipo_cobertura == "premium":
            return 1.0
        elif tipo_cobertura == "estandar":
            return 0.9
        elif tipo_cobertura == "basica":
            return 0.8
        else:
            return 0.7
    
    def _calcular_deducible(self, poliza: Dict[str, Any], monto: float) -> float:
        """
        Calcula el deducible aplicable.
        
        Args:
            poliza (Dict[str, Any]): Información de la póliza
            monto (float): Monto de indemnización
            
        Returns:
            float: Deducible aplicable
        """
        # Implementación simplificada
        deducible_porcentaje = poliza.get("deducible_porcentaje", 0)
        deducible_minimo = poliza.get("deducible_minimo", 0)
        
        deducible_calculado = monto * (deducible_porcentaje / 100.0)
        return max(deducible_calculado, deducible_minimo)