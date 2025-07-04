
"""
Configuration Manager
จัดการการตั้งค่าทั้งหมด
"""

import json
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    def __init__(self):
        self.config_dir = Path("config")
        self.configs = {}
        self.load_all_configs()
        
    def load_all_configs(self):
        """โหลดการตั้งค่าทั้งหมด"""
        config_files = ['system.json', 'chrome.json', 'ai.json']
        
        for config_file in config_files:
            config_path = self.config_dir / config_file
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.configs[config_file.replace('.json', '')] = json.load(f)
                    
    def get_config(self, name: str) -> Dict[str, Any]:
        """ดึงการตั้งค่า"""
        return self.configs.get(name, {})
        
    def update_config(self, name: str, config: Dict[str, Any]):
        """อัปเดตการตั้งค่า"""
        self.configs[name] = config
        self.save_config(name)
        
    def save_config(self, name: str):
        """บันทึกการตั้งค่า"""
        config_path = self.config_dir / f"{name}.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.configs[name], f, indent=2, ensure_ascii=False)
