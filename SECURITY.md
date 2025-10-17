# Guía de Seguridad y Privacidad

## 🔒 Información Importante sobre Datos Personales

Este proyecto procesa **información financiera personal y sensible** de resúmenes bancarios que pueden incluir:

- Nombres completos de titulares de tarjetas
- Números de tarjeta (parciales o completos)
- Números de comprobante
- Detalles de transacciones y comercios
- Montos de compras
- Direcciones y datos de contacto

## ⚠️ Antes de Publicar o Compartir

### Archivos que NUNCA deben ser públicos

1. **PDFs originales** (`input/VISA_*/`)
2. **Archivos de salida** (`output/`)
3. **Archivos de debug** (`debug/text/`, `debug/resultados/`)
4. **Cualquier archivo .txt, .csv, .xlsx** generado

### Protección Automática

Este repositorio incluye un archivo `.gitignore` que excluye automáticamente:

```gitignore
# Archivos con datos personales
*.pdf
output/
debug/text/
debug/resultados/
*.csv
*.xlsx
*.txt
input/VISA_Patagonia/*.pdf
input/VISA_Galicia/*.pdf
```

## ✅ Antes de Hacer Push a GitHub

### Verificación de Seguridad

Ejecuta estos comandos para asegurarte de no incluir datos personales:

```bash
# Ver qué archivos se incluirían en el commit
git status

# Ver qué archivos están siendo rastreados
git ls-files

# Buscar cualquier PDF que pudiera estar rastreado
git ls-files | findstr /i ".pdf"

# Buscar archivos CSV
git ls-files | findstr /i ".csv"
```

### Si Accidentalmente Agregaste Datos Sensibles

Si ya commiteaste archivos con datos personales:

```bash
# Quitar archivo del staging area (antes de commit)
git reset HEAD archivo_sensible.txt

# Quitar archivo del repositorio pero mantenerlo local
git rm --cached archivo_sensible.txt

# Si ya hiciste push, considera reescribir la historia
# ⚠️ CUIDADO: Esto reescribe la historia del repositorio
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch ruta/al/archivo_sensible.pdf" \
  --prune-empty --tag-name-filter cat -- --all
```

## 🔐 Buenas Prácticas

### Para Desarrollo

1. **Nunca hardcodear** nombres, números de tarjeta u otros datos personales en el código
2. **Usar variables de entorno** para cualquier configuración sensible
3. **Revisar diffs** antes de commitear para detectar datos personales
4. **Usar ejemplos ficticios** en documentación y tests

### Para Compartir o Colaborar

1. **Compartir solo el código fuente** (archivos .py, .md, config sin datos)
2. **Crear datos de prueba** con información ficticia si necesitas ejemplos
3. **Documentar el formato** sin incluir datos reales
4. **Usar placeholders** como "TITULAR EJEMPLO" o "1234-XXXX-XXXX-5678"

## 📋 Checklist Pre-Publicación

Antes de hacer tu repositorio público o compartirlo:

- [ ] Verificar que `.gitignore` existe y está configurado
- [ ] Ejecutar `git status` y revisar la lista
- [ ] Confirmar que NO hay archivos .pdf en `git ls-files`
- [ ] Confirmar que NO hay archivos .csv o .xlsx rastreados
- [ ] Revisar el historial de commits en busca de datos sensibles
- [ ] Buscar en el código referencias a nombres personales
- [ ] Verificar que debug/ y output/ no tienen archivos rastreados
- [ ] Leer todos los .md en busca de ejemplos con datos reales

## 🆘 En Caso de Exposición Accidental

Si accidentalmente publicaste datos personales:

1. **Inmediatamente** hacer el repositorio privado
2. **Eliminar** el repositorio público si es posible
3. **Reescribir** la historia del git para eliminar los datos
4. **Cambiar** cualquier contraseña o token que pudiera haber sido expuesta
5. **Notificar** a las personas afectadas si aplica

## 📚 Recursos Adicionales

- [GitHub - Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [Git - Rewriting History](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History)
- [OWASP - Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
