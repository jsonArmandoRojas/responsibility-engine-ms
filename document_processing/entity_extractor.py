#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para extracción de entidades relevantes en documentos de siniestros.
"""

from typing import Dict, List, Any, Optional
import re
import spacy
from spacy.language import Language
from document_processing.nlp_processor import NLPProcessor
from utils.logger import get_logger

logger = get_logger(__name__)

class EntityExtractor:
    """
    Extractor de entidades para documentos de siniestros.
    """
    
    def __init__(self, nlp_processor: Optional[NLPProcessor] = None):
        """
        Inicializa el extractor de entidades.
        
        Args:
            nlp_processor (Optional[NLPProcessor]): Procesador NLP a utilizar
        """
        self.nlp_processor = nlp_processor if nlp_processor else NLPProcessor()
        logger.info("EntityExtractor inicializado")
        
        # Patrones regulares para extracción
        self._init_patrones()
    
    def extraer_entidades(self, texto: str) -> Dict[str, Any]:
        """
        Extrae entidades relevantes de un texto.
        
        Args:
            texto (str): Texto del documento
            
        Returns:
            Dict[str, Any]: Entidades extraídas estructuradas
        """
        logger.info(f"Extrayendo entidades de texto ({len(texto)} caracteres)")
        
        # Procesar texto con NLP
        doc = self.nlp_processor.procesar(texto)
        
        # Extraer las diferentes entidades
        entidades = {
            "referencia_siniestro": self._extraer_referencia_siniestro(texto),
            "fecha": self._extraer_fecha(texto),
            "tipo_documento": self._determinar_tipo_documento(texto),
            "ubicacion": self._extraer_ubicacion(doc),
            "personas": self._extraer_personas(doc),
            "vehiculos": self._extraer_vehiculos(texto, doc),
            "danos": self._extraer_danos(doc),
            "descripcion_siniestro": self._extraer_descripcion_siniestro(doc),
            "confianza_extraccion": self._calcular_confianza(doc)
        }
        
        logger.info(f"Extracción completada: {len(entidades['vehiculos'])} vehículos, {len(entidades['personas'])} personas")
        return entidades
    
    def _init_patrones(self):
        """Inicializa patrones regulares para extracción de entidades."""
        # Patrones para referencias de siniestros
        self.patron_referencia = re.compile(r'(SIN|SINIESTRO|REF)[:\-\s]*(\d{4}[-\s]?\d{4}|\w{3}[-\s]?\d{4}[-\s]?\d{4})')
        
        # Patrones para fechas
        self.patron_fecha = re.compile(r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})')
        
        # Patrones para placas
        self.patron_placa = re.compile(r'\b([A-Z]{3}[\s\-]?\d{3})\b')
        
        # Patrones para otros identificadores
        # ...
    
    def _extraer_referencia_siniestro(self, texto: str) -> str:
        """Extrae referencia de siniestro."""
        match = self.patron_referencia.search(texto)
        if match:
            return match.group(2)
        return ""
    
    def _extraer_fecha(self, texto: str) -> str:
        """Extrae fecha del documento."""
        match = self.patron_fecha.search(texto)
        if match:
            dia, mes, anio = match.groups()
            # Normalizar año
            if len(anio) == 2:
                anio = "20" + anio
            return f"{anio}-{mes.zfill(2)}-{dia.zfill(2)}"
        return ""
    
    def _determinar_tipo_documento(self, texto: str) -> str:
        """Determina el tipo de documento."""
        texto_lower = texto.lower()
        
        if "informe policial" in texto_lower or "acta policial" in texto_lower:
            return "Informe Policial"
        elif "peritaje" in texto_lower:
            return "Peritaje"
        elif "declaración" in texto_lower:
            return "Declaración"
        elif "reclamo" in texto_lower:
            return "Formulario de Reclamo"
        else:
            return "Documento Siniestro"
    
    def _extraer_ubicacion(self, doc: Language) -> Dict[str, str]:
        """Extrae información de ubicación."""
        # Buscar entidades de tipo dirección y ubicación en spaCy
        direcciones = [ent.text for ent in doc.ents if ent.label_ in ["LOC", "FAC"]]
        
        # Buscar patrones de direcciones (Calle, Carrera, Avenida, etc.)
        patrones_direccion = ["calle", "carrera", "avenida", "diagonal", "transversal", "autopista"]
        
        ubicacion = {"direccion": "", "localidad": "", "ciudad": ""}
        
        for direccion in direcciones:
            dir_lower = direccion.lower()
            # Si contiene algún patrón de dirección, asumimos que es la dirección principal
            if any(patron in dir_lower for patron in patrones_direccion):
                ubicacion["direccion"] = direccion
            # Si no tiene un patrón de dirección, podría ser localidad o ciudad
            elif ubicacion["localidad"] == "":
                ubicacion["localidad"] = direccion
            elif ubicacion["ciudad"] == "":
                ubicacion["ciudad"] = direccion
        
        return ubicacion
    
    def _extraer_personas(self, doc: Language) -> List[Dict[str, str]]:
        """Extrae información de personas involucradas."""
        personas = []
        
        # Buscar entidades de tipo persona en spaCy
        for ent in doc.ents:
            if ent.label_ == "PER":
                # Buscar documentos de identidad cercanos
                documento = self._buscar_documento_cercano(doc, ent)
                
                # Buscar roles (conductor, propietario, testigo, etc.)
                rol = self._determinar_rol(doc, ent)
                
                personas.append({
                    "nombre": ent.text,
                    "documento": documento,
                    "rol": rol
                })
        
        return personas
    
    def _extraer_vehiculos(self, texto: str, doc: Language) -> List[Dict[str, Any]]:
        """Extrae información de vehículos."""
        vehiculos = []
        
        # Buscar placas
        placas = self.patron_placa.findall(texto)
        
        for placa in placas:
            # Buscar información del vehículo cerca de la placa
            marca, modelo = self._buscar_info_vehiculo(doc, placa)
            
            # Buscar conductor asociado
            conductor = self._buscar_conductor(doc, placa)
            
            # Buscar daños reportados
            danos = self._buscar_danos_vehiculo(doc, placa)
            
            vehiculos.append({
                "placa": placa,
                "marca": marca,
                "modelo": modelo,
                "conductor": conductor,
                "danos_descritos": danos
            })
        
        return vehiculos
    
    def _extraer_danos(self, doc: Language) -> List[Dict[str, Any]]:
        """Extrae descripciones de daños."""
        danos = []
        
        # Patrones para identificar textos que describen daños
        patrones_danos = ["daño", "abolladura", "impacto", "rotura", "colisión", "choque", "golpe"]
        
        for sent in doc.sents:
            sent_lower = sent.text.lower()
            if any(patron in sent_lower for patron in patrones_danos):
                # Determinar a qué vehículo corresponde el daño
                vehiculo = self._determinar_vehiculo_dano(sent)
                
                # Determinar severidad
                severidad = self._determinar_severidad_dano(sent)
                
                danos.append({
                    "descripcion": sent.text,
                    "vehiculo": vehiculo,
                    "severidad": severidad
                })
        
        return danos
    
    def _extraer_descripcion_siniestro(self, doc: Language) -> str:
        """Extrae la descripción general del siniestro."""
        # Buscar oraciones que describen el hecho
        patrones_descripcion = ["ocurrió", "sucedió", "aconteció", "accidente", "siniestro", "colisión"]
        
        descripciones = []
        for sent in doc.sents:
            sent_lower = sent.text.lower()
            if any(patron in sent_lower for patron in patrones_descripcion):
                descripciones.append(sent.text)
        
        if descripciones:
            return " ".join(descripciones)
        return ""
    
    def _calcular_confianza(self, doc: Language) -> float:
        """Calcula un score de confianza para la extracción."""
        # Implementación simplificada - en producción usaríamos métricas más complejas
        # Cuantas más entidades y patrones identificamos, mayor confianza
        num_ents = len(doc.ents)
        total_tokens = len(doc)
        
        if total_tokens == 0:
            return 0.0
        
        # Fórmula simple de confianza
        confianza = min(0.95, 0.5 + (num_ents / total_tokens) * 5)
        return round(confianza, 2)
    
    # Métodos auxiliares
    
    def _buscar_documento_cercano(self, doc: Language, ent) -> str:
        """Busca un documento de identidad cerca de una entidad persona."""
        # Simplificado - en producción usaríamos análisis de proximidad más sofisticado
        patron_cedula = re.compile(r'\b(cedula|c\.?c\.?|documento|dni|id)[\s\.:]*(\d{6,12})\b', re.IGNORECASE)
        
        # Buscar en el contexto (±20 tokens) de la entidad
        inicio = max(0, ent.start - 20)
        fin = min(len(doc), ent.end + 20)
        
        contexto = doc[inicio:fin].text
        match = patron_cedula.search(contexto)
        
        if match:
            return match.group(2)
        return ""
    
    def _determinar_rol(self, doc: Language, ent) -> str:
        """Determina el rol de una persona en el siniestro."""
        # Simplificado - en producción usaríamos análisis semántico más sofisticado
        patrones_roles = {
            "conductor": ["conductor", "manejaba", "conducía", "al volante"],
            "propietario": ["propietario", "dueño", "titular"],
            "testigo": ["testigo", "presenció", "observó", "vio"],
            "pasajero": ["pasajero", "acompañante"]
        }
        
        # Buscar en el contexto (±10 tokens) de la entidad
        inicio = max(0, ent.start - 10)
        fin = min(len(doc), ent.end + 10)
        
        contexto = doc[inicio:fin].text.lower()
        
        for rol, patrones in patrones_roles.items():
            if any(patron in contexto for patron in patrones):
                return rol
        
        return "implicado"
    
    def _buscar_info_vehiculo(self, doc: Language, placa: str) -> tuple:
        """Busca información de marca y modelo de un vehículo."""
        # Lista de marcas comunes
        marcas = ["Toyota", "Mazda", "Renault", "Chevrolet", "Ford", "Nissan", "Kia", "Hyundai"]
        
        # Buscar en el contexto de la placa
        for sent in doc.sents:
            if placa in sent.text:
                # Buscar marca
                marca = ""
                for m in marcas:
                    if m.lower() in sent.text.lower():
                        marca = m
                        break
                
                # Buscar modelo (patrón simple: número de 2-4 dígitos)
                modelo = ""
                modelo_match = re.search(r'\b(19|20)\d{2}\b|\b\d{2,4}\b', sent.text)
                if modelo_match:
                    modelo = modelo_match.group()
                
                return marca, modelo
        
        return "", ""
    
    def _buscar_conductor(self, doc: Language, placa: str) -> str:
        """Busca el conductor asociado a un vehículo por su placa."""
        # Implementación simplificada
        for sent in doc.sents:
            if placa in sent.text:
                for ent in sent.ents:
                    if ent.label_ == "PER":
                        # Verificar si hay patrones de conductor
                        contexto = sent.text.lower()
                        if any(p in contexto for p in ["conductor", "conducía", "manejaba"]):
                            return ent.text
        
        return ""
    
    def _buscar_danos_vehiculo(self, doc: Language, placa: str) -> str:
        """Busca descripciones de daños asociados a un vehículo."""
        # Patrones para identificar daños
        patrones_danos = ["daño", "abolladura", "impacto", "rotura", "colisión"]
        
        for sent in doc.sents:
            # Si la placa está en la oración o en oraciones adyacentes
            contexto = sent.text.lower()
            if placa in sent.text:
                # Buscar descripciones de daños
                if any(patron in contexto for patron in patrones_danos):
                    return sent.text
        
        return ""
    
    def _determinar_vehiculo_dano(self, sent) -> str:
        """Determina a qué vehículo corresponde una descripción de daño."""
        # Buscar placa en la oración
        texto = sent.text
        match = self.patron_placa.search(texto)
        
        if match:
            return match.group()
            
        # Si no hay placa, buscar referencias como "vehículo A" o "primer vehículo"
        patrones_vehiculo = {
            "vehiculo_a": ["vehículo a", "primer vehículo", "vehículo 1"],
            "vehiculo_b": ["vehículo b", "segundo vehículo", "vehículo 2"]
        }
        
        texto_lower = texto.lower()
        
        for vehiculo, patrones in patrones_vehiculo.items():
            if any(patron in texto_lower for patron in patrones):
                return vehiculo
        
        return "desconocido"
    
    def _determinar_severidad_dano(self, sent) -> str:
        """Determina la severidad del daño basado en el texto."""
        # Patrones para niveles de severidad
        patrones_severidad = {
            "leve": ["leve", "menor", "superficial", "pequeño"],
            "moderado": ["moderado", "medio", "parcial"],
            "grave": ["grave", "severo", "importante", "mayor", "total", "destrucción"]
        }
        
        texto_lower = sent.text.lower()
        
        for severidad, patrones in patrones_severidad.items():
            if any(patron in texto_lower for patron in patrones):
                return severidad
        
        return "no_especificado"