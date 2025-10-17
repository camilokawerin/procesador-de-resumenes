"""
Extractor específico para PDFs de Banco Patagonia
Usa estrategia TextBasedExtractor con posiciones fijas
"""
import re
from typing import List, Dict, Optional
from pathlib import Path
import logging
from extractors.base import TextBasedExtractor
from utils import parse_date, clean_description, debug_log, warning_log

logger = logging.getLogger(__name__)

class PatagoniaExtractor(TextBasedExtractor):
    """
    Extractor para resúmenes de tarjeta de crédito del Banco Patagonia
    
    Estrategia: TextBasedExtractor
    - Analiza texto plano con posiciones fijas
    - Usa regex y slicing por columnas
    - Muy preciso para formato consistente de Patagonia
    """
    
    def __init__(self):
        """Inicializa el extractor con configuración de Patagonia"""
        from config import BANK_CONFIGS
        super().__init__(BANK_CONFIGS["Patagonia"])
    
    def extract(self, pdf_path: Path) -> List[Dict]:
        """
        Extrae y procesa movimientos del PDF de Patagonia
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Lista de diccionarios con movimientos extraídos y procesados
        """
        debug_log(f"🟣 [PatagoniaExtractor.extract] Iniciando procesamiento de: {pdf_path.name}")
        
        # Extraer movimientos usando el método heredado
        movements = self.extract_movements(pdf_path)
        
        debug_log(f"🟣 [PatagoniaExtractor.extract] Movimientos base extraídos: {len(movements)}")
        
        if not movements:
            warning_log(f"⚠️  [PatagoniaExtractor.extract] No se encontraron movimientos")
            return movements
        
        # Procesar movimientos extraídos
        resumen_info = {}
        filename = pdf_path.name
        saldo_actual = None
        pago_minimo = None
        
        # Extraer saldo anterior y eliminar movimientos relacionados
        debug_log(f"🟣 [PatagoniaExtractor.extract] Extrayendo saldo anterior...")
        
        saldo_anterior, movements = self._extract_saldo_anterior(movements)
        resumen_info['saldo_anterior'] = saldo_anterior
        
        debug_log(f"🟣 [PatagoniaExtractor.extract] Saldo anterior: ${saldo_anterior:,.2f}, Movimientos restantes: {len(movements)}")
        
        # Extraer cargos bancarios y eliminar movimientos relacionados
        debug_log(f"🟣 [PatagoniaExtractor.extract] Extrayendo cargos bancarios...")
        
        total_cargos, movements = self._extract_cargos_bancarios(movements)
        resumen_info['cargos_bancarios'] = total_cargos
        
        debug_log(f"🟣 [PatagoniaExtractor.extract] Cargos bancarios: ${total_cargos:,.2f}, Movimientos restantes: {len(movements)}")
        
        # Extraer información de saldos de los movimientos antes de eliminar contrapartes
        debug_log(f"🟣 [PatagoniaExtractor.extract] Extrayendo saldos y pago mínimo...")
        
        saldo_movements = []
        for i, mov in enumerate(movements):
            if 'SALDO ACTUAL' in mov['descripcion']:
                saldo_actual = mov['importe']
                saldo_movements.append(i)
                debug_log(f"🟣 [PatagoniaExtractor.extract] Saldo actual encontrado: ${saldo_actual:,.2f}")
            elif 'PAGO MINIMO' in mov['descripcion']:
                pago_minimo = mov['importe']
                saldo_movements.append(i)
                debug_log(f"🟣 [PatagoniaExtractor.extract] Pago mínimo encontrado: ${pago_minimo:,.2f}")
        
        # Eliminar movimientos de saldo y pago mínimo
        for i in reversed(saldo_movements):
            del movements[i]
        
        debug_log(f"🟣 [PatagoniaExtractor.extract] Movimientos tras eliminar saldos: {len(movements)}")
        
        # Asignar titulares usando la nueva lógica
        debug_log(f"🟣 [PatagoniaExtractor.extract] Asignando titulares...")
        
        movements = self._assign_titular_to_movements_advanced(movements)
        
        debug_log(f"🟣 [PatagoniaExtractor.extract] Titulares asignados - Movimientos finales: {len(movements)}")
        
        # Agregar información del resumen a los movimientos
        resumen_info['saldo_actual'] = saldo_actual
        resumen_info['pago_minimo'] = pago_minimo
        
        # Calcular totales por categoría para validación
        debug_log(f"🟣 [PatagoniaExtractor.extract] Calculando totales para validación...")
        
        total_consumos = sum(mov['importe'] for mov in movements if mov['importe'] > 0)
        bonificaciones = sum(mov['importe'] for mov in movements if mov['importe'] < 0)
        saldo_calculado = saldo_anterior + total_consumos + bonificaciones + total_cargos
        
        resumen_info['total_consumos'] = total_consumos
        resumen_info['bonificaciones'] = bonificaciones
        resumen_info['saldo_calculado'] = saldo_calculado
        
        # Validar saldo calculado vs saldo actual
        if saldo_actual is not None:
            diferencia = abs(saldo_calculado - saldo_actual)
            resumen_info['diferencia_validacion'] = diferencia
            resumen_info['validacion_ok'] = diferencia <= 1.0
            
            # Log de validación detallada
            logger.info(f"Validación de categorías en {filename}:")
            logger.info(f"  Saldo anterior: ${saldo_anterior:,.2f}")
            logger.info(f"  Total consumos: ${total_consumos:,.2f}")
            logger.info(f"  Bonificaciones: ${bonificaciones:,.2f}")
            logger.info(f"  Cargos bancarios: ${total_cargos:,.2f}")
            logger.info(f"  Saldo calculado: ${saldo_calculado:,.2f}")
            logger.info(f"  Saldo oficial: ${saldo_actual:,.2f}")
            logger.info(f"  Diferencia: ${diferencia:,.2f}")
            if resumen_info['validacion_ok']:
                logger.info("✅ Validación exitosa")
            else:
                logger.warning("⚠️ Diferencia significativa en validación")
        
        # Guardar información del resumen para acceso externo
        self.last_resumen_info = resumen_info.copy()
        
        return movements
    
    def _extract_saldo_anterior(self, movements: List[Dict]) -> tuple[float, List[Dict]]:
        """
        Extrae el saldo anterior del resumen y elimina los movimientos relacionados
        """
        saldo_anterior = 0.0
        indices_a_eliminar = []
        
        for i, mov in enumerate(movements):
            descripcion = mov.get('descripcion', '').upper()
            
            # Verificar si coincide con patrones de saldo
            for pattern in self.config['saldo_patterns']:
                if re.search(pattern, descripcion):
                    saldo_anterior += mov.get('importe', 0)
                    indices_a_eliminar.append(i)
                    break
        
        # Eliminar movimientos encontrados (en orden inverso para mantener índices)
        for i in reversed(indices_a_eliminar):
            del movements[i]
        
        return saldo_anterior, movements
    
    def _extract_cargos_bancarios(self, movements: List[Dict]) -> tuple[float, List[Dict]]:
        """
        Extrae los cargos bancarios del resumen y elimina los movimientos relacionados
        """
        total_cargos = 0.0
        indices_a_eliminar = []
        
        for i, mov in enumerate(movements):
            descripcion = mov.get('descripcion', '').upper()
            
            # Verificar si coincide con patrones de cargos bancarios
            for pattern in self.config['cargos_patterns']:
                if re.search(pattern, descripcion):
                    total_cargos += mov.get('importe', 0)
                    indices_a_eliminar.append(i)
                    break
        
        # Eliminar movimientos encontrados (en orden inverso para mantener índices)
        for i in reversed(indices_a_eliminar):
            del movements[i]
        
        return total_cargos, movements
    
    def _assign_titular_to_movements_advanced(self, movements: List[Dict]) -> List[Dict]:
        """
        Asigna información de titular a los movimientos usando la nueva lógica simplificada
        """
        titulares_data = []  # Array de titulares con rangos
        primer_movimiento = 0
        movements_to_remove = []  # Índices de pseudo-movimientos a eliminar
        ultimo_movimiento = 0
        
        # Primera pasada: identificar rangos de movimientos por titular
        for i, mov in enumerate(movements):
            # Combinar condiciones: si es pseudo-movimiento Y hay movimientos pendientes
            if mov.get('titular') and primer_movimiento < i:
                ultimo_movimiento = i - 1
                titulares_data.append({
                    'nombre': mov['titular'],
                    'primer_movimiento': primer_movimiento,
                    'ultimo_movimiento': ultimo_movimiento
                })
                primer_movimiento = i + 1
                
            # Marcar pseudo-movimiento para eliminar
            if mov.get('titular'):
                movements_to_remove.append(i)
                if primer_movimiento == i:  # Si es el primer pseudo-movimiento
                    primer_movimiento = i + 1
        
        # Segunda pasada: asignar titulares a movimientos (antes de eliminar pseudo-movimientos)
        for mov in movements:
            mov['titular'] = ""  # Inicializar todos vacíos
        
        for titular_data in titulares_data:
            nombre = titular_data['nombre']
            inicio = titular_data['primer_movimiento']
            fin = titular_data['ultimo_movimiento']
            
            for i in range(max(0, inicio), min(len(movements), fin + 1)):
                movements[i]['titular'] = nombre
        
        # Tercera pasada: eliminar pseudo-movimientos (conservando índices ya asignados)
        for i in reversed(movements_to_remove):
            del movements[i]
        
        return movements

