#!/usr/bin/env python3
"""
Gutenberg Resource Extractor MCP Server
========================================

Servidor MCP (Model Context Protocol) para extraer recursos embebidos
en archivos Gutenberg usando la herramienta gutenberg_extractor.py

Autor: Roo AI Agent
Versión: 2.0.0
Cumplimiento: Protocolo MCP completo
"""

import asyncio
import json
import logging
import sys
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse

# Añadir directorio actual al path para importar el extractor
sys.path.insert(0, os.path.dirname(__file__))
from gutenberg_extractor import GutenbergExtractor

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GutenbergExtractorMCPServer:
    """Servidor MCP para extracción de recursos Gutenberg."""
    
    def __init__(self):
        self.extractor = GutenbergExtractor(threshold_kb=1)
        self.capabilities = {
            "tools": {}
        }
        self.tools = self._register_tools()
    
    def _register_tools(self) -> Dict[str, Dict]:
        """Registrar herramientas MCP disponibles."""
        return {
            "extract_resources": {
                "name": "extract_resources",
                "description": "Extraer recursos embebidos de un archivo Gutenberg (.gutemberg) (SVG, PNG, JPG, etc.)",
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
            },
            "analyze_file": {
                "name": "analyze_file",
                "description": "Analizar un archivo Gutenberg (.gutemberg) sin procesar para detectar recursos embebidos",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Ruta del archivo Gutenberg a analizar"
                        }
                    },
                    "required": ["file_path"]
                }
            },
            "batch_process": {
                "name": "batch_process",
                "description": "Procesar múltiples archivos Gutenberg (.gutemberg) en lote",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Lista de rutas de archivos a procesar"
                        },
                        "threshold_kb": {
                            "type": "integer",
                            "description": "Umbral en KB para extraer recursos",
                            "default": 1
                        },
                        "output_base_dir": {
                            "type": "string",
                            "description": "Directorio base de salida opcional"
                        }
                    },
                    "required": ["file_paths"]
                }
            },
            "get_statistics": {
                "name": "get_statistics",
                "description": "Obtener estadísticas detalladas de optimización desde archivo de metadatos",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "metadata_file_path": {
                            "type": "string",
                            "description": "Ruta al archivo de metadatos JSON"
                        }
                    },
                    "required": ["metadata_file_path"]
                }
            },
            "list_supported_types": {
                "name": "list_supported_types",
                "description": "Listar tipos de recursos soportados para extracción",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    
    async def extract_resources(self, file_path: str, threshold_kb: int = 1, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Extraer recursos de un archivo Gutenberg.
        
        Args:
            file_path: Ruta del archivo a procesar
            threshold_kb: Umbral en KB para extraer recursos
            output_dir: Directorio de salida (opcional)
            
        Returns:
            Diccionario con resultados
        """
        try:
            # Validar que el archivo existe
            input_path = Path(file_path)
            if not input_path.exists():
                return {
                    "success": False,
                    "error": f"Archivo no encontrado: {file_path}",
                    "results": None
                }
            
            # Crear extractor con umbral especificado
            extractor = GutenbergExtractor(threshold_kb=threshold_kb)
            
            # Procesar archivo
            metadata = extractor.process_file(file_path, output_dir)
            
            # Formatear respuesta
            return {
                "success": True,
                "error": None,
                "results": {
                    "original_file": metadata["original_file"],
                    "optimized_file": metadata["optimized_file"],
                    "assets_directory": metadata["assets_directory"],
                    "extracted_resources_count": len(metadata["extracted_resources"]),
                    "statistics": metadata["statistics"],
                    "reduction_percentage": round(
                        (metadata["statistics"]["original_size"] - metadata["statistics"]["optimized_size"]) / 
                        metadata["statistics"]["original_size"] * 100, 2
                    ) if metadata["statistics"]["original_size"] > 0 else 0,
                    "metadata_file": metadata.get("output_directory", "") + "/extraction_metadata.json"
                }
            }
            
        except Exception as e:
            logger.error(f"Error procesando archivo {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": None
            }
    
    async def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analizar un archivo Gutenberg sin procesar, solo detectar recursos.
        
        Args:
            file_path: Ruta del archivo a analizar
            
        Returns:
            Diccionario con análisis de recursos
        """
        try:
            # Validar que el archivo existe
            input_path = Path(file_path)
            if not input_path.exists():
                return {
                    "success": False,
                    "error": f"Archivo no encontrado: {file_path}",
                    "analysis": None
                }
            
            # Leer archivo y buscar patterns
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Análisis básico
            analysis = {
                "file_path": str(input_path.absolute()),
                "file_size": len(content),
                "resource_types": {},
                "total_data_uris": 0,
                "estimated_savings": 0
            }
            
            # Buscar diferentes tipos de data URIs
            patterns = self.extractor.patterns
            
            for resource_type, pattern in patterns.items():
                matches = list(pattern.finditer(content))
                analysis["resource_types"][resource_type] = {
                    "count": len(matches),
                    "total_size_estimate": 0
                }
                analysis["total_data_uris"] += len(matches)
            
            # Estimación simplificada de ahorros
            analysis["estimated_savings"] = analysis["total_data_uris"] * 0.1  # 10% por data URI
            
            return {
                "success": True,
                "error": None,
                "analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"Error analizando archivo {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": None
            }
    
    async def batch_process(self, file_paths: List[str], threshold_kb: int = 1, output_base_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Procesar múltiples archivos Gutenberg en lote.
        
        Args:
            file_paths: Lista de rutas de archivos a procesar
            threshold_kb: Umbral en KB para extraer recursos
            output_base_dir: Directorio base de salida (opcional)
            
        Returns:
            Diccionario con resultados del procesamiento en lote
        """
        try:
            results = []
            total_processed = 0
            total_extracted = 0
            total_original_size = 0
            total_optimized_size = 0
            errors = []
            
            for file_path in file_paths:
                try:
                    # Validar archivo
                    input_path = Path(file_path)
                    if not input_path.exists():
                        errors.append(f"Archivo no encontrado: {file_path}")
                        continue
                    
                    # Crear directorio de salida específico
                    file_output_dir = None
                    if output_base_dir:
                        file_output_dir = f"{output_base_dir}/{input_path.stem}_batch"
                    
                    # Procesar archivo individual
                    extractor = GutenbergExtractor(threshold_kb=threshold_kb)
                    metadata = extractor.process_file(file_path, file_output_dir)
                    
                    # Acumular estadísticas
                    total_processed += 1
                    total_extracted += metadata['statistics']['extracted']
                    total_original_size += metadata['statistics']['original_size']
                    total_optimized_size += metadata['statistics']['optimized_size']
                    
                    # Agregar resultado individual
                    result = {
                        "file_path": file_path,
                        "original_file": metadata["original_file"],
                        "optimized_file": metadata["optimized_file"],
                        "extracted_resources_count": len(metadata["extracted_resources"]),
                        "reduction_percentage": round(
                            (metadata["statistics"]["original_size"] - metadata["statistics"]["optimized_size"]) /
                            metadata["statistics"]["original_size"] * 100, 2
                        ) if metadata["statistics"]["original_size"] > 0 else 0,
                        "statistics": metadata["statistics"],
                        "success": True
                    }
                    results.append(result)
                    
                except Exception as e:
                    error_msg = f"Error procesando {file_path}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    results.append({
                        "file_path": file_path,
                        "success": False,
                        "error": str(e)
                    })
            
            # Calcular estadísticas generales
            total_reduction = total_original_size - total_optimized_size
            overall_reduction_percentage = round(
                (total_reduction / total_original_size * 100), 2
            ) if total_original_size > 0 else 0
            
            return {
                "success": True,
                "error": None,
                "batch_summary": {
                    "total_files": len(file_paths),
                    "processed_successfully": total_processed,
                    "failed": len(file_paths) - total_processed,
                    "total_extracted_resources": total_extracted,
                    "total_original_size": total_original_size,
                    "total_optimized_size": total_optimized_size,
                    "total_reduction_bytes": total_reduction,
                    "overall_reduction_percentage": overall_reduction_percentage
                },
                "individual_results": results,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Error en procesamiento en lote: {e}")
            return {
                "success": False,
                "error": str(e),
                "batch_summary": None,
                "individual_results": [],
                "errors": [str(e)]
            }
    
    async def get_statistics(self, metadata_file_path: str) -> Dict[str, Any]:
        """
        Obtener estadísticas de optimización de un archivo de metadatos.
        
        Args:
            metadata_file_path: Ruta al archivo de metadatos JSON
            
        Returns:
            Diccionario con estadísticas detalladas
        """
        try:
            # Validar que el archivo de metadatos existe
            metadata_path = Path(metadata_file_path)
            if not metadata_path.exists():
                return {
                    "success": False,
                    "error": f"Archivo de metadatos no encontrado: {metadata_file_path}",
                    "statistics": None
                }
            
            # Cargar metadatos
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Calcular estadísticas adicionales
            stats = metadata.get('statistics', {})
            extracted_resources = metadata.get('extracted_resources', [])
            
            # Análisis por tipo de recurso
            resource_type_analysis = {}
            for resource in extracted_resources:
                resource_type = resource.get('type', 'unknown')
                if resource_type not in resource_type_analysis:
                    resource_type_analysis[resource_type] = {
                        'count': 0,
                        'total_size': 0,
                        'average_size': 0,
                        'files': []
                    }
                
                resource_type_analysis[resource_type]['count'] += 1
                resource_type_analysis[resource_type]['total_size'] += resource.get('size_bytes', 0)
                resource_type_analysis[resource_type]['files'].append(resource.get('file', ''))
            
            # Calcular tamaños promedio
            for resource_type in resource_type_analysis:
                if resource_type_analysis[resource_type]['count'] > 0:
                    resource_type_analysis[resource_type]['average_size'] = round(
                        resource_type_analysis[resource_type]['total_size'] /
                        resource_type_analysis[resource_type]['count']
                    )
            
            # Análisis de eficiencia
            efficiency_metrics = {
                'resources_per_kb_saved': round(
                    stats.get('extracted', 0) / max(stats.get('original_size', 0) / 1024 / 1000, 1),
                    3
                ),
                'compression_ratio': round(
                    stats.get('original_size', 0) / max(stats.get('optimized_size', 1), 1),
                    2
                ),
                'bytes_saved_per_resource': round(
                    (stats.get('original_size', 0) - stats.get('optimized_size', 0)) /
                    max(stats.get('extracted', 1), 1)
                )
            }
            
            # Proyección de ahorro
            projection = {
                'estimated_monthly_savings_mb': round(
                    (stats.get('original_size', 0) - stats.get('optimized_size', 0)) * 100 / 1024 / 1024,
                    2
                ),
                'projected_yearly_savings_mb': round(
                    (stats.get('original_size', 0) - stats.get('optimized_size', 0)) * 1200 / 1024 / 1024,
                    2
                )
            }
            
            return {
                "success": True,
                "error": None,
                "statistics": {
                    "basic_stats": stats,
                    "resource_type_analysis": resource_type_analysis,
                    "efficiency_metrics": efficiency_metrics,
                    "savings_projection": projection,
                    "metadata": {
                        "extraction_timestamp": metadata.get('extraction_timestamp'),
                        "threshold_kb": metadata.get('threshold_kb'),
                        "original_file": metadata.get('original_file'),
                        "optimized_file": metadata.get('optimized_file')
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de {metadata_file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "statistics": None
            }
    
    async def list_supported_types(self) -> Dict[str, Any]:
        """
        Listar tipos de recursos soportados.
        
        Returns:
            Diccionario con tipos soportados
        """
        return {
            "success": True,
            "error": None,
            "supported_types": {
                "svg": {
                    "pattern": "data:image/svg+xml",
                    "extension": ".svg",
                    "decode_method": "url_decode",
                    "description": "Imágenes vectoriales SVG embebidas"
                },
                "png": {
                    "pattern": "data:image/png;base64",
                    "extension": ".png",
                    "decode_method": "base64_decode",
                    "description": "Imágenes PNG con transparencia"
                },
                "jpg": {
                    "pattern": "data:image/jpeg;base64",
                    "extension": ".jpg",
                    "decode_method": "base64_decode",
                    "description": "Imágenes JPG fotográficas"
                },
                "webp": {
                    "pattern": "data:image/webp;base64",
                    "extension": ".webp",
                    "decode_method": "base64_decode",
                    "description": "Imágenes WebP optimizadas"
                },
                "gif": {
                    "pattern": "data:image/gif;base64",
                    "extension": ".gif",
                    "decode_method": "base64_decode",
                    "description": "Imágenes GIF animadas"
                }
            }
        }


async def handle_initialize(params: Dict[str, Any]) -> Dict[str, Any]:
    """Manejar solicitud initialize del protocolo MCP."""
    return {
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


async def handle_list_tools() -> Dict[str, Any]:
    """Manejar solicitud tools/list del protocolo MCP."""
    server = GutenbergExtractorMCPServer()
    tools = list(server.tools.values())
    
    return {
        "tools": tools
    }


async def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Manejar request del MCP."""
    server = GutenbergExtractorMCPServer()
    
    method = request.get("method")
    params = request.get("params", {})
    
    try:
        # Protocolo MCP methods
        if method == "initialize":
            result = await handle_initialize(params)
            
        elif method == "tools/list":
            result = await handle_list_tools()
            
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            if tool_name not in server.tools:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32601, "message": f"Herramienta no encontrada: {tool_name}"}
                }
            
            # Ejecutar herramienta específica
            if tool_name == "extract_resources":
                file_path = tool_args.get("file_path")
                threshold_kb = tool_args.get("threshold_kb", 1)
                output_dir = tool_args.get("output_dir")
                
                if not file_path:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32602, "message": "file_path es requerido"}
                    }
                
                result = await server.extract_resources(file_path, threshold_kb, output_dir)
                
            elif tool_name == "analyze_file":
                file_path = tool_args.get("file_path")
                
                if not file_path:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32602, "message": "file_path es requerido"}
                    }
                
                result = await server.analyze_file(file_path)
                
            elif tool_name == "batch_process":
                file_paths = tool_args.get("file_paths", [])
                threshold_kb = tool_args.get("threshold_kb", 1)
                output_base_dir = tool_args.get("output_base_dir")
                
                if not file_paths:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32602, "message": "file_paths es requerido"}
                    }
                
                result = await server.batch_process(file_paths, threshold_kb, output_base_dir)
                
            elif tool_name == "get_statistics":
                metadata_file_path = tool_args.get("metadata_file_path")
                
                if not metadata_file_path:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32602, "message": "metadata_file_path es requerido"}
                    }
                
                result = await server.get_statistics(metadata_file_path)
                
            elif tool_name == "list_supported_types":
                result = await server.list_supported_types()
                
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32601, "message": f"Método no implementado: {tool_name}"}
                }
        
        # Legacy methods (mantener para compatibilidad)
        elif method in ["extract_resources", "analyze_file", "list_supported_types", "batch_process", "get_statistics"]:
            if method == "extract_resources":
                file_path = params.get("file_path")
                threshold_kb = params.get("threshold_kb", 1)
                output_dir = params.get("output_dir")
                
                if not file_path:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32602, "message": "file_path es requerido"}
                    }
                
                result = await server.extract_resources(file_path, threshold_kb, output_dir)
                
            elif method == "analyze_file":
                file_path = params.get("file_path")
                
                if not file_path:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32602, "message": "file_path es requerido"}
                    }
                
                result = await server.analyze_file(file_path)
                
            elif method == "list_supported_types":
                result = await server.list_supported_types()
                
            elif method == "batch_process":
                file_paths = params.get("file_paths", [])
                threshold_kb = params.get("threshold_kb", 1)
                output_base_dir = params.get("output_base_dir")
                
                if not file_paths:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32602, "message": "file_paths es requerido"}
                    }
                
                result = await server.batch_process(file_paths, threshold_kb, output_base_dir)
                
            elif method == "get_statistics":
                metadata_file_path = params.get("metadata_file_path")
                
                if not metadata_file_path:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32602, "message": "metadata_file_path es requerido"}
                    }
                
                result = await server.get_statistics(metadata_file_path)
                
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32601, "message": f"Método no encontrado: {method}"}
            }
        
        # Respuesta exitosa
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error manejando request: {e}")
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {"code": -32603, "message": f"Error interno: {str(e)}"}
        }


