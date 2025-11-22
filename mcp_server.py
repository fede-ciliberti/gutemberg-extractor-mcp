#!/usr/bin/env python3
"""
Gutenberg Resource Extractor MCP Server
========================================

MCP (Model Context Protocol) server for extracting embedded resources
from Gutenberg files using the gutenberg_extractor.py tool

Author: Roo AI Agent
Version: 2.0.0
Compliance: Full MCP Protocol
"""

import asyncio
import json
import logging
import sys
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse

# Add current directory to path to import the extractor
sys.path.insert(0, os.path.dirname(__file__))
from gutenberg_extractor import GutenbergExtractor

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GutenbergExtractorMCPServer:
    """MCP server for Gutenberg resource extraction."""
    
    def __init__(self):
        self.extractor = GutenbergExtractor(threshold_kb=1)
        self.capabilities = {
            "tools": {}
        }
        self.tools = self._register_tools()
    
    def _register_tools(self) -> Dict[str, Dict]:
        """Register available MCP tools."""
        return {
            "extract_resources": {
                "name": "extract_resources",
                "description": "Extract embedded resources from a Gutenberg file (.gutemberg) (SVG, PNG, JPG, etc.)",
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
            },
            "analyze_file": {
                "name": "analyze_file",
                "description": "Analyze a Gutenberg file (.gutemberg) without processing to detect embedded resources",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path of the Gutenberg file to analyze"
                        }
                    },
                    "required": ["file_path"]
                }
            },
            "batch_process": {
                "name": "batch_process",
                "description": "Process multiple Gutenberg files (.gutemberg) in batch",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of file paths to process"
                        },
                        "threshold_kb": {
                            "type": "integer",
                            "description": "Threshold in KB to extract resources",
                            "default": 1
                        },
                        "output_base_dir": {
                            "type": "string",
                            "description": "Optional base output directory"
                        }
                    },
                    "required": ["file_paths"]
                }
            },
            "get_statistics": {
                "name": "get_statistics",
                "description": "Get detailed optimization statistics from metadata file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "metadata_file_path": {
                            "type": "string",
                            "description": "Path to JSON metadata file"
                        }
                    },
                    "required": ["metadata_file_path"]
                }
            },
            "list_supported_types": {
                "name": "list_supported_types",
                "description": "List supported resource types for extraction",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    
    async def extract_resources(self, file_path: str, threshold_kb: int = 1, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract resources from a Gutenberg file.
        
        Args:
            file_path: Path of the file to process
            threshold_kb: Threshold in KB to extract resources
            output_dir: Output directory (optional)
            
        Returns:
            Dictionary with results
        """
        try:
            # Validate that the file exists
            input_path = Path(file_path)
            if not input_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "results": None
                }
            
            # Create extractor with specified threshold
            extractor = GutenbergExtractor(threshold_kb=threshold_kb)
            
            # Process file
            metadata = extractor.process_file(file_path, output_dir)
            
            # Format response
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
            logger.error(f"Error processing file {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": None
            }
    
    async def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a Gutenberg file without processing, only detect resources.
        
        Args:
            file_path: Path of the file to analyze
            
        Returns:
            Dictionary with resource analysis
        """
        try:
            # Validate that the file exists
            input_path = Path(file_path)
            if not input_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "analysis": None
                }
            
            # Read file and search patterns
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic analysis
            analysis = {
                "file_path": str(input_path.absolute()),
                "file_size": len(content),
                "resource_types": {},
                "total_data_uris": 0,
                "estimated_savings": 0
            }
            
            # Search for different data URI types
            patterns = self.extractor.patterns
            
            for resource_type, pattern in patterns.items():
                matches = list(pattern.finditer(content))
                analysis["resource_types"][resource_type] = {
                    "count": len(matches),
                    "total_size_estimate": 0
                }
                analysis["total_data_uris"] += len(matches)
            
            # Simplified savings estimation
            analysis["estimated_savings"] = analysis["total_data_uris"] * 0.1  # 10% per data URI
            
            return {
                "success": True,
                "error": None,
                "analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": None
            }
    
    async def batch_process(self, file_paths: List[str], threshold_kb: int = 1, output_base_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Process multiple Gutenberg files in batch.
        
        Args:
            file_paths: List of file paths to process
            threshold_kb: Threshold in KB to extract resources
            output_base_dir: Base output directory (optional)
            
        Returns:
            Dictionary with batch processing results
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
                    # Validate file
                    input_path = Path(file_path)
                    if not input_path.exists():
                        errors.append(f"File not found: {file_path}")
                        continue
                    
                    # Create specific output directory
                    file_output_dir = None
                    if output_base_dir:
                        file_output_dir = f"{output_base_dir}/{input_path.stem}_batch"
                    
                    # Process individual file
                    extractor = GutenbergExtractor(threshold_kb=threshold_kb)
                    metadata = extractor.process_file(file_path, file_output_dir)
                    
                    # Accumulate statistics
                    total_processed += 1
                    total_extracted += metadata['statistics']['extracted']
                    total_original_size += metadata['statistics']['original_size']
                    total_optimized_size += metadata['statistics']['optimized_size']
                    
                    # Add individual result
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
                    error_msg = f"Error processing {file_path}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    results.append({
                        "file_path": file_path,
                        "success": False,
                        "error": str(e)
                    })
            
            # Calculate overall statistics
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
            logger.error(f"Error in batch processing: {e}")
            return {
                "success": False,
                "error": str(e),
                "batch_summary": None,
                "individual_results": [],
                "errors": [str(e)]
            }
    
    async def get_statistics(self, metadata_file_path: str) -> Dict[str, Any]:
        """
        Get optimization statistics from a metadata file.
        
        Args:
            metadata_file_path: Path to JSON metadata file
            
        Returns:
            Dictionary with detailed statistics
        """
        try:
            # Validate that the metadata file exists
            metadata_path = Path(metadata_file_path)
            if not metadata_path.exists():
                return {
                    "success": False,
                    "error": f"Metadata file not found: {metadata_file_path}",
                    "statistics": None
                }
            
            # Load metadata
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Calculate additional statistics
            stats = metadata.get('statistics', {})
            extracted_resources = metadata.get('extracted_resources', [])
            
            # Resource type analysis
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
            
            # Calculate average sizes
            for resource_type in resource_type_analysis:
                if resource_type_analysis[resource_type]['count'] > 0:
                    resource_type_analysis[resource_type]['average_size'] = round(
                        resource_type_analysis[resource_type]['total_size'] /
                        resource_type_analysis[resource_type]['count']
                    )
            
            # Efficiency analysis
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
            
            # Savings projection
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
            logger.error(f"Error getting statistics from {metadata_file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "statistics": None
            }
    
    async def list_supported_types(self) -> Dict[str, Any]:
        """
        List supported resource types.
        
        Returns:
            Dictionary with supported types
        """
        return {
            "success": True,
            "error": None,
            "supported_types": {
                "svg": {
                    "pattern": "data:image/svg+xml",
                    "extension": ".svg",
                    "decode_method": "url_decode",
                    "description": "Embedded SVG vector images"
                },
                "png": {
                    "pattern": "data:image/png;base64",
                    "extension": ".png",
                    "decode_method": "base64_decode",
                    "description": "PNG images with transparency"
                },
                "jpg": {
                    "pattern": "data:image/jpeg;base64",
                    "extension": ".jpg",
                    "decode_method": "base64_decode",
                    "description": "JPG photographic images"
                },
                "webp": {
                    "pattern": "data:image/webp;base64",
                    "extension": ".webp",
                    "decode_method": "base64_decode",
                    "description": "Optimized WebP images"
                },
                "gif": {
                    "pattern": "data:image/gif;base64",
                    "extension": ".gif",
                    "decode_method": "base64_decode",
                    "description": "Animated GIF images"
                }
            }
        }


