# Gutenberg Extractor MCP Server - Complete Documentation

## Description

MCP (Model Context Protocol) server for extracting embedded resources from Gutenberg files. Full compliance with MCP protocol 2024-11-05.

## Features

### MCP Protocol Compliance

- ✅ **Initialize**: Complete support for MCP protocol initialize requests
- ✅ **Tools/List**: Implements tools/list method to return list of available tools  
- ✅ **JSON-RPC 2.0**: Correct handling of MCP protocol JSON-RPC 2.0 requests
- ✅ **Tool Registration**: Tools are correctly registered in the response
- ✅ **Detection**: Server is correctly detected by MCP system
- ✅ **Testing**: Complete protocol compliance test suite

### Functionalities

1. **extract_resources**: Extract embedded resources (SVG, PNG, JPG, WebP, GIF) from Gutenberg files
2. **analyze_file**: Analyze file to detect embedded resources without processing
3. **batch_process**: Process multiple Gutenberg files in batch
4. **get_statistics**: Get detailed optimization statistics
5. **list_supported_types**: List supported resource types

## Installation and Configuration

### Requirements

- Python 3.9+
- Libraries: asyncio, json, logging, pathlib

### MCP Configuration

1. **Configuration in MCP Settings**:

```json
{
  "mcpServers": {
    "gutenberg-extractor": {
      "command": "python",
      "args": ["mcp_server.py", "--stdio"],
      "cwd": "/path/to/tools/gutenberg-extractor"
    }
  }
}
```

### Server Usage

#### Stdio Mode (Production)
```bash
python mcp_server.py --stdio
```

#### HTTP Mode (Development)
```bash
python mcp_server.py --host localhost --port 8080
```

## MCP Protocol API

### Initialize

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "client-name",
      "version": "1.0.0"
    }
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {}
    },
    "serverInfo": {
      "name": "gutenberg-extractor",
      "version": "2.0.0",
      "description": "MCP server for extracting embedded resources from Gutenberg files"
    }
  }
}
```

### Tools/List

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "extract_resources",
        "description": "Extract embedded resources from a Gutenberg file (SVG, PNG, JPG, etc.)",
        "inputSchema": {
          "type": "object",
          "properties": {
            "file_path": {
              "type": "string",
              "description": "Path of the Gutenberg file to process"
            },
            "threshold_kb": {
              "type": "integer",
              "description": "Threshold in KB to extract resources",
              "default": 1
            },
            "output_dir": {
              "type": "string",
              "description": "Optional output directory"
            }
          },
          "required": ["file_path"]
        }
      }
      // ... more tools
    ]
  }
}
```

### Tools/Call - extract_resources

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "extract_resources",
    "arguments": {
      "file_path": "/path/to/gutenberg.template",
      "threshold_kb": 1,
      "output_dir": "/path/to/output"
    }
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "success": true,
    "error": null,
    "results": {
      "original_file": "/path/to/gutenberg.template",
      "optimized_file": "/path/to/gutenberg_optimized.template",
      "assets_directory": "/path/to/output/assets",
      "extracted_resources_count": 15,
      "statistics": {
        "original_size": 1024000,
        "optimized_size": 875200,
        "extracted": 15,
        "bytes_saved": 148800
      },
      "reduction_percentage": 14.53,
      "metadata_file": "/path/to/extraction_metadata.json"
    }
  }
}
```

## Legacy Compatibility

The server maintains compatibility with legacy methods to facilitate migration:

- `extract_resources` (direct call)
- `analyze_file` (direct call)  
- `batch_process` (direct call)
- `get_statistics` (direct call)
- `list_supported_types` (direct call)

## Testing and Validation

### Run Compliance Tests

```bash
python test_mcp_compliance.py
```

### Included Tests

1. **Initialize Test**: Validates correct initialize response
2. **Tools/List Test**: Verifies complete tool list
3. **Tools/Call Test**: Tests tool execution
4. **Legacy Methods Test**: Confirms legacy compatibility
5. **Error Handling Test**: Validates JSON-RPC error handling

### Test Report

```
===========================================================
FINAL TEST REPORT
===========================================================
initialize: ✅ PASSED
tools_list: ✅ PASSED  
tools_call: ✅ PASSED
legacy_methods: ✅ PASSED
error_handling: ✅ PASSED

Total: 5/5 tests passed
🎉 All tests passed! The server complies with the MCP protocol
```

## Complete Usage Example

```python
import asyncio
import json

# Simulate initialize request
initialize_request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize", 
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test-client", "version": "1.0.0"}
    }
}

# Simulate tools/list request
tools_list_request = {
    "jsonrpc": "2.0", 
    "id": 2,
    "method": "tools/list",
    "params": {}
}

# Simulate tools/call request for list_supported_types
tools_call_request = {
    "jsonrpc": "2.0",
    "id": 3, 
    "method": "tools/call",
    "params": {
        "name": "list_supported_types",
        "arguments": {}
    }
}
```

## Troubleshooting

### Server Not Detected

1. Verify MCP configuration in settings
2. Run compliance tests: `python test_mcp_compliance.py`
3. Check server logs for errors
4. Confirm that `mcp_server.py` file is executable

### Tools Don't Appear

1. Verify that initialize runs correctly
2. Confirm that tools/list responds with tool list
3. Check tools/list response structure

### JSON-RPC Errors

1. Validate JSON format of requests
2. Verify correct error codes (-32601, -32602, -32603)
3. Confirm that protocol version matches

## Logging and Debugging

The server uses logging configured with:

```python
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
```

### Important Logs

- `INFO - Starting MCP server in stdio mode`
- `INFO - Sending request: {method}`
- `INFO - Response received: {server_name}`
- `ERROR - Error handling request: {error}`

## Project Structure

```
tools/gutenberg-extractor/
├── mcp_server.py              # Main MCP server
├── test_mcp_compliance.py     # Test suite
├── gutenberg_extractor.py     # Base extractor
├── README.md                  # This documentation
├── example_usage.sh          # Usage example
└── setup_mcp.sh             # Configuration script
```

## Version and Updates

- **v2.0.0**: Full MCP protocol compliance
- **v1.0.0**: Basic initial version

### Changes in v2.0.0

- ✅ Complete initialize/initialize implementation
- ✅ Support for tools/list and tools/call
- ✅ Formal MCP tool registration
- ✅ Correct JSON-RPC 2.0 response structure
- ✅ Compliance test suite
- ✅ Compatibility with legacy methods

## Contribution

1. Run tests: `python test_mcp_compliance.py`
2. Verify MCP compliance before commit
3. Document new tools with appropriate schemas
4. Maintain backward compatibility with legacy methods