async def main():
    """Función principal del servidor MCP."""
    parser = argparse.ArgumentParser(description='Servidor MCP para Gutenberg Resource Extractor')
    parser.add_argument('--stdio', action='store_true', help='Usar stdio para comunicación')
    parser.add_argument('--host', default='localhost', help='Host para servidor HTTP')
    parser.add_argument('--port', type=int, default=8080, help='Puerto para servidor HTTP')
    
    args = parser.parse_args()
    
    if args.stdio:
        # Modo stdio para MCP
        logger.info("Iniciando servidor MCP en modo stdio")
        
        # Crear reader para stdin
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
        
        try:
            while True:
                try:
                    # Leer línea completa de stdin
                    line = await reader.readline()
                    if not line:
                        break
                    
                    # Decodificar y procesar request
                    request_str = line.decode('utf-8').strip()
                    if not request_str:
                        continue
                    
                    request = json.loads(request_str)
                    response = await handle_request(request)
                    
                    # Escribir response a stdout con flush
                    response_str = json.dumps(response) + '\n'
                    sys.stdout.write(response_str)
                    sys.stdout.flush()
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Error decodificando JSON: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
                    }
                    sys.stdout.write(json.dumps(error_response) + '\n')
                    sys.stdout.flush()
                except KeyboardInterrupt:
                    logger.info("Servidor detenido por usuario")
                    break
                except Exception as e:
                    logger.error(f"Error en servidor: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
                    }
                    sys.stdout.write(json.dumps(error_response) + '\n')
                    sys.stdout.flush()
                    
        except Exception as e:
            logger.error(f"Error crítico en servidor stdio: {e}")
        finally:
            logger.info("Servidor MCP stdio terminado")
                
    else:
        # Modo HTTP para desarrollo/testing
        logger.info(f"Iniciando servidor HTTP en {args.host}:{args.port}")
        
        # Implementación HTTP simple (para desarrollo)
        # En producción se usaría un framework web como FastAPI
        import aiohttp
        
        async def handle_http_request(request):
            if request.method == 'POST':
                try:
                    data = await request.json()
                    response = await handle_request(data)
                    return aiohttp.web.json_response(response)
                except Exception as e:
                    return aiohttp.web.json_response({
                        "jsonrpc": "2.0",
                        "error": {"code": -32700, "message": f"Error parseando request: {str(e)}"}
                    })
            else:
                return aiohttp.web.Response(text="Gutenberg Extractor MCP Server")
        
        app = aiohttp.web.Application()
        app.router.add_post('/', handle_http_request)
        app.router.add_get('/', lambda req: aiohttp.web.Response(text="Gutenberg Extractor MCP Server"))
        
        runner = aiohttp.web.AppRunner(app)
        await runner.setup()
        
        site = aiohttp.web.TCPSite(runner, args.host, args.port)
        await site.start()
        
        logger.info(f"Servidor MCP disponible en http://{args.host}:{args.port}")
        
        try:
            await asyncio.Future()  # Ejecutar indefinidamente
        except KeyboardInterrupt:
            logger.info("Servidor detenido por usuario")
        finally:
            await runner.cleanup()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Servidor detenido")
    except Exception as e:
        logger.error(f"Error ejecutando servidor: {e}")
        sys.exit(1)