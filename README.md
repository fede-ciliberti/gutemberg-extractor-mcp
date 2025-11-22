# Gutenberg Extractor MCP Server - Documentación Completa

## Descripción

Servidor MCP (Model Context Protocol) para extraer recursos embebidos en archivos Gutenberg. Cumplimiento completo del protocolo MCP 2024-11-05.

## Características

### Protocolo MCP Compliance

- ✅ **Initialize**: Soporte completo para solicitudes initialize del protocolo MCP
- ✅ **Tools/List**: Implementa método tools/list para devolver lista de herramientas disponibles  
- ✅ **JSON-RPC 2.0**: Manejo correcto de solicitudes JSON-RPC 2.0 del protocolo MCP
- ✅ **Registro de herramientas**: Las herramientas se registran correctamente en la respuesta
- ✅ **Detección**: El servidor se detecta correctamente por el sistema MCP
- ✅ **Testing**: Suite completa de pruebas de cumplimiento del protocolo

### Funcionalidades

1. **extract_resources**: Extraer recursos embebidos (SVG, PNG, JPG, WebP, GIF) de archivos Gutenberg
2. **analyze_file**: Analizar archivo para detectar recursos embebidos sin procesar
3. **batch_process**: Procesar múltiples archivos Gutenberg en lote
4. **get_statistics**: Obtener estadísticas detalladas de optimización
5. **list_supported_types**: Listar tipos de recursos soportados

## Instalación y Configuración

### Requisitos

- Python 3.9+
- Librerías: asyncio, json, logging, pathlib

### Configuración MCP

1. **Configuración en MCP Settings**:

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

### Uso del Servidor

#### Modo Stdio (Producción)
```bash
python mcp_server.py --stdio
```

#### Modo HTTP (Desarrollo)
```bash
python mcp_server.py --host localhost --port 8080
```

## API del Protocolo MCP

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
      "description": "Servidor MCP para extracción de recursos embebidos en archivos Gutenberg"
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
        "description": "Extraer recursos embebidos de un archivo Gutenberg (SVG, PNG, JPG, etc.)",
        "inputSchema": {
          "type": "object",
          "properties": {
            "file_path": {
              "type": "string",
              "description": "Ruta del archivo Gutenberg a procesar"
            },
            "threshold_kb": {
              "type": "integer",
              "description": "Umbral en KB para extraer recursos",
              "default": 1
            },
            "output_dir": {
              "type": "string",
              "description": "Directorio de salida opcional"
            }
          },
          "required": ["file_path"]
        }
      }
      // ... más herramientas
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

## Compatibilidad Legacy

El servidor mantiene compatibilidad con métodos legacy para facilitar la migración:

- `extract_resources` (direct call)
- `analyze_file` (direct call)  
- `batch_process` (direct call)
- `get_statistics` (direct call)
- `list_supported_types` (direct call)

## Testing y Validación

### Ejecutar Tests de Cumplimiento

```bash
python test_mcp_compliance.py
```

### Tests Incluidos

1. **Initialize Test**: Valida respuesta correcta a initialize
2. **Tools/List Test**: Verifica lista completa de herramientas
3. **Tools/Call Test**: Prueba ejecución de herramientas
4. **Legacy Methods Test**: Confirma compatibilidad legacy
5. **Error Handling Test**: Valida manejo de errores JSON-RPC

### Reporte de Tests

```
===========================================================
REPORTE FINAL DE TESTS
===========================================================
initialize: ✅ PASSED
tools_list: ✅ PASSED  
tools_call: ✅ PASSED
legacy_methods: ✅ PASSED
error_handling: ✅ PASSED

Total: 5/5 tests pasados
🎉 Todos los tests han pasado! El servidor cumple con el protocolo MCP
```

## Ejemplo de Uso Completo

```python
import asyncio
import json

# Simular request initialize
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

# Simular request tools/list
tools_list_request = {
    "jsonrpc": "2.0", 
    "id": 2,
    "method": "tools/list",
    "params": {}
}

# Simular request tools/call para list_supported_types
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

## Resolución de Problemas

### Servidor No Se Detecta

1. Verificar configuración MCP en settings
2. Ejecutar tests de cumplimiento: `python test_mcp_compliance.py`
3. Revisar logs del servidor para errores
4. Confirmar que el archivo `mcp_server.py` es ejecutable

### Herramientas No Aparecen

1. Verificar que initialize se ejecuta correctamente
2. Confirmar que tools/list responde con lista de herramientas
3. Revisar estructura de respuesta tools/list

### Errores JSON-RPC

1. Validar formato JSON de requests
2. Verificar códigos de error correctos (-32601, -32602, -32603)
3. Confirmar que el protocolo version coincide

## Logs y Debugging

El servidor usa logging configurado con:

```python
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
```

### Logs Importantes

- `INFO - Iniciando servidor MCP en modo stdio`
- `INFO - Enviando request: {method}`
- `INFO - Respuesta recibida: {server_name}`
- `ERROR - Error manejando request: {error}`

## Estructura del Proyecto

```
tools/gutenberg-extractor/
├── mcp_server.py              # Servidor MCP principal
├── test_mcp_compliance.py     # Suite de pruebas
├── gutenberg_extractor.py     # Extractor base
├── README.md                  # Esta documentación
├── example_usage.sh          # Ejemplo de uso
└── setup_mcp.sh             # Script de configuración
```

## Versión y Actualizaciones

- **v2.0.0**: Cumplimiento completo del protocolo MCP
- **v1.0.0**: Versión inicial básica

### Cambios en v2.0.0

- ✅ Implementación completa initialize/initialize
- ✅ Soporte para tools/list y tools/call
- ✅ Registro formal de herramientas MCP
- ✅ Estructura de respuesta JSON-RPC 2.0 correcta
- ✅ Suite de pruebas de cumplimiento
- ✅ Compatibilidad con métodos legacy

## Contribución

1. Ejecutar tests: `python test_mcp_compliance.py`
2. Verificar cumplimiento MCP antes de commit
3. Documentar nuevas herramientas con schemas apropiados
4. Mantener compatibilidad backward con legacy methods