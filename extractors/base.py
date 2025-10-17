"""
Clase base para extractores de resúmenes de tarjeta de crédito
Proporciona funcionalidad común para todos los extractores específicos de bancos
"""
import re
import pdfplumber
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
import logging
from utils import parse_date, clean_description, debug_log, warning_log, extract_amount
from config import DEBUG_MODE

logger = logging.getLogger(__name__)

class BaseExtractor:
    """
    Clase base abstracta para extractores de resúmenes de tarjeta
    Define interfaz común y métodos compartidos
    """
    
    def __init__(self, bank_config: Dict):
        """
        Inicializa el extractor con configuración del banco
        
        Args:
            bank_config: Diccionario con configuración específica del banco
        """
        self.config = bank_config
        self.last_resumen_info = None
    
    def extract_movements(self, pdf_path: Path) -> List[Dict]:
        """
        Extrae movimientos del PDF
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Lista de diccionarios con movimientos extraídos
        """
        debug_log(f"🔵 [BaseExtractor.extract_movements] Iniciando extracción de: {pdf_path.name}")
        
        movements = self._extract_movements_from_file(pdf_path)
        
        debug_log(f"🔵 [BaseExtractor.extract_movements] Movimientos extraídos: {len(movements)}")
        
        # Asignar metadatos a todos los movimientos
        banco = self.config.get('processor', '').title()
        
        debug_log(f"🔵 [BaseExtractor.extract_movements] Asignando metadata - Banco: {banco}, Archivo: {pdf_path.name}")
        
        for movement in movements:
            movement['archivo_origen'] = pdf_path.name
            movement['banco'] = banco
        
        debug_log(f"🔵 [BaseExtractor.extract_movements] Finalizado - Total movimientos: {len(movements)}")
        
        return movements
    
    def _extract_movements_from_file(self, pdf_path: Path) -> List[Dict]:
        """
        Extrae movimientos del archivo PDF
        Debe ser implementado por cada subclase
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Lista de diccionarios con movimientos extraídos
        """
        raise NotImplementedError("Subclases deben implementar _extract_movements_from_file()")
    
    def _extract_pages_from_pdf(self, pdf_path: Path):
        """
        Extrae páginas del PDF
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Lista de páginas del PDF (pdfplumber pages)
        """
        debug_log(f"🔵 [BaseExtractor._extract_pages_from_pdf] Abriendo PDF: {pdf_path.name}")
        
        try:
            pdf = pdfplumber.open(pdf_path)
            
            debug_log(f"🔵 [BaseExtractor._extract_pages_from_pdf] PDF abierto exitosamente - Páginas: {len(pdf.pages)}")
            
            return pdf.pages
        except Exception as e:
            logger.error(f"❌ [BaseExtractor._extract_pages_from_pdf] Error abriendo PDF {pdf_path}: {e}")
            return []


