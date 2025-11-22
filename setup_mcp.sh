#!/bin/bash
# Setup script para el servidor MCP de Gutenberg Resource Extractor v2.0.0
# Cumplimiento completo del protocolo MCP

echo "🚀 Configurando Gutenberg Extractor MCP Server v2.0.0"
echo "====================================================="

# Verificar Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    exit 1
fi

echo "✅ Python 3 encontrado: $(python3 --version)"

# Crear entorno virtual (opcional)
VENV_DIR="venv"
if [ "$1" = "--venv" ]; then
    echo "🔧 Creando entorno virtual..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    echo "✅ Entorno virtual activado"
fi

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip3 install aiohttp 2>/dev/null || echo "⚠️ aiohttp ya está instalado o no disponible"

# Hacer ejecutables los scripts
chmod +x gutenberg_extractor.py
chmod +x mcp_server.py
chmod +x test_mcp_compliance.py
chmod +x example_usage.sh

echo ""
echo "✅ Configuración completada!"
echo ""
echo "📋 Comandos disponibles:"
echo "  • python3 gutenberg_extractor.py archivo.template"
echo "  • python3 mcp_server.py --stdio"
echo "  • python3 test_mcp_compliance.py (pruebas de cumplimiento MCP)"
echo "  • ./example_usage.sh"
echo ""
echo "🔧 Configuración MCP:"
echo "  1. Agregar a tu configuración MCP settings:"
echo ""
echo '  {'
echo '    "mcpServers": {'
echo '      "gutenberg-extractor": {'
echo '        "command": "python3",'
echo '        "args": ["mcp_server.py", "--stdio"],'
echo '        "cwd": "'$(pwd)'"'
echo '      }'
echo '    }'
echo '  }'
echo ""
echo "🧪 Validar cumplimiento MCP:"
echo "  python3 test_mcp_compliance.py"
echo ""
echo "📚 Herramientas disponibles:"
echo "  • extract_resources: Extraer recursos embebidos"
echo "  • analyze_file: Analizar archivo sin procesar"
echo "  • batch_process: Procesar múltiples archivos"
echo "  • get_statistics: Obtener estadísticas detalladas"
echo "  • list_supported_types: Listar tipos soportados"