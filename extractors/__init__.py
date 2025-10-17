"""
Módulo de extractores para diferentes bancos
"""
from .patagonia import PatagoniaExtractor

# Registro de extractores disponibles
EXTRACTORS = {
    'patagonia': PatagoniaExtractor,
    # Agregar más extractores aquí según sea necesario
    # 'santander': SantanderExtractor,
    # 'galicia': GaliciaExtractor,
}

def get_extractor(bank_name: str):
    """
    Obtiene el extractor correspondiente para un banco
    """
    extractor_class = EXTRACTORS.get(bank_name.lower())
    if extractor_class:
        return extractor_class()
    else:
        raise ValueError(f"No hay extractor disponible para el banco: {bank_name}")