#!/usr/bin/env python3
"""
WAWAGOT V.2 Simple Test Runner
Tests API endpoints without complex setup
"""

import requests
import time
import sys

def test_api_server():
    print("🧪 WAWAGOT V.2 Simple Test Runner")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health Check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to API server")
        print("   💡 Make sure to run 'python launch_simple.py' first")
        return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 2: Root endpoint
    print("2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Root endpoint: {data.get('message', 'OK')}")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Root endpoint error: {e}")
    
    # Test 3: AI Command endpoint
    print("3. Testing AI command endpoint...")
    try:
        payload = {
            "command": "test command",
            "parameters": {},
            "language": "thai"
        }
        response = requests.post(f"{base_url}/api/command", json=payload, timeout=10)
        if response.status_code == 200:
            print("   ✅ AI command endpoint working")
        else:
            print(f"   ⚠️ AI command endpoint: {response.status_code}")
    except Exception as e:
        print(f"   ❌ AI command error: {e}")
    
    print("\n🎉 Basic API tests completed!")
    print("   API server is running and responding")
    return True

if __name__ == "__main__":
    success = test_api_server()
    sys.exit(0 if success else 1) 