class TextBasedExtractor(BaseExtractor):
    """
    Extractor basado en análisis de texto plano
    
    Estrategia:
    - Usa extract_text() para obtener texto completo del PDF
    - Parsea movimientos usando regex y posiciones fijas
    - Ideal para PDFs con formato consistente y predecible
    
    Ventajas:
    - Control preciso sobre parsing
    - Puede manejar formatos complejos
    - Acceso a espacios en blanco y posiciones
    
    Desventajas:
    - Más frágil ante cambios de formato
    - Requiere más mantenimiento
    """
    
    def _extract_movements_from_file(self, pdf_path: Path) -> List[Dict]:
        """
        Extrae movimientos del archivo PDF usando análisis de texto
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Lista de diccionarios con movimientos extraídos
        """
        debug_log(f"🟢 [TextBasedExtractor.extract_movements_from_file] Iniciando extracción basada en texto")
        
        pages = self._extract_pages_from_pdf(pdf_path)
        if not pages:
            warning_log(f"⚠️  [TextBasedExtractor.extract_movements_from_file] No se pudieron extraer páginas")
            return []
        
        full_text = self._extract_text_from_pages(pages)
        
        debug_log(f"🟢 [TextBasedExtractor.extract_movements_from_file] Texto extraído - Caracteres: {len(full_text)}")
        
        movements = self._extract_movements_from_text(full_text)
        
        debug_log(f"🟢 [TextBasedExtractor.extract_movements_from_file] Movimientos parseados del texto: {len(movements)}")
        
        return movements
    
    def _extract_text_from_pages(self, pages) -> str:
        """
        Extrae texto completo de todas las páginas del PDF
        
        Args:
            pages: Lista de páginas del PDF (pdfplumber pages)
            
        Returns:
            Texto completo extraído de todas las páginas
        """
        debug_log(f"🟢 [TextBasedExtractor._extract_text_from_pages] Extrayendo texto de {len(pages)} página(s)")
        
        # Extraer texto completo de todas las páginas
        full_text = ""
        for i, page in enumerate(pages, 1):
            page_text = page.extract_text(keep_blank_chars=True)
            if page_text:
                full_text += page_text
                debug_log(f"🟢 [TextBasedExtractor._extract_text_from_pages] Página {i}: {len(page_text)} caracteres")
        
        debug_log(f"🟢 [TextBasedExtractor._extract_text_from_pages] Texto total extraído: {len(full_text)} caracteres")
        
        return full_text
    
    def _extract_movements_from_text(self, text: str) -> List[Dict]:
        """
        Extrae todos los movimientos del texto
        """
        debug_log(f"🟢 [TextBasedExtractor._extract_movements_from_text] Parseando movimientos del texto")
        
        movements = []
        lines = text.split('\n')
        
        debug_log(f"🟢 [TextBasedExtractor._extract_movements_from_text] Total líneas: {len(lines)}")
        
        # Buscar sección de movimientos
        in_movement_section = False
        lines_processed = 0
        lines_parsed = 0
        
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            
            # Verificar si estamos entrando en una sección de movimientos
            if not in_movement_section:
                if "FECHA" in line and "COMPROBANTE" in line and "DETALLE" in line:
                    in_movement_section = True
                    debug_log(f"🟢 [TextBasedExtractor._extract_movements_from_text] ✅ Encontrada sección de movimientos en línea {i}")
                continue
            
            # Verificar si estamos saliendo de la sección de movimientos
            if in_movement_section:
                # Buscar texto que indica el final de los movimientos
                if ("DEBITAREMOS DE SU" in line or
                    "Plan V:" in line or 
                    "CFTEA" in line or 
                    "Condiciones vigentes" in line or
                    "Estimado Cliente" in line):
                    in_movement_section = False
                    debug_log(f"🟢 [TextBasedExtractor._extract_movements_from_text] ⛔ Fin de sección de movimientos en línea {i}")
                    continue
            
            # Solo procesar si estamos en sección de movimientos
            if in_movement_section:
                lines_processed += 1
                
                # Verificar si es una línea de resumen por titular
                titular_nombre = self._extract_titular_info(line)
                if titular_nombre:
                    # Crear pseudo-movimiento simplificado
                    pseudo_movement = {
                        'fecha': None,
                        'comprobante': "",
                        'descripcion': "",
                        'importe': 0,
                        'cuota': "",
                        'moneda': "",
                        'titular': titular_nombre
                    }
                    movements.append(pseudo_movement)
                    debug_log(f"🟢 [TextBasedExtractor._extract_movements_from_text] 👤 Titular encontrado: {titular_nombre}")
                    continue
                
                if self._looks_like_movement(line):
                    # Procesar directamente con posiciones fijas
                    parsed_movements = self._parse_by_fixed_positions(line)
                    
                    if parsed_movements:
                        movements.extend(parsed_movements)
                        lines_parsed += 1
        
        debug_log(f"🟢 [TextBasedExtractor._extract_movements_from_text] Líneas procesadas: {lines_processed}, Líneas parseadas: {lines_parsed}, Movimientos totales: {len(movements)}")
        
        return movements
    
    def _extract_titular_info(self, line: str) -> str:
        """
        Extrae solo el nombre del titular de las líneas de resumen.
        Formato esperado: "Tarjeta XXXX Total Consumos de NOMBRE APELLIDO     MONTO"
        """
        # Patrón para detectar líneas de resumen por titular
        if "Total Consumos de" in line and "Tarjeta" in line:
            # Extraer nombre (después de "Total Consumos de")
            nombre_match = re.search(r'Total\s+Consumos\s+de\s+(.+?)\s+([\d.,]+)', line)
            if nombre_match:
                return nombre_match.group(1).strip()
        
        return None
    
    def _looks_like_movement(self, line: str) -> bool:
        """
        Determina si una línea parece contener un movimiento usando dos criterios:
        1. Longitud entre 103-124 caracteres
        2. Contiene un monto al final (considerando líneas con dos montos)
        """
        # Criterio 1: Longitud de línea
        line_len = len(line)
        if line_len < 103 or line_len > 124:
            return False
        
        # Criterio 2: Monto al final (puede haber dos montos separados por espacios o guiones bajos)
        # Patrón para un monto: [\d]{1,3}(?:\.[\d]{3})*(?:,[\d]{2})?\-?
        # Permitir uno o dos montos al final de la línea, considerando guiones bajos como placeholder
        monto_pattern = r'[\d]{1,3}(?:\.[\d]{3})*(?:,[\d]{2})?\-?'
        has_amount = bool(re.search(rf'({monto_pattern}(?:\s+(?:{monto_pattern}|_))?)\s*_?\s*$', line))
        
        return has_amount
    
    def _parse_by_fixed_positions(self, line: str) -> List[Dict]:
        """
        Parsea una línea usando posiciones fijas exactas para cada columna.
        Extrae de derecha a izquierda: monto -> cuota -> descripción -> comprobante -> fecha
        
        Posiciones de inicio de columnas (con keep_blank_chars=True):
        - fecha: 7 (después de espacios iniciales)
        - comprobante: 21 (después de fecha + espacios)  
        - descripción: 31 (después del comprobante + espacios)
        - monto: alineado a la derecha (variable)
        """
        movements = []
        original_line = line
        
        # Verificar que la línea no esté vacía
        if not line or len(line.strip()) < 10:
            return movements
        
        # 1. Detectar monto(s) al final - puede haber uno o dos montos separados
        # Fijar posición mínima desde columna de cuotas (pos ~65) + extensión (~15) = pos 80
        min_amount_pos = 80
        
        # Patrón más específico para capturar líneas con dos montos desde posición mínima
        monto_doble_match = re.search(rf'([\d.,]+\-?)\s+([\d.,_]+\-?)\s*_?\s*$', line[min_amount_pos:])
        monto_simple_match = re.search(rf'([.\d,\-]+)\s*$', line[min_amount_pos:])
        
        monto_raw = None
        monto_start_pos = 0
        
        if monto_doble_match:
            # Línea con dos montos - usar el primer monto (principal)
            monto_raw = monto_doble_match.group(1)
            monto_start_pos = min_amount_pos + monto_doble_match.start()
        elif monto_simple_match:
            # Línea con un monto
            monto_raw = monto_simple_match.group(1)
            monto_start_pos = min_amount_pos + monto_simple_match.start()
        else:
            return movements
        
        # Detectar signo negativo
        is_negative = monto_raw.endswith('-')
        if is_negative:
            monto_raw = monto_raw[:-1]
        
        # Limpiar y validar formato de número argentino
        monto_clean = re.sub(r'[^\d,.]', '', monto_raw)
        if not re.match(r'^\d{1,3}(?:\.\d{3})*(?:,\d{2})?$', monto_clean):
            return movements
        
        monto_str = monto_clean + ('-' if is_negative else '')
        
        # Limpiar la línea eliminando el monto (modificar la misma variable line)
        line = line[:monto_start_pos].rstrip()
        
        # 2. Extraer cuota desde los últimos caracteres (búsqueda hacia atrás)
        cuota = ""
        cuota_match = re.search(r'\s+(?:Cuota\s+)?(\d{2}/\d{2})\s*$', line)
        if cuota_match:
            cuota = cuota_match.group(1)
            # Limpiar la línea eliminando la cuota encontrada
            line = line[:cuota_match.start()].rstrip()
        
        # 3. Extraer descripción desde posición 31
        descripcion = ""
        if len(line) > 31:
            descripcion = line[31:].strip()
            # Limpiar la línea eliminando la descripción
            line = line[:31].rstrip()
        
        # 4. Extraer comprobante desde posición 21  
        comprobante = ""
        if len(line) > 20:
            comprobante_substring = line[20:].strip()
            if comprobante_substring:
                # Buscar patrón de comprobante
                comprobante_match = re.match(r'^(\w+\*?[KX]?)', comprobante_substring)
                if comprobante_match:
                    comprobante = comprobante_match.group(1)
            # Limpiar la línea eliminando el comprobante
            line = line[:20].rstrip()
        
        # 5. Extraer fecha desde posición 7
        fecha_final = None
        if len(line) >= 15:  # 7 + 8 caracteres de fecha
            possible_fecha = line[7:15].strip()
            fecha_match = re.match(r'^(\d{2}\.\d{2}\.\d{2})$', possible_fecha)
            if fecha_match:
                fecha_str = fecha_match.group(1)
                try:
                    day, month, year = fecha_str.split('.')
                    year = f"20{year}" if len(year) == 2 else year
                    fecha_completa = f"{day}/{month}/{year}"
                    fecha_final = parse_date(fecha_completa, ["%d/%m/%Y"])
                except:
                    fecha_final = None
        
        # Procesar descripción - usar la extraída o toda la línea si no hay descripción
        descripcion_final = descripcion.strip() if descripcion else ""
        if not descripcion_final:
            descripcion_final = original_line[:monto_start_pos].strip()
        
        # Limpiar descripción usando la función de utils
        descripcion_final = clean_description(descripcion_final)
        
        # Procesar monto usando la función de utils
        importe_final = extract_amount(monto_str)
        
        # Crear movimiento directamente
        movement = {
            'fecha': fecha_final,
            'comprobante': comprobante if comprobante else "",
            'descripcion': descripcion_final,
            'importe': importe_final,
            'cuota': cuota if cuota else "",
            'moneda': 'ARS'
        }
        
        # Validar que tenga descripción e importe válidos
        if movement['descripcion'] and movement['importe'] is not None:
            movements.append(movement)
        
        return movements


