#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para procesamiento de lenguaje natural (NLP).
"""

from typing import Dict, List, Any, Optional
import spacy
from spacy.language import Language
import re
from utils.logger import get_logger

logger = get_logger(__name__)

class NLPProcessor:
    """
    Procesador de lenguaje natural para análisis de textos.
    """
    
    def __init__(self, modelo: str = "es_core_news_md"):
        """
        Inicializa el procesador NLP.
        
        Args:
            modelo (str): Modelo de spaCy a utilizar
        """
        try:
            self.nlp = spacy.load(modelo)
            logger.info(f"NLPProcessor inicializado con modelo: {modelo}")
        except OSError:
            logger.warning(f"Modelo {modelo} no encontrado. Descargando...")
            spacy.cli.download(modelo)
            self.nlp = spacy.load(modelo)
            logger.info(f"Modelo {modelo} descargado e inicializado")
    
    def procesar(self, texto: str) -> Language:
        """
        Procesa un texto y devuelve el documento spaCy.
        
        Args:
            texto (str): Texto a procesar
            
        Returns:
            Language: Documento spaCy procesado
        """
        # Limpiar texto
        texto_limpio = self._limpiar_texto(texto)
        
        # Procesar con spaCy
        doc = self.nlp(texto_limpio)
        
        logger.info(f"Texto procesado: {len(texto_limpio)} caracteres, {len(doc)} tokens")
        return doc
    
    def extraer_oraciones(self, texto: str) -> List[str]:
        """
        Extrae oraciones de un texto.
        
        Args:
            texto (str): Texto a procesar
            
        Returns:
            List[str]: Lista de oraciones
        """
        doc = self.procesar(texto)
        return [sent.text.strip() for sent in doc.sents]
    
    def extraer_palabras_clave(self, texto: str, min_freq: int = 2) -> Dict[str, int]:
        """
        Extrae palabras clave de un texto.
        
        Args:
            texto (str): Texto a procesar
            min_freq (int): Frecuencia mínima para considerar palabra clave
            
        Returns:
            Dict[str, int]: Diccionario con palabras clave y sus frecuencias
        """
        doc = self.procesar(texto)
        
        # Filtrar tokens relevantes (sustantivos, verbos, adjetivos)
        tokens = [token.lemma_.lower() for token in doc 
                if not token.is_stop and not token.is_punct
                and token.pos_ in ['NOUN', 'VERB', 'ADJ', 'PROPN']
                and len(token.text) > 2]
        
        # Contar frecuencias
        frecuencias = {}
        for token in tokens:
            frecuencias[token] = frecuencias.get(token, 0) + 1
        
        # Filtrar por frecuencia mínima
        keywords = {k: v for k, v in frecuencias.items() if v >= min_freq}
        
        logger.info(f"Extraídas {len(keywords)} palabras clave con frecuencia >= {min_freq}")
        return keywords
    
    def detectar_idioma(self, texto: str) -> str:
        """
        Detecta el idioma del texto.
        
        Args:
            texto (str): Texto a analizar
            
        Returns:
            str: Código de idioma detectado
        """
        try:
            from langdetect import detect
            return detect(texto)
        except:
            logger.warning("No se pudo detectar el idioma, asumiendo español")
            return "es"
    
    def analizar_sentimiento(self, texto: str) -> Dict[str, Any]:
        """
        Analiza el sentimiento del texto.
        
        Args:
            texto (str): Texto a analizar
            
        Returns:
            Dict[str, Any]: Resultado del análisis de sentimiento
        """
        # Implementación simplificada - en producción usaríamos un modelo específico
        doc = self.procesar(texto)
        
        # Palabras positivas y negativas (simplificado)
        positivas = ['bueno', 'excelente', 'positivo', 'favorable', 'adecuado', 'correcto']
        negativas = ['malo', 'terrible', 'negativo', 'desfavorable', 'inadecuado', 'incorrecto']
        
        # Contar ocurrencias
        pos_count = sum(1 for token in doc if token.lemma_.lower() in positivas)
        neg_count = sum(1 for token in doc if token.lemma_.lower() in negativas)
        
        # Determinar polaridad
        total = pos_count + neg_count
        if total == 0:
            polaridad = 0.0
        else:
            polaridad = (pos_count - neg_count) / total
        
        return {
            "polaridad": polaridad,
            "positivo": pos_count,
            "negativo": neg_count,
            "neutral": len(doc) - pos_count - neg_count
        }
    
    def _limpiar_texto(self, texto: str) -> str:
        """
        Limpia el texto eliminando caracteres innecesarios.
        
        Args:
            texto (str): Texto a limpiar
            
        Returns:
            str: Texto limpio
        """
        # Eliminar espacios múltiples
        texto = re.sub(r'\s+', ' ', texto)
        
        # Eliminar saltos de línea múltiples
        texto = re.sub(r'\n+', '\n', texto)
        
        # Otros patrones de limpieza específicos
        # ...
        
        return texto.strip()