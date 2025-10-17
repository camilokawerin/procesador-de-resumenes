"""
Utilidades para procesamiento de PDFs y fechas
"""
import re
import logging
from datetime import datetime
from typing import Optional, List
from config import MESES_ES, DATE_FORMATS, DEBUG_MODE

logger = logging.getLogger(__name__)

def debug_log(message: str):
    """
    Log condicional solo si DEBUG_MODE está activo
    
    Args:
        message: Mensaje a loguear
    """
    if DEBUG_MODE:
        logger.info(message)

def warning_log(message: str):
    """
    Log de warning condicional solo si DEBUG_MODE está activo
    
    Args:
        message: Mensaje de warning a loguear
    """
    if DEBUG_MODE:
        logger.warning(message)

def normalize_spanish_month(text: str) -> str:
    """Normaliza los meses en español a inglés para parsing"""
    text_lower = text.lower()
    for es_month, en_month in MESES_ES.items():
        text_lower = text_lower.replace(es_month, en_month)
    return text_lower

def parse_date(date_str: str, formats: List[str] = None) -> Optional[datetime]:
    """
    Intenta parsear una fecha usando varios formatos
    """
    if not date_str or not isinstance(date_str, str):
        return None
        
    date_str = date_str.strip()
    if not date_str:
        return None
    
    # Normalizar meses en español
    date_str = normalize_spanish_month(date_str)
    
    formats_to_try = formats or DATE_FORMATS
    
    for fmt in formats_to_try:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None

def extract_amount(amount_str: str) -> Optional[float]:
    """
    Extrae y convierte un monto a float
    Maneja formato argentino por defecto (punto como miles, coma como decimal)
    
    Args:
        amount_str: String con el monto a convertir
        
    Returns:
        Monto como float o None si no se puede convertir
    """
    if not amount_str:
        return None
    
    cleaned = amount_str.strip()
    
    # Verificar si es negativo
    is_negative = cleaned.endswith('-')
    if is_negative:
        cleaned = cleaned[:-1].strip()
    
    # Remover caracteres no numéricos excepto puntos y comas
    cleaned = re.sub(r'[^\d.,]', '', cleaned)
    
    if not cleaned:
        return None
    
    try:
        # Formato argentino: punto como miles, coma como decimal
        if '.' in cleaned and ',' in cleaned:
            cleaned = cleaned.replace('.', '').replace(',', '.')
        elif ',' in cleaned:
            parts = cleaned.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2:
                cleaned = cleaned.replace(',', '.')
            else:
                cleaned = cleaned.replace(',', '')
        elif '.' in cleaned:
            parts = cleaned.split('.')
            if len(parts) == 2 and len(parts[1]) <= 2 and len(parts[0]) <= 3:
                pass  # Ya está en formato correcto
            else:
                cleaned = cleaned.replace('.', '')
        
        amount = float(cleaned)
        return -amount if is_negative else amount
        
    except ValueError:
        return None

def clean_description(text: str) -> str:
    """
    Limpia la descripción de un movimiento
    """
    if not text:
        return ""
    
    # Remover múltiples espacios
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remover información de cuotas redundante al final
    text = re.sub(r'\s+Cuota\s+\d+/\d+\s*$', '', text)
    
    # Remover caracteres especiales innecesarios pero mantener * y otros importantes
    text = re.sub(r'[^\w\s\-\.\/*$%]', ' ', text)
    
    # Limpiar espacios nuevamente
    text = re.sub(r'\s+', ' ', text.strip())
    
    return text.strip()