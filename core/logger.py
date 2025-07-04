"""
Advanced Logging System for WAWAGOT.AI
ระบบ Logging ขั้นสูงสำหรับการ Debug และ Monitoring
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import json

class WAWALogger:
    def __init__(self, name: str = "wawagot", log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # สร้าง loggers
        self.system_logger = self._create_logger("system", "system.log")
        self.error_logger = self._create_logger("error", "error.log")
        self.performance_logger = self._create_logger("performance", "performance.log")
        self.ai_logger = self._create_logger("ai", "ai.log")
        
    def _create_logger(self, logger_name: str, filename: str) -> logging.Logger:
        """สร้าง logger สำหรับแต่ละประเภท"""
        logger = logging.getLogger(f"{self.name}.{logger_name}")
        logger.setLevel(logging.DEBUG)
        
        # ป้องกันการสร้าง handler ซ้ำ
        if logger.handlers:
            return logger
            
        # File Handler
        file_handler = logging.FileHandler(self.log_dir / filename, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_system(self, message: str, level: str = "info"):
        """บันทึก log ระบบ"""
        getattr(self.system_logger, level.lower())(f"🖥️ {message}")
    
    def log_error(self, error: Exception, context: str = ""):
        """บันทึก error"""
        error_msg = f"❌ {context}: {str(error)}" if context else f"❌ {str(error)}"
        self.error_logger.error(error_msg, exc_info=True)
    
    def log_performance(self, operation: str, duration: float, details: dict = None):
        """บันทึก performance metrics"""
        perf_data = {
            "operation": operation,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.performance_logger.info(f"⚡ {operation}: {duration:.3f}s | {json.dumps(details or {})}")
    
    def log_ai(self, operation: str, input_data: dict, output_data: dict, confidence: float):
        """บันทึก AI operations"""
        ai_data = {
            "operation": operation,
            "input": input_data,
            "output": output_data,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
        self.ai_logger.info(f"🤖 {operation} (confidence: {confidence:.2f})")
    
    def get_system_status(self) -> dict:
        """ดึงสถานะระบบจาก logs"""
        try:
            status = {
                "last_system_log": self._get_last_log_entry("system.log"),
                "last_error": self._get_last_log_entry("error.log"),
                "performance_summary": self._get_performance_summary(),
                "ai_operations": self._get_ai_summary()
            }
            return status
        except Exception as e:
            return {"error": f"ไม่สามารถดึงสถานะได้: {e}"}
    
    def _get_last_log_entry(self, filename: str) -> Optional[str]:
        """ดึง log entry ล่าสุด"""
        log_file = self.log_dir / filename
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                return lines[-1].strip() if lines else None
        return None
    
    def _get_performance_summary(self) -> dict:
        """สรุป performance metrics"""
        perf_file = self.log_dir / "performance.log"
        if not perf_file.exists():
            return {"total_operations": 0, "avg_duration": 0}
        
        try:
            with open(perf_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            operations = []
            for line in lines:
                if "⚡" in line:
                    # Parse duration from log line
                    try:
                        duration_str = line.split(": ")[1].split("s")[0]
                        duration = float(duration_str)
                        operations.append(duration)
                    except:
                        continue
            
            if operations:
                return {
                    "total_operations": len(operations),
                    "avg_duration": sum(operations) / len(operations),
                    "min_duration": min(operations),
                    "max_duration": max(operations)
                }
        except Exception as e:
            return {"error": f"ไม่สามารถสรุป performance ได้: {e}"}
        
        return {"total_operations": 0, "avg_duration": 0}
    
    def _get_ai_summary(self) -> dict:
        """สรุป AI operations"""
        ai_file = self.log_dir / "ai.log"
        if not ai_file.exists():
            return {"total_operations": 0, "avg_confidence": 0}
        
        try:
            with open(ai_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            confidences = []
            operations = []
            for line in lines:
                if "🤖" in line and "confidence:" in line:
                    try:
                        # Extract confidence value
                        conf_str = line.split("confidence: ")[1].split(")")[0]
                        confidence = float(conf_str)
                        confidences.append(confidence)
                        
                        # Extract operation name
                        op_name = line.split("🤖 ")[1].split(" (")[0]
                        operations.append(op_name)
                    except:
                        continue
            
            if confidences:
                return {
                    "total_operations": len(operations),
                    "avg_confidence": sum(confidences) / len(confidences),
                    "min_confidence": min(confidences),
                    "max_confidence": max(confidences),
                    "recent_operations": operations[-5:]  # 5 operations ล่าสุด
                }
        except Exception as e:
            return {"error": f"ไม่สามารถสรุป AI operations ได้: {e}"}
        
        return {"total_operations": 0, "avg_confidence": 0}

# Global logger instance
wawa_logger = WAWALogger() 