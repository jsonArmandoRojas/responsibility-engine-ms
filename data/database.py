#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuración y manejo de base de datos.
"""

import os
from typing import Dict, List, Any, Optional, Union
import json
from datetime import datetime
import sqlite3
from utils.logger import get_logger

logger = get_logger(__name__)

class Database:
    """
    Clase para gestión de la base de datos.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Inicializa la conexión a la base de datos.
        
        Args:
            db_path (Optional[str]): Ruta a la base de datos SQLite
        """
        self.db_path = db_path or os.environ.get('DB_PATH', 'responsabilidad.db')
        self.conn = None
        
        # Inicializar base de datos
        self._init_db()
        
        logger.info(f"Base de datos inicializada: {self.db_path}")
    
    def _init_db(self):
        """Inicializa la estructura de la base de datos."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # Tabla de siniestros
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS siniestros (
                id TEXT PRIMARY KEY,
                fecha TEXT,
                estado TEXT,
                vehiculo_a_id TEXT,
                vehiculo_b_id TEXT,
                responsabilidad TEXT,
                indemnizacion TEXT,
                creado_en TEXT,
                actualizado_en TEXT,
                acta_url TEXT
            )
            ''')
            
            # Tabla de vehículos
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehiculos (
                id TEXT PRIMARY KEY,
                placa TEXT,
                marca TEXT,
                modelo TEXT,
                anio INTEGER,
                conductor TEXT,
                poliza_numero TEXT,
                aseguradora TEXT,
                datos_adicionales TEXT
            )
            ''')
            
            # Tabla de evidencias
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS evidencias (
                id TEXT PRIMARY KEY,
                siniestro_id TEXT,
                tipo TEXT,
                url TEXT,
                timestamp TEXT,
                geolocalizacion TEXT,
                hash TEXT,
                analisis TEXT,
                FOREIGN KEY (siniestro_id) REFERENCES siniestros (id)
            )
            ''')
            
            # Tabla de documentos
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS documentos (
                id TEXT PRIMARY KEY,
                siniestro_id TEXT,
                tipo TEXT,
                url TEXT,
                texto TEXT,
                entidades TEXT,
                clasificacion TEXT,
                FOREIGN KEY (siniestro_id) REFERENCES siniestros (id)
            )
            ''')
            
            self.conn.commit()
            
        except Exception as e:
            logger.error(f"Error al inicializar la base de datos: {str(e)}")
            if self.conn:
                self.conn.close()
            raise
    
    def registrar_siniestro(self, datos_siniestro: Dict[str, Any]) -> str:
        """
        Registra un nuevo siniestro en la base de datos.
        
        Args:
            datos_siniestro (Dict[str, Any]): Datos del siniestro
            
        Returns:
            str: ID del siniestro registrado
        """
        try:
            # Generar ID si no viene
            siniestro_id = datos_siniestro.get('id', self._generar_id())
            
            # Registrar vehículos
            vehiculo_a_id = self.registrar_vehiculo(datos_siniestro.get('vehiculo_a', {}))
            vehiculo_b_id = self.registrar_vehiculo(datos_siniestro.get('vehiculo_b', {}))
            
            # Fecha actual
            ahora = datetime.now().isoformat()
            
            # Registrar siniestro
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO siniestros (
                id, fecha, estado, vehiculo_a_id, vehiculo_b_id, 
                responsabilidad, indemnizacion, creado_en, actualizado_en, acta_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                siniestro_id,
                datos_siniestro.get('fecha', ahora),
                datos_siniestro.get('estado', 'registrado'),
                vehiculo_a_id,
                vehiculo_b_id,
                None,  # responsabilidad, se actualizará después
                None,  # indemnizacion, se actualizará después
                ahora,
                ahora,
                None   # acta_url, se actualizará después
            ))
            
            # Registrar evidencias
            for evidencia in datos_siniestro.get('evidencias', []):
                self.registrar_evidencia(siniestro_id, evidencia)
            
            # Registrar documentos
            for documento in datos_siniestro.get('documentos', []):
                self.registrar_documento(siniestro_id, documento)
            
            self.conn.commit()
            logger.info(f"Siniestro registrado: {siniestro_id}")
            
            return siniestro_id
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error al registrar siniestro: {str(e)}")
            raise
    
    def registrar_vehiculo(self, datos_vehiculo: Dict[str, Any]) -> str:
        """
        Registra un vehículo en la base de datos.
        
        Args:
            datos_vehiculo (Dict[str, Any]): Datos del vehículo
            
        Returns:
            str: ID del vehículo registrado
        """
        try:
            # Generar ID si no viene
            vehiculo_id = datos_vehiculo.get('id', self._generar_id())
            
            # Extraer datos adicionales que no tienen columna propia
            datos_extra = {k: v for k, v in datos_vehiculo.items() 
                          if k not in ['id', 'placa', 'marca', 'modelo', 'anio', 
                                      'conductor', 'poliza_numero', 'aseguradora']}
            
            # Registrar vehículo
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT OR REPLACE INTO vehiculos (
                id, placa, marca, modelo, anio, conductor, poliza_numero, 
                aseguradora, datos_adicionales
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                vehiculo_id,
                datos_vehiculo.get('placa', ''),
                datos_vehiculo.get('marca', ''),
                datos_vehiculo.get('modelo', ''),
                datos_vehiculo.get('anio', 0),
                datos_vehiculo.get('conductor', ''),
                datos_vehiculo.get('poliza_numero', ''),
                datos_vehiculo.get('aseguradora', ''),
                json.dumps(datos_extra)
            ))
            
            return vehiculo_id
            
        except Exception as e:
            logger.error(f"Error al registrar vehículo: {str(e)}")
            raise
    
    def registrar_evidencia(self, siniestro_id: str, datos_evidencia: Dict[str, Any]) -> str:
        """
        Registra una evidencia en la base de datos.
        
        Args:
            siniestro_id (str): ID del siniestro
            datos_evidencia (Dict[str, Any]): Datos de la evidencia
            
        Returns:
            str: ID de la evidencia registrada
        """
        try:
            # Generar ID si no viene
            evidencia_id = datos_evidencia.get('id', self._generar_id())
            
            # Registrar evidencia
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO evidencias (
                id, siniestro_id, tipo, url, timestamp, geolocalizacion, hash, analisis
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                evidencia_id,
                siniestro_id,
                datos_evidencia.get('tipo', ''),
                datos_evidencia.get('url', ''),
                datos_evidencia.get('timestamp', ''),
                json.dumps(datos_evidencia.get('geolocalizacion', {})),
                datos_evidencia.get('hash', ''),
                json.dumps(datos_evidencia.get('analisis', {}))
            ))
            
            return evidencia_id
            
        except Exception as e:
            logger.error(f"Error al registrar evidencia: {str(e)}")
            raise
    
    def registrar_documento(self, siniestro_id: str, datos_documento: Dict[str, Any]) -> str:
        """
        Registra un documento en la base de datos.
        
        Args:
            siniestro_id (str): ID del siniestro
            datos_documento (Dict[str, Any]): Datos del documento
            
        Returns:
            str: ID del documento registrado
        """
        try:
            # Generar ID si no viene
            documento_id = datos_documento.get('id', self._generar_id())
            
            # Registrar documento
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO documentos (
                id, siniestro_id, tipo, url, texto, entidades, clasificacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                documento_id,
                siniestro_id,
                datos_documento.get('tipo', ''),
                datos_documento.get('url', ''),
                datos_documento.get('texto', ''),
                json.dumps(datos_documento.get('entidades', {})),
                json.dumps(datos_documento.get('clasificacion', {}))
            ))
            
            return documento_id
            
        except Exception as e:
            logger.error(f"Error al registrar documento: {str(e)}")
            raise
    
    def actualizar_siniestro(self, siniestro_id: str, datos_actualizados: Dict[str, Any]) -> bool:
        """
        Actualiza los datos de un siniestro.
        
        Args:
            siniestro_id (str): ID del siniestro
            datos_actualizados (Dict[str, Any]): Datos actualizados
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            # Obtener datos actuales
            siniestro = self.obtener_siniestro(siniestro_id)
            if not siniestro:
                logger.error(f"No se encontró el siniestro: {siniestro_id}")
                return False
            
            # Actualizar campos
            cursor = self.conn.cursor()
            
            # Actualizar estado
            if 'estado' in datos_actualizados:
                cursor.execute('''
                UPDATE siniestros SET estado = ? WHERE id = ?
                ''', (datos_actualizados['estado'], siniestro_id))
            
            # Actualizar responsabilidad
            if 'responsabilidad' in datos_actualizados:
                cursor.execute('''
                UPDATE siniestros SET responsabilidad = ? WHERE id = ?
                ''', (json.dumps(datos_actualizados['responsabilidad']), siniestro_id))
            
            # Actualizar indemnización
            if 'indemnizacion' in datos_actualizados:
                cursor.execute('''
                UPDATE siniestros SET indemnizacion = ? WHERE id = ?
                ''', (json.dumps(datos_actualizados['indemnizacion']), siniestro_id))
            
            # Actualizar acta URL
            if 'acta_url' in datos_actualizados:
                cursor.execute('''
                UPDATE siniestros SET acta_url = ? WHERE id = ?
                ''', (datos_actualizados['acta_url'], siniestro_id))
            
            # Actualizar timestamp
            ahora = datetime.now().isoformat()
            cursor.execute('''
            UPDATE siniestros SET actualizado_en = ? WHERE id = ?
            ''', (ahora, siniestro_id))
            
            self.conn.commit()
            logger.info(f"Siniestro actualizado: {siniestro_id}")
            
            return True
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error al actualizar siniestro: {str(e)}")
            raise
    
    def obtener_siniestro(self, siniestro_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los datos de un siniestro por su ID.
        
        Args:
            siniestro_id (str): ID del siniestro
            
        Returns:
            Optional[Dict[str, Any]]: Datos del siniestro o None si no existe
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            SELECT * FROM siniestros WHERE id = ?
            ''', (siniestro_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Convertir a diccionario
            cols = [col[0] for col in cursor.description]
            siniestro = dict(zip(cols, row))
            
            # Deserializar campos JSON
            if siniestro['responsabilidad']:
                siniestro['responsabilidad'] = json.loads(siniestro['responsabilidad'])
            
            if siniestro['indemnizacion']:
                siniestro['indemnizacion'] = json.loads(siniestro['indemnizacion'])
            
            # Obtener vehículos
            siniestro['vehiculo_a'] = self.obtener_vehiculo(siniestro['vehiculo_a_id'])
            siniestro['vehiculo_b'] = self.obtener_vehiculo(siniestro['vehiculo_b_id'])
            
            # Obtener evidencias
            siniestro['evidencias'] = self.obtener_evidencias(siniestro_id)
            
            # Obtener documentos
            siniestro['documentos'] = self.obtener_documentos(siniestro_id)
            
            return siniestro
            
        except Exception as e:
            logger.error(f"Error al obtener siniestro: {str(e)}")
            return None
    
    def obtener_vehiculo(self, vehiculo_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los datos de un vehículo por su ID.
        
        Args:
            vehiculo_id (str): ID del vehículo
            
        Returns:
            Optional[Dict[str, Any]]: Datos del vehículo o None si no existe
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            SELECT * FROM vehiculos WHERE id = ?
            ''', (vehiculo_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Convertir a diccionario
            cols = [col[0] for col in cursor.description]
            vehiculo = dict(zip(cols, row))
            
            # Deserializar datos adicionales
            if vehiculo['datos_adicionales']:
                datos_adicionales = json.loads(vehiculo['datos_adicionales'])
                vehiculo.update(datos_adicionales)
                del vehiculo['datos_adicionales']
            
            return vehiculo
            
        except Exception as e:
            logger.error(f"Error al obtener vehículo: {str(e)}")
            return None
    
    def obtener_evidencias(self, siniestro_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene las evidencias de un siniestro.
        
        Args:
            siniestro_id (str): ID del siniestro
            
        Returns:
            List[Dict[str, Any]]: Lista de evidencias
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            SELECT * FROM evidencias WHERE siniestro_id = ?
            ''', (siniestro_id,))
            
            evidencias = []
            for row in cursor.fetchall():
                # Convertir a diccionario
                cols = [col[0] for col in cursor.description]
                evidencia = dict(zip(cols, row))
                
                # Deserializar campos JSON
                if evidencia['geolocalizacion']:
                    evidencia['geolocalizacion'] = json.loads(evidencia['geolocalizacion'])
                
                if evidencia['analisis']:
                    evidencia['analisis'] = json.loads(evidencia['analisis'])
                
                evidencias.append(evidencia)
            
            return evidencias
            
        except Exception as e:
            logger.error(f"Error al obtener evidencias: {str(e)}")
            return []
    
    def obtener_documentos(self, siniestro_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene los documentos de un siniestro.
        
        Args:
            siniestro_id (str): ID del siniestro
            
        Returns:
            List[Dict[str, Any]]: Lista de documentos
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            SELECT * FROM documentos WHERE siniestro_id = ?
            ''', (siniestro_id,))
            
            documentos = []
            for row in cursor.fetchall():
                # Convertir a diccionario
                cols = [col[0] for col in cursor.description]
                documento = dict(zip(cols, row))
                
                # Deserializar campos JSON
                if documento['entidades']:
                    documento['entidades'] = json.loads(documento['entidades'])
                
                if documento['clasificacion']:
                    documento['clasificacion'] = json.loads(documento['clasificacion'])
                
                documentos.append(documento)
            
            return documentos
            
        except Exception as e:
            logger.error(f"Error al obtener documentos: {str(e)}")
            return []
    
    def cerrar(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()
            logger.info("Conexión a base de datos cerrada")
    
    def _generar_id(self) -> str:
        """
        Genera un ID único.
        
        Returns:
            str: ID generado
        """
        import uuid
        return str(uuid.uuid4())