async def handle_initialize(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle initialize request from MCP protocol."""
    return {
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


async def handle_list_tools() -> Dict[str, Any]:
    """Handle tools/list request from MCP protocol."""
    server = GutenbergExtractorMCPServer()
    tools = list(server.tools.values())
    
    return {
        "tools": tools
    }


async def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP request."""
    server = GutenbergExtractorMCPServer()
    
    method = request.get("method")
    params = request.get("params", {})
    
    try:
        # Protocol MCP methods
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
                    "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}
                }
            
            # Execute specific tool
            if tool_name == "extract_resources":
                file_path = tool_args.get("file_path")
                threshold_kb = tool_args.get("threshold_kb", 1)
                output_dir = tool_args.get("output_dir")
                
                if not file_path:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32602, "message": "file_path is required"}
                    }
                
                result = await server.extract_resources(file_path, threshold_kb, output_dir)
                
            elif tool_name == "analyze_file":
                file_path = tool_args.get("file_path")
                
                if not file_path:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32602, "message": "file_path is required"}
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
                        "error": {"code": -32602, "message": "file_paths is required"}
                    }
                
                result = await server.batch_process(file_paths, threshold_kb, output_base_dir)
                
            elif tool_name == "get_statistics":
                metadata_file_path = tool_args.get("metadata_file_path")
                
                if not metadata_file_path:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32602, "message": "metadata_file_path is required"}
                    }
                
                result = await server.get_statistics(metadata_file_path)
                
            elif tool_name == "list_supported_types":
                result = await server.list_supported_types()
                
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32601, "message": f"Method not implemented: {tool_name}"}
                }
        
        # Legacy methods (maintain for compatibility)
        elif method in ["extract_resources", "analyze_file", "list_supported_types", "batch_process", "get_statistics"]:
            if method == "extract_resources":
                file_path = params.get("file_path")
                threshold_kb = params.get("threshold_kb", 1)
                output_dir = params.get("output_dir")
                
                if not file_path:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32602, "message": "file_path is required"}
                    }
                
                result = await server.extract_resources(file_path, threshold_kb, output_dir)
                
            elif method == "analyze_file":
                file_path = params.get("file_path")
                
                if not file_path:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32602, "message": "file_path is required"}
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
                        "error": {"code": -32602, "message": "file_paths is required"}
                    }
                
                result = await server.batch_process(file_paths, threshold_kb, output_base_dir)
                
            elif method == "get_statistics":
                metadata_file_path = params.get("metadata_file_path")
                
                if not metadata_file_path:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32602, "message": "metadata_file_path is required"}
                    }
                
                result = await server.get_statistics(metadata_file_path)
                
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }
        
        # Successful response
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error handling request: {e}")
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
        }


