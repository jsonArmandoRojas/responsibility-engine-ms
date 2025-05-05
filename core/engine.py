#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Motor principal que coordina el procesamiento de siniestros.
"""

from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from uuid import uuid4

from core.rules import MatrizResponsabilidad
from core.negotiation import NegociadorResponsabilidad
from core.calculator import CalculadorIndemnizacion
from document_processing.pdf_reader import PDFReader
from document_processing.ocr import OCREngine
from document_processing.nlp_processor import NLPProcessor
from document_processing.entity_extractor import EntityExtractor
from ai.vision.damage_detector import DamageDetector
from ai.vision.image_validator import ImageValidator
from ai.nlp.text_classifier import TextClassifier
from ai.ml.responsibility_model import ResponsibilityModel
from data.database import Database
from utils.logger import get_logger

logger = get_logger(__name__)

class MotorPrincipal:
    """
    Clase principal que coordina todos los componentes del motor de responsabilidad.
    """
    
    def __init__(self):
        # Inicialización de componentes
        self.db = Database()
        self.pdf_reader = PDFReader()
        self.ocr_engine = OCREngine()
        self.nlp_processor = NLPProcessor()
        self.entity_extractor = EntityExtractor()
        self.damage_detector = DamageDetector()
        self.image_validator = ImageValidator()
        self.text_classifier = TextClassifier()
        self.responsibility_model = ResponsibilityModel()
        self.matriz_responsabilidad = MatrizResponsabilidad()
        self.negociador = NegociadorResponsabilidad()
        self.calculador = CalculadorIndemnizacion()
        
        logger.info("Motor de Responsabilidad inicializado correctamente")
        
    def procesar_siniestro(self, datos_siniestro: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa un siniestro completo desde los datos iniciales hasta la determinación
        de responsabilidad y cálculo de indemnización.
        
        Args:
            datos_siniestro (Dict[str, Any]): Datos completos del siniestro
            
        Returns:
            Dict[str, Any]: Resultado del procesamiento con responsabilidad e indemnización
        """
        logger.info(f"Iniciando procesamiento de siniestro: {datos_siniestro.get('id', uuid4())}")
        
        try:
            # 1. Registrar siniestro en la base de datos
            siniestro_id = self.db.registrar_siniestro(datos_siniestro)
            
            # 2. Procesar documentos si existen
            documentos_procesados = []
            for doc in datos_siniestro.get("documentos", []):
                try:
                    doc_procesado = self._procesar_documento(doc)
                    documentos_procesados.append(doc_procesado)
                except Exception as e:
                    logger.error(f"Error al procesar documento {doc.get('id')}: {str(e)}")
            
            # 3. Procesar evidencias visuales (fotos, videos)
            evidencias_procesadas = []
            for evidencia in datos_siniestro.get("evidencias", []):
                try:
                    evidencia_procesada = self._procesar_evidencia(evidencia)
                    evidencias_procesadas.append(evidencia_procesada)
                except Exception as e:
                    logger.error(f"Error al procesar evidencia {evidencia.get('id')}: {str(e)}")
            
            # 4. Determinar circunstancias de cada vehículo
            circunstancia_a = self._determinar_circunstancia(
                datos_siniestro.get("vehiculo_a", {}),
                documentos_procesados,
                evidencias_procesadas
            )
            
            circunstancia_b = self._determinar_circunstancia(
                datos_siniestro.get("vehiculo_b", {}),
                documentos_procesados,
                evidencias_procesadas
            )
            
            # 5. Determinar responsabilidad según la matriz
            if datos_siniestro.get("disputa", False):
                # Si hay disputa, usar el negociador
                resultado_responsabilidad = self.negociador.negociar(
                    circunstancia_a,
                    circunstancia_b,
                    documentos_procesados,
                    evidencias_procesadas
                )
            else:
                # Usar la matriz directamente
                resultado_responsabilidad = self.matriz_responsabilidad.determinar_responsabilidad(
                    circunstancia_a,
                    circunstancia_b
                )
            
            # 6. Calcular indemnización si aplica
            indemnizacion = None
            if resultado_responsabilidad["responsable"] not in ["no_aplica", "indeterminado"]:
                indemnizacion = self.calculador.calcular_indemnizacion(
                    resultado_responsabilidad,
                    datos_siniestro.get("vehiculo_a", {}).get("poliza_info", {}),
                    datos_siniestro.get("vehiculo_b", {}).get("poliza_info", {}),
                    datos_siniestro.get("danos", {})
                )
            
            # 7. Generar acta digital si se solicita
            acta_url = None
            if datos_siniestro.get("generar_acta", True):
                acta_url = self._generar_acta(
                    siniestro_id,
                    datos_siniestro,
                    resultado_responsabilidad,
                    indemnizacion
                )
            
            # 8. Preparar y devolver resultado final
            resultado_final = {
                "id": siniestro_id,
                "fecha": datos_siniestro.get("fecha", datetime.now().isoformat()),
                "estado": "procesado",
                "vehiculo_a": datos_siniestro.get("vehiculo_a", {}),
                "vehiculo_b": datos_siniestro.get("vehiculo_b", {}),
                "responsabilidad": resultado_responsabilidad,
                "indemnizacion": indemnizacion,
                "acta_url": acta_url,
                "creado_en": datetime.now().isoformat(),
            }
            
            # 9. Actualizar en la base de datos
            self.db.actualizar_siniestro(siniestro_id, resultado_final)
            
            logger.info(f"Procesamiento de siniestro completado: {siniestro_id}")
            return resultado_final
            
        except Exception as e:
            logger.error(f"Error en el procesamiento del siniestro: {str(e)}")
            raise
    
    def _procesar_documento(self, documento: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa un documento y extrae información relevante."""
        documento_id = documento.get("id", str(uuid4()))
        ruta = documento.get("ruta", "")
        tipo = documento.get("tipo", "desconocido")
        
        logger.info(f"Procesando documento {documento_id} de tipo {tipo}")
        
        # Extraer texto del documento
        if tipo in ["pdf", "documento"]:
            texto = self.pdf_reader.extraer_texto(ruta)
            
            # Si es necesario OCR
            if not texto or len(texto) < 100:
                texto = self.ocr_engine.procesar_documento(ruta)
        else:
            texto = self.ocr_engine.procesar_documento(ruta)
        
        # Procesar texto con NLP
        texto_procesado = self.nlp_processor.procesar(texto)
        
        # Extraer entidades
        entidades = self.entity_extractor.extraer_entidades(texto_procesado)
        
        # Clasificar texto
        clasificacion = self.text_classifier.clasificar(texto_procesado)
        
        return {
            "id": documento_id,
            "tipo": tipo,
            "texto": texto,
            "entidades": entidades,
            "clasificacion": clasificacion,
            "confianza": clasificacion.get("confianza", 0)
        }
    
    def _procesar_evidencia(self, evidencia: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa una evidencia visual y extrae información relevante."""
        evidencia_id = evidencia.get("id", str(uuid4()))
        ruta = evidencia.get("ruta", "")
        tipo = evidencia.get("tipo", "desconocido")
        
        logger.info(f"Procesando evidencia {evidencia_id} de tipo {tipo}")
        
        # Validar la evidencia
        validacion = self.image_validator.validar(
            ruta,
            evidencia.get("timestamp"),
            evidencia.get("geolocalizacion")
        )
        
        if not validacion["valida"]:
            logger.warning(f"Evidencia {evidencia_id} no válida: {validacion['mensaje']}")
            return {
                "id": evidencia_id,
                "tipo": tipo,
                "validacion": validacion,
                "procesada": False
            }
        
        # Detectar daños en la imagen si es una foto
        analisis = {}
        if tipo == "foto":
            analisis = self.damage_detector.detectar_danos(ruta)
        
        return {
            "id": evidencia_id,
            "tipo": tipo,
            "validacion": validacion,
            "procesada": True,
            "analisis": analisis
        }
    
    def _determinar_circunstancia(
        self, 
        vehiculo: Dict[str, Any], 
        documentos: List[Dict[str, Any]], 
        evidencias: List[Dict[str, Any]]
    ) -> int:
        """
        Determina la circunstancia aplicable a un vehículo según la matriz de responsabilidad.
        
        Args:
            vehiculo: Datos del vehículo
            documentos: Documentos procesados
            evidencias: Evidencias procesadas
            
        Returns:
            int: Número de circunstancia (1-15)
        """
        # Usar el modelo de ML para predecir la circunstancia
        circunstancia = self.responsibility_model.predecir_circunstancia(
            vehiculo, documentos, evidencias
        )
        
        return circunstancia
    
    def _generar_acta(
        self, 
        siniestro_id: str, 
        datos_siniestro: Dict[str, Any],
        responsabilidad: Dict[str, Any],
        indemnizacion: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Genera un acta digital para el siniestro procesado.
        
        Returns:
            str: URL del acta generada
        """
        # Generar acta (implementación simulada)
        return f"/actas/{siniestro_id}.pdf"