#!/usr/bin/env python3
"""
Test simple del servidor MCP
"""

import asyncio
import json
import subprocess
import sys

async def test_mcp():
    print("🚀 Test simple del servidor MCP")
    
    # Crear proceso del servidor
    process = await asyncio.create_subprocess_exec(
        sys.executable, 'mcp_server.py', '--stdio',
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    try:
        # Test 1: initialize
        print("📤 Test 1: initialize")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test"}
            }
        }
        
        # Enviar request y leer respuesta
        process.stdin.write((json.dumps(init_request) + '\n').encode())
        await process.stdin.drain()
        
        # Leer respuesta con timeout
        try:
            response = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
            if response:
                print(f"✅ Respuesta 1: {response.decode()}")
            else:
                print("❌ No hay respuesta 1")
        except asyncio.TimeoutError:
            print("❌ Timeout en respuesta 1")
        
        # Test 2: tools/list
        print("📤 Test 2: tools/list")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        process.stdin.write((json.dumps(tools_request) + '\n').encode())
        await process.stdin.drain()
        
        try:
            response = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
            if response:
                print(f"✅ Respuesta 2: {response.decode()}")
            else:
                print("❌ No hay respuesta 2")
        except asyncio.TimeoutError:
            print("❌ Timeout en respuesta 2")
            
        print("✅ Test completo")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        try:
            process.terminate()
            await process.wait()
        except:
            pass

if __name__ == '__main__':
    asyncio.run(test_mcp())