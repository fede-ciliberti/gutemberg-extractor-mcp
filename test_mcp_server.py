#!/usr/bin/env python3
"""
Test Script for Gutenberg Extractor MCP Server
===============================================

Test script to verify MCP server functionality.

Author: Roo AI Agent
Version: 1.0.0
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from mcp_server import handle_request


async def test_mcp_server():
    """Run MCP server tests."""
    print("🧪 Starting Gutenberg Extractor MCP Server Tests")
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
            print(f"\n📋 Running: {test.__name__}")
            result = await test()
            if result:
                print(f"✅ {test.__name__}: PASSED")
                passed += 1
            else:
                print(f"❌ {test.__name__}: FAILED")
        except Exception as e:
            print(f"💥 {test.__name__}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed successfully!")
        return True
    else:
        print("⚠️  Some tests failed")
        return False


async def test_list_supported_types():
    """Test list_supported_types."""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "list_supported_types",
        "params": {}
    }
    
    response = await handle_request(request)
    
    # Verify response
    if "result" in response:
        result = response["result"]
        if result.get("success") and "supported_types" in result:
            types = result["supported_types"]
            expected_types = ["svg", "png", "jpg", "webp", "gif"]
            
            for expected_type in expected_types:
                if expected_type not in types:
                    print(f"  ❌ Missing type: {expected_type}")
                    return False
            
            print(f"  ✅ {len(types)} supported types found")
            return True
    
    print(f"  ❌ Invalid response: {response}")
    return False


async def test_analyze_file():
    """Test analyze_file with test file."""
    # Create temporary test file
    test_content = '''
<!-- wp:image {"id":123} -->
<figure class="wp-block-image">
    <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==" alt="Test"/>
</figure>
<!-- /wp:image -->
'''
    
    test_file = Path("test_gutenberg.gutemberg")
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
                    print(f"  ✅ Detected {analysis['total_data_uris']} data URIs")
                    return True
                else:
                    print(f"  ❌ No data URIs detected")
                    return False
        
        print(f"  ❌ Invalid response: {response}")
        return False
    
    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()


async def test_extract_resources():
    """Test extract_resources with test file."""
    # Create test file with larger data URI
    test_svg = '''data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Crect width='100' height='100' fill='red'/%3E%3C/svg%3E'''
    test_content = f'''
<!-- wp:image {{"id":456}} -->
<figure class="wp-block-image">
    <img src="{test_svg}" alt="Test SVG"/>
</figure>
<!-- /wp:image -->
'''
    
    test_file = Path("test_gutenberg_extract.gutemberg")
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
                print(f"  ✅ Processing successful")
                print(f"     Original file: {results.get('original_file', 'N/A')}")
                print(f"     Extracted resources: {results.get('extracted_resources_count', 0)}")
                print(f"     Reduction: {results.get('reduction_percentage', 0)}%")
                return True
        
        print(f"  ❌ Invalid response: {response}")
        return False
    
    finally:
        # Clean up test files
        if test_file.exists():
            test_file.unlink()
        
        # Clean up extracted directory if exists
        extracted_dir = Path("test_gutenberg_extract_extracted")
        if extracted_dir.exists():
            import shutil
            shutil.rmtree(extracted_dir)


async def test_batch_process():
    """Test batch_process with multiple files."""
    # Create test files
    test_files = []
    test_content = '''
<!-- wp:image {"id":789} -->
<figure class="wp-block-image">
    <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='50' height='50'%3E%3Ccircle cx='25' cy='25' r='20' fill='blue'/%3E%3C/svg%3E" alt="Test"/>
</figure>
<!-- /wp:image -->
'''
    
    for i in range(3):
        test_file = Path(f"test_batch_{i}.gutemberg")
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
                print(f"  ✅ Batch processing successful")
                print(f"     Files processed: {summary.get('processed_successfully', 0)}")
                print(f"     Total extracted resources: {summary.get('total_extracted_resources', 0)}")
                print(f"     Overall reduction: {summary.get('overall_reduction_percentage', 0)}%")
                return True
        
        print(f"  ❌ Invalid response: {response}")
        return False
    
    finally:
        # Clean up test files
        for test_file_path in test_files:
            test_file = Path(test_file_path)
            if test_file.exists():
                test_file.unlink()
        
        # Clean up extracted directories if they exist
        for i in range(3):
            extracted_dir = Path(f"test_batch_{i}_batch")
            if extracted_dir.exists():
                import shutil
                shutil.rmtree(extracted_dir)


async def test_get_statistics():
    """Test get_statistics."""
    # Create test metadata file
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
                print(f"  ✅ Statistics obtained successfully")
                print(f"     Resource types analyzed: {len(statistics.get('resource_type_analysis', {}))}")
                print(f"     Efficiency metrics available: {len(statistics.get('efficiency_metrics', {}))}")
                return True
        
        print(f"  ❌ Invalid response: {response}")
        return False
    
    finally:
        # Clean up test metadata file
        if metadata_file.exists():
            metadata_file.unlink()


if __name__ == "__main__":
    try:
        success = asyncio.run(test_mcp_server())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Error running tests: {e}")
        sys.exit(1)