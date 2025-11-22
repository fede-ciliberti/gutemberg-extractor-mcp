#!/bin/bash
# Setup script for Gutenberg Resource Extractor MCP Server v2.0.0
# Full MCP protocol compliance

echo "🚀 Configuring Gutenberg Extractor MCP Server v2.0.0"
echo "====================================================="

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment (optional)
VENV_DIR="venv"
if [ "$1" = "--venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    echo "✅ Virtual environment activated"
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install aiohttp 2>/dev/null || echo "⚠️ aiohttp is already installed or not available"

# Make scripts executable
chmod +x gutenberg_extractor.py
chmod +x mcp_server.py
chmod +x test_mcp_compliance.py
chmod +x example_usage.sh

echo ""
echo "✅ Configuration completed!"
echo ""
echo "📋 Available commands:"
echo "  • python3 gutenberg_extractor.py file.template"
echo "  • python3 mcp_server.py --stdio"
echo "  • python3 test_mcp_compliance.py (MCP compliance tests)"
echo "  • ./example_usage.sh"
echo ""
echo "🔧 MCP Configuration:"
echo "  1. Add to your MCP settings configuration:"
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
echo "🧪 Validate MCP compliance:"
echo "  python3 test_mcp_compliance.py"
echo ""
echo "📚 Available tools:"
echo "  • extract_resources: Extract embedded resources"
echo "  • analyze_file: Analyze file without processing"
echo "  • batch_process: Process multiple files"
echo "  • get_statistics: Get detailed statistics"
echo "  • list_supported_types: List supported types"