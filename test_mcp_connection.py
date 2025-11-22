#!/usr/bin/env python3
"""
Direct connection test to MCP server
"""

import asyncio
import json
import sys
import subprocess
import time
import os

async def test_mcp_server():
    """Test the MCP server directly"""
    
    print("🔍 Starting MCP server test...")
    
    # Change to server directory
    os.chdir('/home/fciliberti/Trabajos/Cronopia/sites/bosk/tools/gutenberg-extractor')
    
    # Start the MCP server as a process
    process = await asyncio.create_subprocess_exec(
        sys.executable, 'mcp_server.py', '--stdio',
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    try:
        # Test 1: Initialize
        print("📤 Sending initialize...")
        initialize_request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'test-client'}
            }
        }
        
        request_line = json.dumps(initialize_request) + '\n'
        stdout, stderr = await process.communicate(request_line.encode())
        
        if stdout:
            response = json.loads(stdout.decode().strip())
            print(f"✅ Initialize response: {json.dumps(response, indent=2)}")
        else:
            print(f"❌ No response for initialize. Stderr: {stderr.decode()}")
        
        # Test 2: Tools/list
        print("\n📤 Sending tools/list...")
        tools_request = {
            'jsonrpc': '2.0', 
            'id': 2,
            'method': 'tools/list'
        }
        
        request_line = json.dumps(tools_request) + '\n'
        stdout, stderr = await process.communicate(request_line.encode())
        
        if stdout:
            response = json.loads(stdout.decode().strip())
            print(f"✅ Tools/list response: {json.dumps(response, indent=2)}")
            
            # Verify that tools are present
            tools = response.get('result', {}).get('tools', [])
            if tools:
                print(f"🎯 Tools found: {len(tools)}")
                for tool in tools:
                    print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
            else:
                print("❌ No tools found")
                
        else:
            print(f"❌ No response for tools/list. Stderr: {stderr.decode()}")
            
        # Test 3: List supported types (specific tool)
        print("\n📤 Sending tools/call list_supported_types...")
        tools_call_request = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'list_supported_types',
                'arguments': {}
            }
        }
        
        request_line = json.dumps(tools_call_request) + '\n'
        stdout, stderr = await process.communicate(request_line.encode())
        
        if stdout:
            response = json.loads(stdout.decode().strip())
            print(f"✅ List supported types response: {json.dumps(response, indent=2)}")
        else:
            print(f"❌ No response for list_supported_types. Stderr: {stderr.decode()}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        
    finally:
        # Close the process
        process.terminate()
        await process.wait()


if __name__ == '__main__':
    asyncio.run(test_mcp_server())