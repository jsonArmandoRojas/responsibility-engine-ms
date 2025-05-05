import os
import json
import logging
import datetime
from typing import Dict, List, Any, Optional

def configurar_logging(level=logging.INFO, log_file="motor_responsabilidad.log"):
    """
    Configura el sistema de logging
    
    Args:
        level: Nivel de logging
        log_file: Archivo donde guardar los logs
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Crear directorio para logs si no existe
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def cargar_json(ruta: str) -> Optional[Dict[str, Any]]:
    """
    Carga un archivo JSON
    
    Args:
        ruta: Ruta al archivo JSON
        
    Returns:
        Contenido del JSON o None si hay error
    """
    try:
        if not os.path.exists(ruta):
            return None
            
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    except Exception as e:
        logging.error(f"Error al cargar JSON {ruta}: {e}")
        return None

def guardar_json(datos: Dict[str, Any], ruta: str) -> bool:
    """
    Guarda datos en un archivo JSON
    
    Args:
        datos: Datos a guardar
        ruta: Ruta donde guardar
        
    Returns:
        True si se guardó correctamente, False en caso contrario
    """
    try:
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
            
        return True
        
    except Exception as e:
        logging.error(f"Error al guardar JSON {ruta}: {e}")
        return False

def validar_json_schema(datos: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """
    Valida un JSON contra un schema
    
    Args:
        datos: Datos a validar
        schema: Schema de validación
        
    Returns:
        Lista de errores encontrados (vacía si es válido)
    """
    # En una implementación real, aquí usaríamos jsonschema o similar
    # Para el ejemplo, devolvemos una lista vacía (todo válido)
    return []

def generar_id(prefijo: str = "") -> str:
    """
    Genera un ID único basado en timestamp
    
    Args:
        prefijo: Prefijo para el ID
        
    Returns:
        ID generado
    """
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    return f"{prefijo}{timestamp}"

def calcular_hash_archivo(ruta: str) -> Optional[str]:
    """
    Calcula el hash SHA-256 de un archivo
    
    Args:
        ruta: Ruta al archivo
        
    Returns:
        Hash SHA-256 o None si hay error
    """
    try:
        import hashlib
        
        if not os.path.exists(ruta):
            return None
            
        hasher = hashlib.sha256()
        
        with open(ruta, 'rb') as f:
            # Leer por bloques para archivos grandes
            for bloque in iter(lambda: f.read(4096), b''):
                hasher.update(bloque)
                
        return hasher.hexdigest()
        
    except Exception as e:
        logging.error(f"Error al calcular hash de {ruta}: {e}")
        return None

def extraer_extension(ruta: str) -> str:
    """
    Extrae la extensión de un archivo
    
    Args:
        ruta: Ruta al archivo
        
    Returns:
        Extensión del archivo (sin punto)
    """
    return os.path.splitext(ruta)[1].lstrip('.').lower()

def es_imagen(ruta: str) -> bool:
    """
    Determina si un archivo es una imagen basado en su extensión
    
    Args:
        ruta: Ruta al archivo
        
    Returns:
        True si es imagen, False en caso contrario
    """
    extensiones_imagen = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp']
    return extraer_extension(ruta) in extensiones_imagen

def es_documento(ruta: str) -> bool:
    """
    Determina si un archivo es un documento basado en su extensión
    
    Args:
        ruta: Ruta al archivo
        
    Returns:
        True si es documento, False en caso contrario
    """
    extensiones_documento = ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt']
    return extraer_extension(ruta) in extensiones_documento