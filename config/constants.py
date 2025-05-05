#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Constantes utilizadas en la aplicación.
"""

# Estados de siniestro
ESTADO_REGISTRADO = "registrado"
ESTADO_PROCESANDO = "procesando"
ESTADO_PROCESADO = "procesado"
ESTADO_DISPUTADO = "disputado"
ESTADO_RESUELTO = "resuelto"
ESTADO_CANCELADO = "cancelado"

# Tipos de responsabilidad
RESP_VEHICULO_A = "vehiculo_a"
RESP_VEHICULO_B = "vehiculo_b"
RESP_COMPARTIDA = "compartida"
RESP_NO_APLICA = "no_aplica"
RESP_INDETERMINADO = "indeterminado"
RESP_ERROR = "error"

# Tipos de evidencia
EVIDENCIA_FOTO = "foto"
EVIDENCIA_VIDEO = "video"
EVIDENCIA_AUDIO = "audio"
EVIDENCIA_DOCUMENTO = "documento"
EVIDENCIA_OTRO = "otro"

# Tipos de documento
DOC_INFORME_POLICIAL = "Informe Policial"
DOC_PERITAJE = "Peritaje"
DOC_DECLARACION = "Declaración"
DOC_RECLAMO = "Formulario de Reclamo"
DOC_OTRO = "Otro"

# Descripciones de circunstancias
CIRCUNSTANCIAS = {
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

# Severidad de daños
SEVERIDAD_LEVE = "leve"
SEVERIDAD_MODERADO = "moderado"
SEVERIDAD_GRAVE = "grave"

# Tipos de cobertura
COBERTURA_PREMIUM = "premium"
COBERTURA_ESTANDAR = "estandar"
COBERTURA_BASICA = "basica"

# Rutas importantes
UPLOAD_FOLDER = "uploads"
PDF_FOLDER = f"{UPLOAD_FOLDER}/pdf"
IMAGEN_FOLDER = f"{UPLOAD_FOLDER}/imagenes"
ACTA_FOLDER = f"{UPLOAD_FOLDER}/actas"

# Límites y umbrales
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_ITERACIONES_NEGOCIACION = 5
UMBRAL_CONVERGENCIA_NEGOCIACION = 0.05  # 5%
UMBRAL_TIEMPO_EVIDENCIA = 300  # 5 minutos en segundos
UMBRAL_DISTANCIA_GEOLOCALIZACION = 0.1  # 100 metros en km