#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Cursor Integration System
ระบบเชื่อมต่อระหว่าง Gemini CLI, Cursor และ WebApp

Flow: User Command (WebApp) >> Gemini CLI >> Cursor/เครื่องมือ >> Gemini CLI >> WebApp (ผลลัพธ์/รายงาน)
"""

import os
import json
import subprocess
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
import threading
import time

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gemini_cursor_integration.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GeminiCursorIntegration:
    """ระบบเชื่อมต่อ Gemini CLI, Cursor และ WebApp"""
    
    def __init__(self, api_key: str = None):
        """Initialize ระบบ"""
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("ต้องตั้งค่า GOOGLE_API_KEY")
        
        # ตั้งค่า Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # ตั้งค่า Cursor path (Windows)
        self.cursor_path = r"C:\Users\{}\AppData\Local\Programs\cursor\Cursor.exe".format(
            os.getenv('USERNAME', 'pleam')
        )
        
        # เก็บประวัติการทำงาน
        self.work_history = []
        self.active_tasks = {}
        
        logger.info("Gemini Cursor Integration เริ่มต้นสำเร็จ")
    
    def analyze_user_command(self, user_command: str) -> Dict[str, Any]:
        """วิเคราะห์คำสั่งของผู้ใช้ผ่าน Gemini"""
        try:
            prompt = f"""
            วิเคราะห์คำสั่งนี้: "{user_command}"
            
            ให้ตอบในรูปแบบ JSON:
            {{
                "action_type": "cursor_command|file_operation|system_command|web_automation|data_analysis",
                "target": "ไฟล์หรือโปรแกรมที่ต้องการทำงาน",
                "operation": "การทำงานที่ต้องการ",
                "parameters": {{"param1": "value1"}},
                "estimated_time": "เวลาที่คาดว่าจะใช้ (วินาที)",
                "risk_level": "low|medium|high",
                "description": "คำอธิบายการทำงาน"
            }}
            
            ตัวอย่าง:
            - "เปิดไฟล์ test.py ใน Cursor" -> {{"action_type": "cursor_command", "target": "test.py", ...}}
            - "รันคำสั่ง python script.py" -> {{"action_type": "system_command", "target": "script.py", ...}}
            """
            
            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            logger.info(f"วิเคราะห์คำสั่ง: {result}")
            return result
            
        except Exception as e:
            logger.error(f"เกิดข้อผิดพลาดในการวิเคราะห์คำสั่ง: {e}")
            return {
                "action_type": "unknown",
                "target": user_command,
                "operation": "analyze",
                "parameters": {},
                "estimated_time": 5,
                "risk_level": "medium",
                "description": "ไม่สามารถวิเคราะห์คำสั่งได้"
            }
    
    def execute_cursor_command(self, target: str, operation: str) -> Dict[str, Any]:
        """รันคำสั่งใน Cursor"""
        try:
            if operation == "open_file":
                # เปิดไฟล์ใน Cursor
                cmd = f'"{self.cursor_path}" "{target}"'
                subprocess.Popen(cmd, shell=True)
                return {
                    "status": "success",
                    "message": f"เปิดไฟล์ {target} ใน Cursor สำเร็จ",
                    "command": cmd
                }
            
            elif operation == "open_folder":
                # เปิดโฟลเดอร์ใน Cursor
                cmd = f'"{self.cursor_path}" "{target}"'
                subprocess.Popen(cmd, shell=True)
                return {
                    "status": "success", 
                    "message": f"เปิดโฟลเดอร์ {target} ใน Cursor สำเร็จ",
                    "command": cmd
                }
            
            else:
                return {
                    "status": "error",
                    "message": f"ไม่รองรับการทำงาน: {operation}"
                }
                
        except Exception as e:
            logger.error(f"เกิดข้อผิดพลาดในการรัน Cursor: {e}")
            return {
                "status": "error",
                "message": f"เกิดข้อผิดพลาด: {str(e)}"
            }
    
    def execute_system_command(self, command: str) -> Dict[str, Any]:
        """รันคำสั่งระบบ"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "command": command
            }
            
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "คำสั่งใช้เวลานานเกินไป (timeout)"
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"เกิดข้อผิดพลาด: {str(e)}"
            }
    
    def execute_web_automation(self, target: str, operation: str) -> Dict[str, Any]:
        """รัน Web Automation"""
        try:
            # ใช้ Selenium หรือ Playwright สำหรับ web automation
            if operation == "open_url":
                import webbrowser
                webbrowser.open(target)
                return {
                    "status": "success",
                    "message": f"เปิด URL: {target} สำเร็จ"
                }
            
            else:
                return {
                    "status": "error",
                    "message": f"ไม่รองรับ web automation: {operation}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"เกิดข้อผิดพลาด: {str(e)}"
            }
    
    def generate_report(self, task_id: str, results: List[Dict]) -> Dict[str, Any]:
        """สร้างรายงานผ่าน Gemini"""
        try:
            # สร้าง prompt สำหรับรายงาน
            prompt = f"""
            สร้างรายงานการทำงาน Task ID: {task_id}
            
            ผลลัพธ์การทำงาน:
            {json.dumps(results, indent=2, ensure_ascii=False)}
            
            ให้สร้างรายงานในรูปแบบ JSON:
            {{
                "summary": "สรุปการทำงาน",
                "status": "success|partial|failed",
                "details": [
                    {{
                        "step": "ขั้นตอนที่ 1",
                        "result": "ผลลัพธ์",
                        "status": "success|error"
                    }}
                ],
                "recommendations": ["คำแนะนำ 1", "คำแนะนำ 2"],
                "next_steps": ["ขั้นตอนต่อไป 1", "ขั้นตอนต่อไป 2"],
                "execution_time": "เวลาที่ใช้",
                "timestamp": "เวลาที่เสร็จสิ้น"
            }}
            """
            
            response = self.model.generate_content(prompt)
            report = json.loads(response.text)
            
            # เพิ่มข้อมูลเพิ่มเติม
            report["task_id"] = task_id
            report["total_steps"] = len(results)
            report["success_count"] = sum(1 for r in results if r.get("status") == "success")
            
            return report
            
        except Exception as e:
            logger.error(f"เกิดข้อผิดพลาดในการสร้างรายงาน: {e}")
            return {
                "task_id": task_id,
                "summary": "เกิดข้อผิดพลาดในการสร้างรายงาน",
                "status": "error",
                "details": [],
                "recommendations": ["ตรวจสอบ log files"],
                "next_steps": ["ติดต่อผู้ดูแลระบบ"],
                "execution_time": "unknown",
                "timestamp": datetime.now().isoformat()
            }
    
    async def process_user_command(self, user_command: str, task_id: str = None) -> Dict[str, Any]:
        """ประมวลผลคำสั่งของผู้ใช้แบบ async"""
        if not task_id:
            task_id = f"task_{int(time.time())}"
        
        try:
            # 1. วิเคราะห์คำสั่งผ่าน Gemini
            analysis = self.analyze_user_command(user_command)
            
            # 2. ประมวลผลตามประเภทการทำงาน
            results = []
            
            if analysis["action_type"] == "cursor_command":
                result = self.execute_cursor_command(
                    analysis["target"], 
                    analysis["operation"]
                )
                results.append(result)
            
            elif analysis["action_type"] == "system_command":
                result = self.execute_system_command(analysis["target"])
                results.append(result)
            
            elif analysis["action_type"] == "web_automation":
                result = self.execute_web_automation(
                    analysis["target"], 
                    analysis["operation"]
                )
                results.append(result)
            
            # 3. สร้างรายงานผ่าน Gemini
            report = self.generate_report(task_id, results)
            
            # 4. บันทึกประวัติ
            self.work_history.append({
                "task_id": task_id,
                "user_command": user_command,
                "analysis": analysis,
                "results": results,
                "report": report,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "task_id": task_id,
                "status": "completed",
                "analysis": analysis,
                "results": results,
                "report": report
            }
            
        except Exception as e:
            logger.error(f"เกิดข้อผิดพลาดในการประมวลผล: {e}")
            return {
                "task_id": task_id,
                "status": "error",
                "message": str(e)
            }

# Flask WebApp
app = Flask(__name__)
app.config['SECRET_KEY'] = 'gemini_cursor_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# สร้าง instance ของระบบ
try:
    integration = GeminiCursorIntegration()
    logger.info("ระบบ Gemini Cursor Integration พร้อมใช้งาน")
except Exception as e:
    logger.error(f"ไม่สามารถเริ่มต้นระบบได้: {e}")
    integration = None

@app.route('/')
def index():
    """หน้าแรกของ WebApp"""
    return render_template('gemini_cursor_interface.html')

@app.route('/api/command', methods=['POST'])
def submit_command():
    """รับคำสั่งจากผู้ใช้"""
    try:
        data = request.get_json()
        user_command = data.get('command', '')
        
        if not user_command:
            return jsonify({"error": "ไม่พบคำสั่ง"}), 400
        
        if not integration:
            return jsonify({"error": "ระบบไม่พร้อมใช้งาน"}), 500
        
        # สร้าง task ID
        task_id = f"task_{int(time.time())}"
        
        # เริ่มประมวลผลแบบ async
        def process_task():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                integration.process_user_command(user_command, task_id)
            )
            loop.close()
            
            # ส่งผลลัพธ์ผ่าน WebSocket
            socketio.emit('task_completed', result)
        
        # รันใน thread แยก
        thread = threading.Thread(target=process_task)
        thread.start()
        
        return jsonify({
            "status": "processing",
            "task_id": task_id,
            "message": "กำลังประมวลผลคำสั่ง..."
        })
        
    except Exception as e:
        logger.error(f"เกิดข้อผิดพลาด: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/history')
def get_history():
    """ดึงประวัติการทำงาน"""
    if not integration:
        return jsonify({"error": "ระบบไม่พร้อมใช้งาน"}), 500
    
    return jsonify({
        "history": integration.work_history[-10:]  # 10 รายการล่าสุด
    })

@app.route('/api/status')
def get_status():
    """ดึงสถานะระบบ"""
    return jsonify({
        "status": "running" if integration else "error",
        "active_tasks": len(integration.active_tasks) if integration else 0,
        "total_history": len(integration.work_history) if integration else 0
    })

@socketio.on('connect')
def handle_connect():
    """เมื่อ WebSocket เชื่อมต่อ"""
    emit('status', {'message': 'เชื่อมต่อสำเร็จ'})

@socketio.on('disconnect')
def handle_disconnect():
    """เมื่อ WebSocket หลุดการเชื่อมต่อ"""
    logger.info('Client disconnected')

if __name__ == '__main__':
    logger.info("เริ่มต้น Gemini Cursor Integration WebApp")
    socketio.run(app, host='0.0.0.0', port=8002, debug=True) 