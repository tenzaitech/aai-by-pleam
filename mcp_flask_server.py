#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAWAGOT.AI Flask MCP Server for Cursor
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import requests
import subprocess
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

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

@app.route('/tools', methods=['GET'])
def tools():
    """MCP Tools endpoint - returns available tools"""
    return jsonify({
        "tools": [
            {
                "name": "dashboard_status",
                "description": "Get current dashboard status",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "start_dashboard",
                "description": "Start the dashboard server",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "system_status",
                "description": "Get system status information",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "custom_api",
                "description": "Call custom API endpoint",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "endpoint": {
                            "type": "string",
                            "description": "API endpoint to call (e.g., /api/status)"
                        }
                    },
                    "required": ["endpoint"]
                }
            }
        ]
    })

@app.route('/execute', methods=['POST'])
def execute():
    """Execute MCP tool"""
    try:
        data = request.get_json()
        command = data.get("command")
        params = data.get("params", {})
        
        if command == "dashboard_status":
            result = get_dashboard_status()
        elif command == "start_dashboard":
            result = start_dashboard()
        elif command == "system_status":
            result = get_system_status()
        elif command == "custom_api":
            endpoint = params.get("endpoint", "/api/status")
            response = requests.get(f'http://localhost:5000{endpoint}', timeout=5)
            result = {
                "status": "success",
                "data": response.json(),
                "timestamp": datetime.now().isoformat()
            }
        else:
            result = {
                "status": "error",
                "error": f"Unknown command: {command}",
                "timestamp": datetime.now().isoformat()
            }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server": "WAWAGOT.AI MCP Flask Server"
    })

if __name__ == '__main__':
    print("Starting WAWAGOT.AI MCP Flask Server on port 5001...")
    print("Available endpoints:")
    print("  GET  /tools     - List available MCP tools")
    print("  POST /execute   - Execute MCP tool")
    print("  GET  /health    - Health check")
    print("")
    print("For Cursor integration, ensure .cursor/mcp.json points to:")
    print("  http://localhost:5001")
    print("")
    app.run(host='0.0.0.0', port=5001, debug=True) 