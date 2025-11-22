#!/bin/bash
# Example usage of Gutenberg Resource Extractor

echo "🚀 Gutenberg Resource Extractor - Usage Example"
echo "================================================"

# Check if Python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 is not installed"
    exit 1
fi

# Example directory
EXAMPLE_DIR="../examples"
mkdir -p "$EXAMPLE_DIR"

# Create example file with embedded data URIs
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

echo "📄 Example file created: $EXAMPLE_DIR/sample-gutenberg.template"

# Run extractor with different configurations
echo ""
echo "🔧 Running extractor..."

# Example 1: Basic usage
echo "📋 Example 1: Basic usage"
python3 gutenberg_extractor.py "$EXAMPLE_DIR/sample-gutenberg.template"

# Example 2: With custom threshold
echo ""
echo "📋 Example 2: With 0 bytes threshold (extract all)"
python3 gutenberg_extractor.py "$EXAMPLE_DIR/sample-gutenberg.template" --threshold 0 --verbose

# Show results
echo ""
echo "📊 Results:"
echo "=============="

if [ -d "$EXAMPLE_DIR/sample-gutenberg_extracted" ]; then
    echo "✅ Output directory created: $EXAMPLE_DIR/sample-gutenberg_extracted/"
    echo ""
    echo "📁 Contents:"
    ls -la "$EXAMPLE_DIR/sample-gutenberg_extracted/"
    echo ""
    echo "🖼️ Extracted assets:"
    ls -la "$EXAMPLE_DIR/sample-gutenberg_extracted/assets/" 2>/dev/null || echo "   No extracted assets"
    echo ""
    echo "📋 Process metadata:"
    if [ -f "$EXAMPLE_DIR/sample-gutenberg_extracted/extraction_metadata.json" ]; then
        echo "   File: extraction_metadata.json"
        echo "   Original vs optimized file size:"
        ORIGINAL_SIZE=$(stat -c%s "$EXAMPLE_DIR/sample-gutenberg.template")
        OPTIMIZED_SIZE=$(stat -c%s "$EXAMPLE_DIR/sample-gutenberg_extracted/sample-gutenberg.template")
        echo "   Original: $ORIGINAL_SIZE bytes"
        echo "   Optimized: $OPTIMIZED_SIZE bytes"
        if [ $ORIGINAL_SIZE -gt $OPTIMIZED_SIZE ]; then
            SAVED=$((ORIGINAL_SIZE - OPTIMIZED_SIZE))
            PERCENT=$((SAVED * 100 / ORIGINAL_SIZE))
            echo "   ✅ Savings: $SAVED bytes ($PERCENT%)"
        else
            echo "   ℹ️ No size reduction (file too small)"
        fi
    fi
else
    echo "❌ Error: Output directory not created"
fi

echo ""
echo "🎉 Example completed!"
echo ""
echo "💡 To use with your own files:"
echo "   python3 gutenberg_extractor.py your_file.template"
echo ""
echo "📖 See README.md for complete documentation"