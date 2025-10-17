# Arquitectura de Extractores

## Diseño basado en Configuración + Herencia

Este módulo implementa un sistema extensible para procesar resúmenes de diferentes bancos, separando la **lógica común** de los **detalles específicos** de cada banco.

## Estructura

```
extractors/
├── base.py           # BaseExtractor - Lógica común
├── patagonia.py      # PatagoniaExtractor - Parsing específico
├── galicia.py        # GaliciaExtractor - Parsing específico
└── __init__.py
```

## Principios de Diseño

### 1. Configuración sobre Código Hardcoded

❌ **Antes (hardcoded):**
```python
def _extract_month_from_filename(self, filename: str):
    parts = filename.split('.')
    meses = {'ene': '01', 'feb': '02', ...}  # Hardcoded
    # Lógica específica de Patagonia hardcoded
```

✅ **Ahora (basado en configuración):**
```python
def _extract_month_from_filename(self, filename: str):
    pattern = self.config.get('filename_date_pattern')
    groups = self.config.get('filename_date_groups')
    mapping = self.config.get('month_mapping', {})
    # Lógica genérica que usa configuración
```

### 2. Separación de Responsabilidades

**BaseExtractor** (base.py):
- ✅ Extracción de texto del PDF
- ✅ Guardado de texto debug
- ✅ Extracción de montos genérica
- ✅ Validación de movimientos
- ✅ Eliminación de contrapartes
- ✅ **Extracción de fecha de archivo (genérico)**

**Extractores Específicos** (patagonia.py, galicia.py):
- ✅ Parsing de texto a movimientos
- ✅ Extracción de información de titular
- ✅ Detección de líneas de movimiento
- ✅ Parsing por posiciones fijas

### 3. Configuración en config.py

Cada banco tiene su configuración en `BANK_CONFIGS`:

```python
BANK_CONFIGS = {
    "Patagonia": {
        # Archivos y formatos
        "folder": "input/VISA_Patagonia",
        "pattern": r"resumenTarjetaCredito\.(\d+\s+\w+\.\s+\d+)\.pdf",
        "currency": "ARS",
        
        # Extracción de fecha del archivo
        "filename_date_pattern": r'resumenTarjetaCredito\.(\d+)\s+(\w+)\.\s+(\d+)\.pdf',
        "filename_date_groups": {
            "day": 1,
            "month": 2,
            "year": 3
        },
        "month_mapping": {
            'ene': '01', 'feb': '02', ...
        },
        
        # Posiciones de columnas fijas
        "fixed_positions": {
            "fecha_start": 7,
            "comprobante_start": 20,
            "descripcion_start": 31,
            "min_amount_pos": 80
        },
        
        # Patrones de búsqueda
        "saldo_patterns": [r'SALDO\s+ANTERIOR', ...],
        "cargos_patterns": [r'COMIS\.\s+PROD', ...],
        
        # Marcadores de secciones
        "movement_section_start": [r'DETALLE DE MOVIMIENTOS'],
        "movement_section_end": [r'DEBITAREMOS DE SU', ...]
    }
}
```

## Ejemplo: _extract_month_from_filename

Este método demuestra el patrón de diseño:

### Funcionamiento

1. **Lee configuración del banco:**
   ```python
   pattern = self.config.get('filename_date_pattern')
   groups_config = self.config.get('filename_date_groups')
   month_mapping = self.config.get('month_mapping', {})
   ```

2. **Aplica patrón regex genérico:**
   ```python
   match = re.search(pattern, filename)
   ```

3. **Extrae componentes según configuración:**
   ```python
   year = match.group(groups_config['year'])
   month = match.group(groups_config['month'])
   ```

4. **Aplica mapeo si es necesario:**
   ```python
   if month.lower() in month_mapping:
       month = month_mapping[month.lower()]
   ```

### Ejemplo con diferentes bancos

**Patagonia:**
- Archivo: `resumenTarjetaCredito.19 dic. 2024.pdf`
- Patrón: `r'resumenTarjetaCredito\.(\d+)\s+(\w+)\.\s+(\d+)\.pdf'`
- Grupos: `{day: 1, month: 2, year: 3}`
- Mapeo: `{'dic': '12'}`
- Resultado: `2024-12`

**Galicia:**
- Archivo: `resumen_2025_02.pdf`
- Patrón: `r'resumen_(\d{4})_(\d{2})\.pdf'`
- Grupos: `{year: 1, month: 2}`
- Mapeo: *(no necesario)*
- Resultado: `2025-02`

## Ventajas del Enfoque

### ✅ Extensibilidad
Agregar un nuevo banco solo requiere:
1. Agregar configuración en `BANK_CONFIGS`
2. Crear clase heredando de `BaseExtractor`
3. Implementar solo métodos específicos de parsing

### ✅ Mantenibilidad
- Cambios de formato → actualizar configuración
- Bugs en lógica común → fix una vez en BaseExtractor
- Testing → probar lógica genérica + configs específicas

### ✅ Claridad
- Configuración declarativa (fácil de leer)
- Lógica de negocio separada de detalles
- Menos duplicación de código

## Próximos Pasos

Para hacer otros métodos extensibles, seguir el mismo patrón:

1. **Identificar elementos específicos del banco:**
   - Posiciones de columnas
   - Patrones de texto
   - Formatos de datos

2. **Mover a configuración:**
   - Agregar keys en `BANK_CONFIGS`
   - Documentar qué representa cada valor

3. **Implementar lógica genérica:**
   - Leer de `self.config`
   - Aplicar configuración dinámicamente
   - Manejar casos edge con valores por defecto

4. **Probar con múltiples bancos:**
   - Verificar que funciona con configs existentes
   - Validar con configs nuevas

## Métodos Candidatos para Generalizar

- [ ] `_looks_like_movement()` - usar config de longitudes min/max
- [ ] `_parse_by_fixed_positions()` - usar `fixed_positions` config
- [ ] Detección de secciones - usar `movement_section_start/end`
- [ ] Extracción de titular - patron configurable
- [ ] Parsing de montos - formato por banco

## Testing

Ejecutar tests de validación:
```bash
# Test con implementación nueva (basada en config)
python test_patagonia.py

# Test con implementación de control
python test_patagonia_ok.py

# Demostración de configuración
python test_extractor_config.py
```

Ambos tests deben producir resultados idénticos (validación $0.00 diferencia).
