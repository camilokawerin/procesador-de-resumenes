"""
Configuración para el procesador de resúmenes de tarjeta
"""
import os
from pathlib import Path

# Configuración de directorios
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Configuración de bancos
BANK_CONFIGS = {
    "Patagonia": {
        "folder": "input/VISA_Patagonia",
        "pattern": r"resumenTarjetaCredito\.(\d+\s+\w+\.\s+\d+)\.pdf",
        "date_format": "%d %b. %Y",
        "currency": "ARS",
        "processor": "patagonia",
        
        # Patrones de búsqueda específicos
        "saldo_patterns": [
            r'SALDO\s+ANTERIOR',
            r'SU\s+PAGO\s+EN\s+PESOS'
        ],
        "cargos_patterns": [
            r'COMIS\.\s+PROD\.\s+PAT',
            r'IVA\s+\$\s+21',
            r'INTERESES\s+FINANCIACION',
            r'IMP\s+DE\s+SELLOS'
        ],
        
        # Extracción de fecha de nombre de archivo
        # Formato: resumenTarjetaCredito.DD mmm. YYYY.pdf
        "filename_date_pattern": r'resumenTarjetaCredito\.(\d+)\s+(\w+)\.\s+(\d+)\.pdf',
        "filename_date_groups": {
            "day": 1,     # Grupo 1: día
            "month": 2,   # Grupo 2: mes (abreviado en español)
            "year": 3     # Grupo 3: año
        },
        "month_mapping": {
            'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04',
            'may': '05', 'jun': '06', 'jul': '07', 'ago': '08',
            'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'
        },
        
        # Formato de columnas fijas (posiciones en caracteres)
        "fixed_positions": {
            "fecha_start": 7,
            "fecha_end": 15,
            "comprobante_start": 20,
            "descripcion_start": 31,
            "min_amount_pos": 80,
            "min_line_length": 103,
            "max_line_length": 124
        },
        
        # Marcadores de inicio/fin de sección de movimientos
        "movement_section_start": [
            r'DETALLES? DE MOVIMIENTOS',
            r'Fecha\s+Comprobante'
        ],
        "movement_section_end": [
            r'DEBITAREMOS DE SU',
            r'Plan V:',
            r'CFTEA',
            r'Condiciones vigentes',
            r'Estimado Cliente'
        ]
    },
    
    "Galicia": {
        "folder": "input/VISA_Galicia",
        "pattern": r"RESUMEN_VISA.*\.pdf",
        "date_format": "%d/%m/%Y",
        "currency": "ARS",
        "processor": "galicia",
        
        # Extracción de fecha de nombre de archivo
        # Formato: RESUMEN_VISA29_5_2025pdf.pdf -> día_mes_año
        "filename_date_pattern": r'RESUMEN_VISA(\d+)_(\d+)_(\d+)pdf\.pdf',
        "filename_date_groups": {
            "day": 1,
            "month": 2,
            "year": 3
        },
        
        # Patrones de búsqueda específicos (TODO: ajustar según formato real)
        "saldo_patterns": [
            r'SALDO\s+ANTERIOR'
        ],
        "cargos_patterns": [
            r'CARGO\s+BANCARIO'
        ],
        
        # Formato de columnas (TODO: ajustar según formato real)
        "fixed_positions": {
            "fecha_start": 0,
            "fecha_end": 10
        },
        
        # Marcadores de sección (TODO: ajustar según formato real)
        "movement_section_start": [
            r'MOVIMIENTOS'
        ],
        "movement_section_end": [
            r'RESUMEN'
        ]
    }
}

# Configuración de logging
LOG_LEVEL = "INFO"
LOG_FILE = OUTPUT_DIR / "procesamiento.log"

# Modo debug - muestra logs detallados del flujo de extracción
DEBUG_MODE = False  # Cambiar a True para ver logs detallados de BaseExtractor, TextBasedExtractor, etc.

# Configuración de fecha
DATE_FORMATS = [
    "%d/%m/%Y",
    "%d-%m-%Y", 
    "%d %b %Y",
    "%d %B %Y",
    "%Y-%m-%d"
]

# Diccionario de meses en español a inglés para parsing de fechas
MESES_ES = {
    'ene': 'jan', 'enero': 'january',
    'feb': 'feb', 'febrero': 'february',
    'mar': 'mar', 'marzo': 'march',
    'abr': 'apr', 'abril': 'april',
    'may': 'may', 'mayo': 'may',
    'jun': 'jun', 'junio': 'june',
    'jul': 'jul', 'julio': 'july',
    'ago': 'aug', 'agosto': 'august',
    'sep': 'sep', 'septiembre': 'september',
    'oct': 'oct', 'octubre': 'october',
    'nov': 'nov', 'noviembre': 'november',
    'dic': 'dec', 'diciembre': 'december'
}