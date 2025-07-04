#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAWAGOT.AI MCP Server for Cursor
"""

import json
import sys
import requests
import subprocess
import os
from datetime import datetime

def get_dashboard_status():
    """Get dashboard status"""
    try:
        response = requests.get('http://localhost:5000/api/status', timeout=5)
        return {
            "status": "success",
            "data": response.json(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def start_dashboard():
    """Start dashboard server"""
    try:
        subprocess.Popen(["python", "dashboard/app.py"], 
                        cwd=os.getcwd(), 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
        return {
            "status": "success",
            "message": "Dashboard started successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def get_system_status():
    """Get system status"""
    try:
        result = subprocess.run(["python", "system_status_check.py"], 
                              capture_output=True, text=True, cwd=os.getcwd())
        return {
            "status": "success",
            "data": result.stdout,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def execute_command(command_type, params=None):
    """Execute various commands"""
    try:
        if command_type == "dashboard_status":
            return get_dashboard_status()
        elif command_type == "start_dashboard":
            return start_dashboard()
        elif command_type == "system_status":
            return get_system_status()
        elif command_type == "custom_api":
            endpoint = params.get("endpoint", "/api/status")
            response = requests.get(f'http://localhost:5000{endpoint}', timeout=5)
            return {
                "status": "success",
                "data": response.json(),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error",
                "error": f"Unknown command: {command_type}",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# MCP Protocol Handler
def handle_mcp_request():
    """Handle MCP requests from Cursor"""
    try:
        line = input()
        request = json.loads(line)
        
        command = request.get("command")
        params = request.get("params", {})
        
        result = execute_command(command, params)
        
        response = {
            "id": request.get("id"),
            "result": result
        }
        
        print(json.dumps(response))
        sys.stdout.flush()
        
    except EOFError:
        pass
    except Exception as e:
        error_response = {
            "id": request.get("id") if 'request' in locals() else None,
            "error": {
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        }
        print(json.dumps(error_response))
        sys.stdout.flush()

if __name__ == "__main__":
    # Simple MCP server loop
    while True:
        try:
            handle_mcp_request()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(json.dumps({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }))
            sys.stdout.flush()