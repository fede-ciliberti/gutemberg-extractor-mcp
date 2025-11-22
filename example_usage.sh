#!/bin/bash
# Ejemplo de uso del Gutenberg Resource Extractor

echo "🚀 Gutenberg Resource Extractor - Ejemplo de Uso"
echo "================================================"

# Verificar que Python3 esté disponible
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 no está instalado"
    exit 1
fi

# Directorio de ejemplo
EXAMPLE_DIR="../examples"
mkdir -p "$EXAMPLE_DIR"

# Crear archivo de ejemplo con data URIs embebidos
cat > "$EXAMPLE_DIR/sample-gutenberg.template" << 'EOF'
<!-- wp:group {"align":"full"} -->
<div class="wp-block-group alignfull"><!-- wp:image -->
<figure class="wp-block-image"><img src="data:image/svg+xml,%3Csvg width="100" height="50" xmlns="http://www.w3.org/2000/svg"%3E%3Crect width="100" height="50" fill="blue"/%3E%3Ctext x="50" y="25" text-anchor="middle" fill="white"%3ESVG%20Test%3C/text%3E%3C/svg%3E" alt="Test SVG"/></figure>
<!-- /wp:image --></div>
<!-- /wp:group -->

<!-- wp:group {"align":"full"} -->
<div class="wp-block-group alignfull"><!-- wp:image -->
<figure class="wp-block-image"><img src="data:image/png;charset=utf-8;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==" alt="Test PNG"/></figure>
<!-- /wp:image --></div>
<!-- /wp:group -->
EOF

echo "📄 Archivo de ejemplo creado: $EXAMPLE_DIR/sample-gutenberg.template"

# Ejecutar extractor con diferentes configuraciones
echo ""
echo "🔧 Ejecutando extractor..."

# Ejemplo 1: Uso básico
echo "📋 Ejemplo 1: Uso básico"
python3 gutenberg_extractor.py "$EXAMPLE_DIR/sample-gutenberg.template"

# Ejemplo 2: Con umbral personalizado
echo ""
echo "📋 Ejemplo 2: Con umbral de 0 bytes (extraer todos)"
python3 gutenberg_extractor.py "$EXAMPLE_DIR/sample-gutenberg.template" --threshold 0 --verbose

# Mostrar resultados
echo ""
echo "📊 Resultados:"
echo "=============="

if [ -d "$EXAMPLE_DIR/sample-gutenberg_extracted" ]; then
    echo "✅ Directorio de salida creado: $EXAMPLE_DIR/sample-gutenberg_extracted/"
    echo ""
    echo "📁 Contenido:"
    ls -la "$EXAMPLE_DIR/sample-gutenberg_extracted/"
    echo ""
    echo "🖼️ Assets extraídos:"
    ls -la "$EXAMPLE_DIR/sample-gutenberg_extracted/assets/" 2>/dev/null || echo "   No hay assets extraídos"
    echo ""
    echo "📋 Metadatos del proceso:"
    if [ -f "$EXAMPLE_DIR/sample-gutenberg_extracted/extraction_metadata.json" ]; then
        echo "   Archivo: extraction_metadata.json"
        echo "   Tamaño del archivo original vs optimizado:"
        ORIGINAL_SIZE=$(stat -c%s "$EXAMPLE_DIR/sample-gutenberg.template")
        OPTIMIZED_SIZE=$(stat -c%s "$EXAMPLE_DIR/sample-gutenberg_extracted/sample-gutenberg.template")
        echo "   Original: $ORIGINAL_SIZE bytes"
        echo "   Optimizado: $OPTIMIZED_SIZE bytes"
        if [ $ORIGINAL_SIZE -gt $OPTIMIZED_SIZE ]; then
            SAVED=$((ORIGINAL_SIZE - OPTIMIZED_SIZE))
            PERCENT=$((SAVED * 100 / ORIGINAL_SIZE))
            echo "   ✅ Ahorro: $SAVED bytes ($PERCENT%)"
        else
            echo "   ℹ️ Sin reducción de tamaño (archivo muy pequeño)"
        fi
    fi
else
    echo "❌ Error: No se creó el directorio de salida"
fi

echo ""
echo "🎉 Ejemplo completado!"
echo ""
echo "💡 Para usar con tus propios archivos:"
echo "   python3 gutenberg_extractor.py tu_archivo.template"
echo ""
echo "📖 Consulta README.md para documentación completa"