"""
Script de prueba para verificar el extractor de Patagonia
Uso: 
  python tests/patagonia.py                    # Procesa todos los PDFs
  python tests/patagonia.py archivo.pdf        # Procesa solo ese archivo
"""
import sys
import argparse
from pathlib import Path

# Agregar el directorio padre al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from extractors.patagonia import PatagoniaExtractor
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logging.getLogger('pdfplumber').setLevel(logging.WARNING)
logging.getLogger('pdfminer').setLevel(logging.WARNING)

def save_movements_to_file(movements, pdf_file, output_folder, resumen_info=None):
    """Guarda los movimientos en un archivo de texto"""
    month_identifier = pdf_file.stem.split('.')[-1] if '.' in pdf_file.stem else '2025-01'
    result_filename = output_folder / f"movimientos_{month_identifier}.txt"
    
    with open(result_filename, 'w', encoding='utf-8') as f:
        f.write(f"📊 MOVIMIENTOS: {pdf_file.name}\n")
        f.write(f"{'='*80}\n\n")
        
        # Tabla de movimientos
        f.write(f"{'#':<3} {'Fecha':<10} {'Comprobante':<12} {'Descripción':<30} {'Cuota':<8} {'Titular':<15} {'Monto':>12}\n")
        f.write("-" * 100 + "\n")
        
        for i, mov in enumerate(movements, 1):
            fecha_str = mov['fecha'].strftime('%Y-%m-%d') if mov.get('fecha') else ''
            comprobante = (mov.get('comprobante', '') or '')[:11]
            descripcion = (mov.get('descripcion', '') or '')[:29]
            cuota = (mov.get('cuota', '') or '')[:7]
            titular = (mov.get('titular', '') or '')[:14]
            
            f.write(f"{i:<3} {fecha_str:<10} {comprobante:<12} {descripcion:<30} "
                   f"{cuota:<8} {titular:<15} ${mov['importe']:>11,.2f}\n")
        
        f.write("-" * 100 + "\n")
        f.write(f"Total movimientos: {len(movements)}\n\n")
        
        # Validación si está disponible
        if resumen_info:
            f.write("\n📊 VALIDACIÓN:\n")
            f.write(f"{'Categoría':<25} {'Importe':>15}\n")
            f.write("-" * 42 + "\n")
            f.write(f"{'Saldo anterior':<25} ${resumen_info.get('saldo_anterior', 0):>12,.2f}\n")
            f.write(f"{'Total consumos':<25} ${resumen_info.get('total_consumos', 0):>12,.2f}\n")
            f.write(f"{'Bonificaciones':<25} ${resumen_info.get('bonificaciones', 0):>12,.2f}\n")
            f.write(f"{'Cargos bancarios':<25} ${resumen_info.get('cargos_bancarios', 0):>12,.2f}\n")
            f.write("-" * 42 + "\n")
            f.write(f"{'SALDO CALCULADO':<25} ${resumen_info.get('saldo_calculado', 0):>12,.2f}\n")
            f.write(f"{'Saldo oficial':<25} ${resumen_info.get('saldo_actual', 0):>12,.2f}\n")
            
            if resumen_info.get('validacion_ok'):
                f.write(f"{'Estado':<25} ✅ Validación exitosa\n")
            else:
                diferencia = resumen_info.get('diferencia_validacion', 0)
                f.write(f"{'Diferencia':<25} ${diferencia:>12,.2f}\n")
                f.write(f"{'Estado':<25} ⚠️ Diferencia significativa\n")

