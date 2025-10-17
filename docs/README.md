# Documentación del Proyecto

Este directorio contiene toda la documentación técnica y guías del procesador de resúmenes bancarios.

## Estructura de Documentación

```
docs/
├── README.md          # Este archivo (índice principal)
└── referencias/       # Referencias técnicas detalladas
```

## Guía de Estilo

**Convenciones de nombres de archivo:**
- Usar `kebab-case` para todos los archivos Markdown (ej: `arquitectura-extractores.md`)
- Los nombres deben ser descriptivos y en español
- Usar guiones `-` para separar palabras

## 📚 Documentación Principal

- [README.md](../README.md) - Guía principal del proyecto
- [SECURITY.md](../SECURITY.md) - Guía de seguridad y manejo de datos sensibles
- [LICENSE](../LICENSE) - Licencia del proyecto

## 📖 Referencias Técnicas

- [referencias/](referencias/) - Documentación técnica detallada de componentes
  - [arquitectura-extractores.md](referencias/arquitectura-extractores.md) - Diseño basado en configuración + herencia

## 📂 Estructura de Directorios

- [input/README.md](../input/README.md) - Guía para organizar PDFs de entrada
- [output/README.md](../output/README.md) - Información sobre archivos generados
- [debug/README.md](../debug/README.md) - Información sobre archivos de debug

## ⚙️ Configuración

- [config.py](../config.py) - Configuración de bancos y patrones
- [utils.py](../utils.py) - Utilidades compartidas

## 🧪 Testing

- [tests/patagonia.py](../tests/patagonia.py) - Tests para Banco Patagonia
- [tests/galicia.py](../tests/galicia.py) - Tests para Banco Galicia
