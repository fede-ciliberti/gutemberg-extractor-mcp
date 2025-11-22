#!/usr/bin/env python3
"""
Script de prueba para validar el cumplimiento del protocolo MCP
del servidor Gutenberg Extractor.
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Configuración de logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MCPComplianceTester:
    """Tester para validar cumplimiento del protocolo MCP."""
    
    def __init__(self):
        self.server_process = None
        
    async def start_server(self):
        """Iniciar el servidor MCP en modo stdio."""
        try:
            logger.info("Iniciando servidor MCP...")
            self.server_process = await asyncio.create_subprocess_exec(
                sys.executable, 'mcp_server.py', '--stdio',
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Esperar un poco para que el servidor se inicie
            await asyncio.sleep(1)
            logger.info("Servidor MCP iniciado")
            
        except Exception as e:
            logger.error(f"Error iniciando servidor: {e}")
            raise
    
    async def stop_server(self):
        """Detener el servidor MCP."""
        if self.server_process:
            self.server_process.terminate()
            try:
                await asyncio.wait_for(self.server_process.wait(), timeout=5)
            except asyncio.TimeoutError:
                self.server_process.kill()
            logger.info("Servidor MCP detenido")
    
    async def send_request(self, request: dict) -> dict:
        """Enviar request al servidor y recibir respuesta."""
        try:
            request_str = json.dumps(request) + '\n'
            logger.info(f"Enviando request: {request['method']}")
            
            self.server_process.stdin.write(request_str.encode())
            await self.server_process.stdin.drain()
            
            response_line = await self.server_process.stdout.readline()
            response = json.loads(response_line.decode())
            
            logger.info(f"Respuesta recibida: {response.get('result', {}).get('serverInfo', {}).get('name', 'unknown') if 'result' in response else 'error'}")
            return response
            
        except Exception as e:
            logger.error(f"Error enviando request: {e}")
            raise
    
    async def test_initialize(self) -> bool:
        """Probar solicitud initialize."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        try:
            response = await self.send_request(request)
            
            # Validar respuesta
            assert "result" in response, "Falta 'result' en respuesta"
            assert "protocolVersion" in response["result"], "Falta 'protocolVersion' en respuesta"
            assert "capabilities" in response["result"], "Falta 'capabilities' en respuesta"
            assert "serverInfo" in response["result"], "Falta 'serverInfo' en respuesta"
            
            server_info = response["result"]["serverInfo"]
            assert server_info["name"] == "gutenberg-extractor", "Nombre del servidor incorrecto"
            assert server_info["version"] == "2.0.0", "Versión del servidor incorrecta"
            
            logger.info("✅ Test initialize PASSED")
            return True
            
        except Exception as e:
            logger.error(f"❌ Test initialize FAILED: {e}")
            return False
    
    async def test_tools_list(self) -> bool:
        """Probar solicitud tools/list."""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        try:
            response = await self.send_request(request)
            
            # Validar respuesta
            assert "result" in response, "Falta 'result' en respuesta"
            assert "tools" in response["result"], "Falta 'tools' en respuesta"
            
            tools = response["result"]["tools"]
            assert len(tools) > 0, "No hay herramientas registradas"
            
            # Verificar que todas las herramientas tienen la estructura correcta
            expected_tools = [
                "extract_resources", "analyze_file", "batch_process", 
                "get_statistics", "list_supported_types"
            ]
            
            actual_tools = [tool["name"] for tool in tools]
            for expected_tool in expected_tools:
                assert expected_tool in actual_tools, f"Herramienta faltante: {expected_tool}"
            
            # Verificar estructura de herramientas
            for tool in tools:
                assert "name" in tool, f"Herramienta sin nombre: {tool}"
                assert "description" in tool, f"Herramienta sin descripción: {tool['name']}"
                assert "inputSchema" in tool, f"Herramienta sin schema: {tool['name']}"
            
            logger.info(f"✅ Test tools/list PASSED - {len(tools)} herramientas encontradas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Test tools/list FAILED: {e}")
            return False
    
    async def test_tools_call(self) -> bool:
        """Probar solicitud tools/call."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "list_supported_types",
                "arguments": {}
            }
        }
        
        try:
            response = await self.send_request(request)
            
            # Validar respuesta
            assert "result" in response, "Falta 'result' en respuesta"
            assert "supported_types" in response["result"], "Falta 'supported_types' en respuesta"
            
            supported_types = response["result"]["supported_types"]
            expected_types = ["svg", "png", "jpg", "webp", "gif"]
            
            for expected_type in expected_types:
                assert expected_type in supported_types, f"Tipo de recurso faltante: {expected_type}"
            
            logger.info(f"✅ Test tools/call PASSED - {len(supported_types)} tipos soportados")
            return True
            
        except Exception as e:
            logger.error(f"❌ Test tools/call FAILED: {e}")
            return False
    
    async def test_legacy_methods(self) -> bool:
        """Probar métodos legacy para compatibilidad."""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "list_supported_types",
            "params": {}
        }
        
        try:
            response = await self.send_request(request)
            
            # Validar respuesta
            assert "result" in response, "Falta 'result' en respuesta"
            assert "supported_types" in response["result"], "Falta 'supported_types' en respuesta"
            
            logger.info("✅ Test legacy methods PASSED")
            return True
            
        except Exception as e:
            logger.error(f"❌ Test legacy methods FAILED: {e}")
            return False
    
    async def test_error_handling(self) -> bool:
        """Probar manejo de errores."""
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "nonexistent_tool",
                "arguments": {}
            }
        }
        
        try:
            response = await self.send_request(request)
            
            # Validar respuesta de error
            assert "error" in response, "Falta 'error' en respuesta"
            assert response["error"]["code"] == -32601, "Código de error incorrecto"
            assert "Herramienta no encontrada" in response["error"]["message"], "Mensaje de error incorrecto"
            
            logger.info("✅ Test error handling PASSED")
            return True
            
        except Exception as e:
            logger.error(f"❌ Test error handling FAILED: {e}")
            return False
    
    async def run_all_tests(self) -> dict:
        """Ejecutar todos los tests."""
        logger.info("Iniciando tests de cumplimiento del protocolo MCP")
        
        results = {}
        
        try:
            await self.start_server()
            
            # Ejecutar tests
            results["initialize"] = await self.test_initialize()
            results["tools_list"] = await self.test_tools_list()
            results["tools_call"] = await self.test_tools_call()
            results["legacy_methods"] = await self.test_legacy_methods()
            results["error_handling"] = await self.test_error_handling()
            
        except Exception as e:
            logger.error(f"Error durante los tests: {e}")
            results["error"] = str(e)
            
        finally:
            await self.stop_server()
        
        # Reporte final
        total_tests = len([k for k in results.keys() if k != "error"])
        passed_tests = len([k for k in results.keys() if results.get(k, False) is True])
        
        logger.info("=" * 60)
        logger.info("REPORTE FINAL DE TESTS")
        logger.info("=" * 60)
        
        for test_name, result in results.items():
            if test_name == "error":
                continue
            
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{test_name}: {status}")
        
        logger.info(f"\nTotal: {passed_tests}/{total_tests} tests pasados")
        
        if passed_tests == total_tests:
            logger.info("🎉 Todos los tests han pasado! El servidor cumple con el protocolo MCP")
        else:
            logger.warning(f"⚠️  {total_tests - passed_tests} tests han fallado")
        
        return results


async def main():
    """Función principal."""
    tester = MCPComplianceTester()
    
    # Cambiar al directorio del servidor
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    results = await tester.run_all_tests()
    
    # Código de salida
    failed_tests = len([k for k, v in results.items() if k != "error" and v is False])
    sys.exit(failed_tests)


if __name__ == "__main__":
    asyncio.run(main())