async def main():
    """Main MCP server function."""
    parser = argparse.ArgumentParser(description='MCP server for Gutenberg Resource Extractor')
    parser.add_argument('--stdio', action='store_true', help='Use stdio for communication')
    parser.add_argument('--host', default='localhost', help='Host for HTTP server')
    parser.add_argument('--port', type=int, default=8080, help='Port for HTTP server')
    
    args = parser.parse_args()
    
    if args.stdio:
        # Stdio mode for MCP
        logger.info("Starting MCP server in stdio mode")
        
        # Create reader for stdin
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
        
        try:
            while True:
                try:
                    # Read complete line from stdin
                    line = await reader.readline()
                    if not line:
                        break
                    
                    # Decode and process request
                    request_str = line.decode('utf-8').strip()
                    if not request_str:
                        continue
                    
                    request = json.loads(request_str)
                    response = await handle_request(request)
                    
                    # Write response to stdout with flush
                    response_str = json.dumps(response) + '\n'
                    sys.stdout.write(response_str)
                    sys.stdout.flush()
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding JSON: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
                    }
                    sys.stdout.write(json.dumps(error_response) + '\n')
                    sys.stdout.flush()
                except KeyboardInterrupt:
                    logger.info("Server stopped by user")
                    break
                except Exception as e:
                    logger.error(f"Error in server: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
                    }
                    sys.stdout.write(json.dumps(error_response) + '\n')
                    sys.stdout.flush()
                    
        except Exception as e:
            logger.error(f"Critical error in stdio server: {e}")
        finally:
            logger.info("stdio MCP server terminated")
                
    else:
        # HTTP mode for development/testing
        logger.info(f"Starting HTTP server on {args.host}:{args.port}")
        
        # Simple HTTP implementation (for development)
        # In production a web framework like FastAPI would be used
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
                        "error": {"code": -32700, "message": f"Error parsing request: {str(e)}"}
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
        
        logger.info(f"MCP server available at http://{args.host}:{args.port}")
        
        try:
            await asyncio.Future()  # Run indefinitely
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        finally:
            await runner.cleanup()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)