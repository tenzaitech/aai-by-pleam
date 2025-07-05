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
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mcp_server.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def get_dashboard_status():
    """Get dashboard status"""
    try:
        response = requests.get('http://localhost:5000/api/status', timeout=5)
        return {
            "status": "success",
            "data": response.json(),
            "timestamp": datetime.now().isoformat()
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Dashboard status request failed: {e}")
        return {
            "status": "error",
            "error": f"Dashboard connection failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Unexpected error in get_dashboard_status: {e}")
        return {
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

def start_dashboard():
    """Start dashboard server"""
    try:
        subprocess.Popen(["python", "dashboard/app.py"], 
                        cwd=os.getcwd(), 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
        logger.info("Dashboard started successfully")
        return {
            "status": "success",
            "message": "Dashboard started successfully",
            "timestamp": datetime.now().isoformat()
        }
    except FileNotFoundError as e:
        logger.error(f"Dashboard file not found: {e}")
        return {
            "status": "error",
            "error": f"Dashboard file not found: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Unexpected error in start_dashboard: {e}")
        return {
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
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
    except FileNotFoundError as e:
        logger.error(f"System status check file not found: {e}")
        return {
            "status": "error",
            "error": f"System status check file not found: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Unexpected error in get_system_status: {e}")
        return {
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
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
            logger.warning(f"Unknown command received: {command_type}")
            return {
                "status": "error",
                "error": f"Unknown command: {command_type}",
                "timestamp": datetime.now().isoformat()
            }
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed in execute_command: {e}")
        return {
            "status": "error",
            "error": f"API request failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Unexpected error in execute_command: {e}")
        return {
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
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
        logger.info("EOF received, ending MCP server")
        pass
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in MCP request: {e}")
        error_response = {
            "id": request.get("id") if 'request' in locals() else None,
            "error": {
                "message": f"Invalid JSON format: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        }
        print(json.dumps(error_response))
        sys.stdout.flush()
    except Exception as e:
        logger.error(f"Unexpected error in handle_mcp_request: {e}")
        error_response = {
            "id": request.get("id") if 'request' in locals() else None,
            "error": {
                "message": f"Unexpected error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        }
        print(json.dumps(error_response))
        sys.stdout.flush()

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    logger.info("WAWAGOT.AI MCP Server starting...")
    
    # Simple MCP server loop
    while True:
        try:
            handle_mcp_request()
        except KeyboardInterrupt:
            logger.info("MCP Server stopped by user")
            break
        except Exception as e:
            logger.error(f"Critical error in MCP server main loop: {e}")
            print(json.dumps({
                "error": f"Critical server error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }))
            sys.stdout.flush()