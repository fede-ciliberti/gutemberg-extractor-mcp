#!/usr/bin/env python3
"""
Test Script para Gutenberg Extractor MCP Server
===============================================

Script de prueba para verificar la funcionalidad del servidor MCP.

Autor: Roo AI Agent
Versión: 1.0.0
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Añadir directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

from mcp_server import handle_request


async def test_mcp_server():
    """Ejecutar pruebas del servidor MCP."""
    print("🧪 Iniciando pruebas del servidor MCP Gutenberg Extractor")
    print("=" * 60)
    
    tests = [
        test_list_supported_types,
        test_analyze_file,
        test_extract_resources,
        test_batch_process,
        test_get_statistics
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            print(f"\n📋 Ejecutando: {test.__name__}")
            result = await test()
            if result:
                print(f"✅ {test.__name__}: PASADO")
                passed += 1
            else:
                print(f"❌ {test.__name__}: FALLIDO")
        except Exception as e:
            print(f"💥 {test.__name__}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Resultados: {passed}/{total} pruebas pasadas")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron exitosamente!")
        return True
    else:
        print("⚠️  Algunas pruebas fallaron")
        return False


async def test_list_supported_types():
    """Probar list_supported_types."""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "list_supported_types",
        "params": {}
    }
    
    response = await handle_request(request)
    
    # Verificar respuesta
    if "result" in response:
        result = response["result"]
        if result.get("success") and "supported_types" in result:
            types = result["supported_types"]
            expected_types = ["svg", "png", "jpg", "webp", "gif"]
            
            for expected_type in expected_types:
                if expected_type not in types:
                    print(f"  ❌ Tipo faltante: {expected_type}")
                    return False
            
            print(f"  ✅ {len(types)} tipos soportados encontrados")
            return True
    
    print(f"  ❌ Respuesta inválida: {response}")
    return False


async def test_analyze_file():
    """Probar analyze_file con archivo de prueba."""
    # Crear archivo de prueba temporal
    test_content = '''
<!-- wp:image {"id":123} -->
<figure class="wp-block-image">
    <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==" alt="Test"/>
</figure>
<!-- /wp:image -->
'''
    
    test_file = Path("test_gutenberg.template")
    test_file.write_text(test_content, encoding='utf-8')
    
    try:
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "analyze_file",
            "params": {
                "file_path": str(test_file.absolute())
            }
        }
        
        response = await handle_request(request)
        
        if "result" in response:
            result = response["result"]
            if result.get("success") and "analysis" in result:
                analysis = result["analysis"]
                if analysis.get("total_data_uris", 0) > 0:
                    print(f"  ✅ Detectado {analysis['total_data_uris']} data URIs")
                    return True
                else:
                    print(f"  ❌ No se detectaron data URIs")
                    return False
        
        print(f"  ❌ Respuesta inválida: {response}")
        return False
    
    finally:
        # Limpiar archivo de prueba
        if test_file.exists():
            test_file.unlink()


async def test_extract_resources():
    """Probar extract_resources con archivo de prueba."""
    # Crear archivo de prueba con data URI más grande
    test_svg = '''data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Crect width='100' height='100' fill='red'/%3E%3C/svg%3E'''
    test_content = f'''
<!-- wp:image {{"id":456}} -->
<figure class="wp-block-image">
    <img src="{test_svg}" alt="Test SVG"/>
</figure>
<!-- /wp:image -->
'''
    
    test_file = Path("test_gutenberg_extract.template")
    test_file.write_text(test_content, encoding='utf-8')
    
    try:
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "extract_resources",
            "params": {
                "file_path": str(test_file.absolute()),
                "threshold_kb": 0
            }
        }
        
        response = await handle_request(request)
        
        if "result" in response:
            result = response["result"]
            if result.get("success") and "results" in result:
                results = result["results"]
                print(f"  ✅ Procesamiento exitoso")
                print(f"     Archivo original: {results.get('original_file', 'N/A')}")
                print(f"     Recursos extraídos: {results.get('extracted_resources_count', 0)}")
                print(f"     Reducción: {results.get('reduction_percentage', 0)}%")
                return True
        
        print(f"  ❌ Respuesta inválida: {response}")
        return False
    
    finally:
        # Limpiar archivos de prueba
        if test_file.exists():
            test_file.unlink()
        
        # Limpiar directorio extraído si existe
        extracted_dir = Path("test_gutenberg_extract_extracted")
        if extracted_dir.exists():
            import shutil
            shutil.rmtree(extracted_dir)


async def test_batch_process():
    """Probar batch_process con múltiples archivos."""
    # Crear archivos de prueba
    test_files = []
    test_content = '''
<!-- wp:image {"id":789} -->
<figure class="wp-block-image">
    <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='50' height='50'%3E%3Ccircle cx='25' cy='25' r='20' fill='blue'/%3E%3C/svg%3E" alt="Test"/>
</figure>
<!-- /wp:image -->
'''
    
    for i in range(3):
        test_file = Path(f"test_batch_{i}.template")
        test_file.write_text(test_content, encoding='utf-8')
        test_files.append(str(test_file.absolute()))
    
    try:
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "batch_process",
            "params": {
                "file_paths": test_files,
                "threshold_kb": 0
            }
        }
        
        response = await handle_request(request)
        
        if "result" in response:
            result = response["result"]
            if result.get("success") and "batch_summary" in result:
                summary = result["batch_summary"]
                print(f"  ✅ Procesamiento en lote exitoso")
                print(f"     Archivos procesados: {summary.get('processed_successfully', 0)}")
                print(f"     Recursos totales extraídos: {summary.get('total_extracted_resources', 0)}")
                print(f"     Reducción general: {summary.get('overall_reduction_percentage', 0)}%")
                return True
        
        print(f"  ❌ Respuesta inválida: {response}")
        return False
    
    finally:
        # Limpiar archivos de prueba
        for test_file_path in test_files:
            test_file = Path(test_file_path)
            if test_file.exists():
                test_file.unlink()
        
        # Limpiar directorios extraídos si existen
        for i in range(3):
            extracted_dir = Path(f"test_batch_{i}_batch")
            if extracted_dir.exists():
                import shutil
                shutil.rmtree(extracted_dir)


async def test_get_statistics():
    """Probar get_statistics."""
    # Crear archivo de metadatos de prueba
    test_metadata = {
        "original_file": "/test/original.template",
        "statistics": {
            "total_resources": 5,
            "extracted": 4,
            "skipped": 1,
            "original_size": 100000,
            "optimized_size": 85000
        },
        "extracted_resources": [
            {"type": "svg", "size_bytes": 1000, "file": "test1.svg"},
            {"type": "png", "size_bytes": 2000, "file": "test2.png"},
            {"type": "svg", "size_bytes": 1500, "file": "test3.svg"}
        ],
        "extraction_timestamp": "2025-11-21T17:00:00Z",
        "threshold_kb": 1
    }
    
    metadata_file = Path("test_metadata.json")
    metadata_file.write_text(json.dumps(test_metadata, indent=2), encoding='utf-8')
    
    try:
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "get_statistics",
            "params": {
                "metadata_file_path": str(metadata_file.absolute())
            }
        }
        
        response = await handle_request(request)
        
        if "result" in response:
            result = response["result"]
            if result.get("success") and "statistics" in result:
                statistics = result["statistics"]
                print(f"  ✅ Estadísticas obtenidas exitosamente")
                print(f"     Tipos de recursos analizados: {len(statistics.get('resource_type_analysis', {}))}")
                print(f"     Métricas de eficiencia disponibles: {len(statistics.get('efficiency_metrics', {}))}")
                return True
        
        print(f"  ❌ Respuesta inválida: {response}")
        return False
    
    finally:
        # Limpiar archivo de metadatos de prueba
        if metadata_file.exists():
            metadata_file.unlink()


if __name__ == "__main__":
    try:
        success = asyncio.run(test_mcp_server())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Pruebas interrumpidas por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Error ejecutando pruebas: {e}")
        sys.exit(1)