#!/usr/bin/env python3
"""
Test script to diagnose regex patterns
"""

import re
import urllib.parse
import base64

# Test patterns
patterns = {
    'svg': re.compile(r'data:image/svg\+xml(?:;charset=utf-8)?,(?P<content>[^"\'\s]+)'),
    'png': re.compile(r'data:image/png(?:;charset=utf-8)?;base64,(?P<content>[A-Za-z0-9+/=]+)'),
    'jpg': re.compile(r'data:image/jpeg(?:;charset=utf-8)?;base64,(?P<content>[A-Za-z0-9+/=]+)')
}

# Test data based on bosk.template file
test_data = [
    'data:image/svg+xml,%3Csvg width="141" height="48" viewBox="0 0 141 48" fill="none" xmlns="http://www.w3.org/2000/svg"%3E%3Cg clip-path="url(%23clip0_875_1070)"%3E%3Cpath d="M10.3038 44.0259L0 43.2242V42.6074L0.609886 42.4842C2.19526 42.1144 2.98794 41.087 2.98794 39.4013V6.41274C2.98794 5.54945 2.85555 4.892</svg>',
    'data:image/png;charset=utf-8;base64,iVBORw0KGgoAAAANSUhEUgAAAaMAAAFbCAYAAAB4VOGAAAAACXBIWXMAAAsTAAALEwEAmpwYAAABaWlDQ1BEaXNwbGF5IFAzAAB4nHWQvUvDUBTFT6tS0DqIDh0cMolD1NIKdnFoKxRFMFQFq1OafgltfCQpUnETVyn4H1jBWXCwiFRwcXAQRAcR3Zw6KbhoeN6XVNoi3sfl/Ticc7lcwBtQGSv2AijplpFMxKS11Lrke4OHnlOqZrKooiwK/v276/PR9d5PiFlNu3YQ2U9cl84ul3aeAlN//V3Vn8maGv3f1EGNGRbgkYmVbYsJ3iUeMWgp4qrgvMvHgtMun',
]

print("🔍 Testing regex patterns...")

for i, test in enumerate(test_data, 1):
    print(f"\n📄 Test {i}: {test[:80]}...")
    
    for pattern_name, pattern in patterns.items():
        match = pattern.search(test)
        if match:
            print(f"  ✅ {pattern_name}: Match found")
            content = match.group('content')
            print(f"     Content: {content[:50]}...")
            
            try:
                if pattern_name == 'svg':
                    # URL decode for SVG
                    decoded = urllib.parse.unquote(content)
                    print(f"     Decoded: {decoded[:50]}...")
                    print(f"     Size: {len(decoded)} bytes")
                    
                    # Save test file
                    with open(f'/tmp/test_{pattern_name}_{i}.svg', 'w', encoding='utf-8') as f:
                        f.write(decoded)
                    print(f"     💾 Saved: /tmp/test_{pattern_name}_{i}.svg")
                    
                else:
                    # Base64 decode for images
                    decoded = base64.b64decode(content)
                    print(f"     Size: {len(decoded)} bytes")
                    
                    # Save test file
                    with open(f'/tmp/test_{pattern_name}_{i}.png', 'wb') as f:
                        f.write(decoded)
                    print(f"     💾 Saved: /tmp/test_{pattern_name}_{i}.png")
                    
            except Exception as e:
                print(f"     ❌ Error decoding: {e}")
        else:
            print(f"  ❌ {pattern_name}: No match")

print("\n🔧 Pattern analysis completed")