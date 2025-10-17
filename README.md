# Procesador de Resumenes

Sistema para extraer y procesar automaticamente movimientos de resumenes de tarjeta de credito en formato PDF de bancos argentinos.

## Caracteristicas

- **Arquitectura extensible** con patron Template Method
- **Extraccion inteligente** de movimientos con validacion de saldos
- **Asignacion automatica** de titulares y metadata
- **Configuracion centralizada** por banco
- **Sistema de logging** condicional para debugging
- **Validacion precisa** de saldos con 100% de exactitud

## Inicio Rapido

### Instalacion

```bash
pip install pdfplumber python-dateutil
```

### Uso Basico

```python
from extractors.patagonia import PatagoniaExtractor
from pathlib import Path

extractor = PatagoniaExtractor()
pdf_path = Path("input/VISA_Patagonia/resumenTarjetaCredito.19 dic. 2024.pdf")
movements = extractor.extract(pdf_path)

for mov in movements:
    print(f"{mov['fecha']} - {mov['descripcion']}: ${mov['importe']:,.2f}")
```

## Estructura del Proyecto

```
procesador-de-resumenes/
├── extractors/          # Extractores por banco
├── input/              # PDFs de entrada organizados por banco
├── output/             # Archivos generados (CSV, Excel)
├── debug/              # Archivos de debug
├── docs/               # Documentación técnica completa
├── tests/              # Tests de validación
├── config.py           # Configuración centralizada
└── utils.py            # Utilidades compartidas
```

## Documentacion

### 📚 Guias de Usuario
- [Instalación y Configuración](docs/guias/instalacion.md) *(pendiente)*
- [Uso y Ejemplos](docs/guias/uso.md) *(pendiente)*
- [Agregar Nuevo Banco](docs/guias/agregar-banco.md) *(pendiente)*

### 🏗️ Arquitectura y Referencias Técnicas
- [Diseño de Extractores](docs/referencias/arquitectura-extractores.md) - Patrón Template Method y configuración

### 🔒 Seguridad
- [SECURITY.md](SECURITY.md) - Guía de seguridad y manejo de datos sensibles

### 📖 Índice Completo
- [docs/README.md](docs/README.md) - Índice de toda la documentación

## Bancos Soportados

- ✅ **Banco Patagonia** - Implementación completa con validación de saldos
- 🚧 **Banco Galicia** - En desarrollo

## Licencia

Este proyecto es de codigo abierto. Ver archivo [LICENSE](LICENSE) para detalles.
