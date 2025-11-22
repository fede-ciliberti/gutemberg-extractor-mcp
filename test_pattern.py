#!/usr/bin/env python3
"""
Script de prueba para diagnosticar los patrones regex
"""

import re
import urllib.parse
import base64

# Patrones de prueba
patterns = {
    'svg': re.compile(r'data:image/svg\+xml(?:;charset=utf-8)?,(?P<content>[^"\'\s]+)'),
    'png': re.compile(r'data:image/png(?:;charset=utf-8)?;base64,(?P<content>[A-Za-z0-9+/=]+)'),
    'jpg': re.compile(r'data:image/jpeg(?:;charset=utf-8)?;base64,(?P<content>[A-Za-z0-9+/=]+)')
}

# Datos de prueba basados en el archivo bosk.template
test_data = [
    'data:image/svg+xml,%3Csvg width="141" height="48" viewBox="0 0 141 48" fill="none" xmlns="http://www.w3.org/2000/svg"%3E%3Cg clip-path="url(%23clip0_875_1070)"%3E%3Cpath d="M10.3038 44.0259L0 43.2242V42.6074L0.609886 42.4842C2.19526 42.1144 2.98794 41.087 2.98794 39.4013V6.41274C2.98794 5.54945 2.85555 4.892</svg>',
    'data:image/png;charset=utf-8;base64,iVBORw0KGgoAAAANSUhEUgAAAaMAAAFbCAYAAAB4VOGAAAAACXBIWXMAAAsTAAALEwEAmpwYAAABaWlDQ1BEaXNwbGF5IFAzAAB4nHWQvUvDUBTFT6tS0DqIDh0cMolD1NIKdnFoKxRFMFQFq1OafgltfCQpUnETVyn4H1jBWXCwiFRwcXAQRAcR3Zw6KbhoeN6XVNoi3sfl/Ticc7lcwBtQGSv2AijplpFMxKS11Lrke4OHnlOqZrKooiwK/v276/PR9d5PiFlNu3YQ2U9cl84ul3aeAlN//V3Vn8maGv3f1EGNGRbgkYmVbYsJ3iUeMWgp4qrgvMvHgtMun',
]

print("🔍 Probando patrones regex...")

for i, test in enumerate(test_data, 1):
    print(f"\n📄 Test {i}: {test[:80]}...")
    
    for pattern_name, pattern in patterns.items():
        match = pattern.search(test)
        if match:
            print(f"  ✅ {pattern_name}: Match encontrado")
            content = match.group('content')
            print(f"     Contenido: {content[:50]}...")
            
            try:
                if pattern_name == 'svg':
                    # URL decode para SVG
                    decoded = urllib.parse.unquote(content)
                    print(f"     Decodificado: {decoded[:50]}...")
                    print(f"     Tamaño: {len(decoded)} bytes")
                    
                    # Guardar archivo de prueba
                    with open(f'/tmp/test_{pattern_name}_{i}.svg', 'w', encoding='utf-8') as f:
                        f.write(decoded)
                    print(f"     💾 Guardado: /tmp/test_{pattern_name}_{i}.svg")
                    
                else:
                    # Base64 decode para imágenes
                    decoded = base64.b64decode(content)
                    print(f"     Tamaño: {len(decoded)} bytes")
                    
                    # Guardar archivo de prueba
                    with open(f'/tmp/test_{pattern_name}_{i}.png', 'wb') as f:
                        f.write(decoded)
                    print(f"     💾 Guardado: /tmp/test_{pattern_name}_{i}.png")
                    
            except Exception as e:
                print(f"     ❌ Error decodificando: {e}")
        else:
            print(f"  ❌ {pattern_name}: No match")

print("\n🔧 Análisis de patrones completado")