class TableBasedExtractor(BaseExtractor):
    """
    Extractor basado en detección y extracción de tablas
    
    Estrategia:
    - Usa extract_tables() con líneas explícitas calculadas dinámicamente
    - Detecta estructura de tabla a partir de posiciones de palabras
    - Ideal para PDFs sin líneas de tabla visibles
    
    Ventajas:
    - Maneja bien PDFs multipágina con muchos movimientos
    - Más robusto ante variaciones en contenido
    - Estructura clara de columnas
    
    Desventajas:
    - Requiere calcular líneas de tabla dinámicamente
    - Necesita identificar header de tabla
    """
    
    def _extract_movements_from_file(self, pdf_path: Path) -> List[Dict]:
        """
        Extrae movimientos del archivo PDF usando extracción de tablas
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Lista de diccionarios con movimientos extraídos
        """
        debug_log(f"🟡 [TableBasedExtractor.extract_movements_from_file] Iniciando extracción basada en tablas")
        
        pages = self._extract_pages_from_pdf(pdf_path)
        if not pages:
            warning_log(f"⚠️  [TableBasedExtractor.extract_movements_from_file] No se pudieron extraer páginas")
            return []
        
        movements = self._extract_movements_from_tables(pages)
        
        debug_log(f"🟡 [TableBasedExtractor.extract_movements_from_file] Movimientos extraídos de tablas: {len(movements)}")
        
        return movements
    
    def _extract_movements_from_tables(self, pages) -> List[Dict]:
        """
        Extrae movimientos de tablas del PDF
        Debe ser implementado por cada banco específico
        
        Args:
            pages: Lista de páginas del PDF (pdfplumber pages)
            
        Returns:
            Lista de movimientos
        """
        raise NotImplementedError("Subclases deben implementar _extract_movements_from_tables()")
