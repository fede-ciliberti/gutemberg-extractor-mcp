#!/usr/bin/env python3
"""
Simple MCP server test
"""

import asyncio
import json
import subprocess
import sys

async def test_mcp():
    print("🚀 Simple MCP server test")
    
    # Create server process
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
        
        # Send request and read response
        process.stdin.write((json.dumps(init_request) + '\n').encode())
        await process.stdin.drain()
        
        # Read response with timeout
        try:
            response = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
            if response:
                print(f"✅ Response 1: {response.decode()}")
            else:
                print("❌ No response 1")
        except asyncio.TimeoutError:
            print("❌ Timeout in response 1")
        
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
                print(f"✅ Response 2: {response.decode()}")
            else:
                print("❌ No response 2")
        except asyncio.TimeoutError:
            print("❌ Timeout in response 2")
            
        print("✅ Complete test")
        
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