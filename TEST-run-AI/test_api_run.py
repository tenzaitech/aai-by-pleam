import requests
import json

BASE_URL = "http://localhost:8000"


def print_result(title, resp):
    print(f"\n=== {title} ===")
    print(f"Status: {resp.status_code}")
    try:
        print(json.dumps(resp.json(), ensure_ascii=False, indent=2))
    except Exception:
        print(resp.text)


def test_health():
    resp = requests.get(f"{BASE_URL}/health")
    print_result("Health Check", resp)


def test_command():
    data = {
        "command": "เปิดเว็บ Google และค้นหาข้อมูล",
        "language": "thai",
        "parameters": {}
    }
    resp = requests.post(f"{BASE_URL}/api/command", json=data)
    print_result("AI Command (Thai)", resp)


def test_chrome():
    data = {
        "action": "navigate",
        "url": "https://www.google.com",
        "parameters": {}
    }
    resp = requests.post(f"{BASE_URL}/api/chrome", json=data)
    print_result("Chrome Navigate", resp)


def test_ai():
    data = {
        "prompt": "What is the capital of Thailand?",
        "context": "",
        "use_vision": False
    }
    resp = requests.post(f"{BASE_URL}/api/ai", json=data)
    print_result("AI Text Processing", resp)


def test_knowledge():
    # Store knowledge
    data = {"content": "กรุงเทพมหานครเป็นเมืองหลวงของประเทศไทย", "timestamp": "2024-01-01T12:00:00"}
    resp = requests.post(f"{BASE_URL}/api/knowledge", json=data)
    print_result("Store Knowledge", resp)
    # Search knowledge
    resp = requests.get(f"{BASE_URL}/api/knowledge?query=กรุงเทพมหานคร")
    print_result("Search Knowledge", resp)


def test_config():
    # Get config
    resp = requests.get(f"{BASE_URL}/api/config")
    print_result("Get Config", resp)
    # Update config
    data = {
        "chrome_headless": True,
        "ai_enabled": True,
        "thai_processing": True,
        "parallel_processing": True
    }
    resp = requests.post(f"{BASE_URL}/api/config", json=data)
    print_result("Update Config", resp)


def test_system_control():
    # Restart system
    resp = requests.post(f"{BASE_URL}/api/system/restart")
    print_result("System Restart", resp)
    # Shutdown system
    # resp = requests.post(f"{BASE_URL}/api/system/shutdown")
    # print_result("System Shutdown", resp)


def main():
    test_health()
    test_command()
    test_chrome()
    test_ai()
    test_knowledge()
    test_config()
    test_system_control()
    print("\n=== All API tests completed ===\n")

if __name__ == "__main__":
    main() 