def test_patagonia_extractor(specific_file=None):
    """Prueba el extractor de Patagonia"""
    extractor = PatagoniaExtractor()
    
    # Buscar PDFs (ajustar ruta relativa desde tests/)
    patagonia_folder = Path(__file__).parent.parent / "input" / "VISA_Patagonia"
    if not patagonia_folder.exists():
        print(f"❌ No se encontró: {patagonia_folder}")
        return
    
    # Determinar archivos a procesar
    if specific_file:
        target_file = patagonia_folder / specific_file
        if not target_file.suffix == '.pdf':
            target_file = patagonia_folder / f"{specific_file}.pdf"
        
        if not target_file.exists():
            print(f"❌ No se encontró: {target_file.name}")
            return
        
        pdf_files = [target_file]
    else:
        pdf_files = sorted(patagonia_folder.glob("*.pdf"))
        if not pdf_files:
            print(f"❌ No hay PDFs en {patagonia_folder}")
            return
    
    # Crear carpeta de salida (ajustar ruta relativa desde tests/)
    output_folder = Path(__file__).parent.parent / "debug" / "resultados"
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Procesar archivos
    validation_results = []
    
    for pdf_file in pdf_files:
        print(f"\n🔍 Procesando: {pdf_file.name}")
        
        try:
            # Extraer movimientos
            movements = extractor.extract(pdf_file)
            
            if not movements:
                print("  ⚠️  No se encontraron movimientos")
                continue
            
            print(f"  Movimientos: {len(movements)}")
            
            # Guardar resultados
            resumen_info = extractor.last_resumen_info
            save_movements_to_file(movements, pdf_file, output_folder, resumen_info)
            
            # Mostrar validación
            if resumen_info:
                validation_results.append({
                    'archivo': pdf_file.name,
                    'saldo_calculado': resumen_info.get('saldo_calculado', 0),
                    'saldo_oficial': resumen_info.get('saldo_actual', 0),
                    'validacion_ok': resumen_info.get('validacion_ok', False),
                    'diferencia': resumen_info.get('diferencia_validacion', 0)
                })
                
                print(f"\n  📊 VALIDACIÓN:")
                print(f"  {'Categoría':<25} {'Importe':>15}")
                print("  " + "-" * 42)
                print(f"  {'Saldo anterior':<25} ${resumen_info.get('saldo_anterior', 0):>12,.2f}")
                print(f"  {'Total consumos':<25} ${resumen_info.get('total_consumos', 0):>12,.2f}")
                print(f"  {'Bonificaciones':<25} ${resumen_info.get('bonificaciones', 0):>12,.2f}")
                print(f"  {'Cargos bancarios':<25} ${resumen_info.get('cargos_bancarios', 0):>12,.2f}")
                print("  " + "-" * 42)
                print(f"  {'SALDO CALCULADO':<25} ${resumen_info.get('saldo_calculado', 0):>12,.2f}")
                print(f"  {'Saldo oficial':<25} ${resumen_info.get('saldo_actual', 0):>12,.2f}")
                print(f"  {'Estado':<25} {'✅ Validación exitosa' if resumen_info.get('validacion_ok') else '⚠️ Diferencia significativa'}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Resumen final
    if len(pdf_files) > 1 and validation_results:
        print(f"\n{'='*60}")
        print(f"📊 RESUMEN FINAL")
        print(f"{'='*60}")
        print(f"  Archivos procesados: {len(pdf_files)}")
        print(f"  Exitosos: {len(validation_results)}")
        
        print(f"\n  Validación por archivo:")
        print(f"  {'Archivo':<35} {'Calculado':>15} {'Oficial':>15} {'Estado':>15}")
        print("  " + "-" * 82)
        
        for result in validation_results:
            archivo = result['archivo'][:34]
            print(f"  {archivo:<35} ${result['saldo_calculado']:>12,.2f} "
                  f"${result['saldo_oficial']:>12,.2f} "
                  f"{'✅' if result['validacion_ok'] else '⚠️':>15}")
        
        print(f"{'='*60}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Prueba del extractor de Patagonia')
    parser.add_argument('archivo', nargs='?', help='Archivo PDF específico (opcional)')
    args = parser.parse_args()
    
    test_patagonia_extractor(args.archivo)