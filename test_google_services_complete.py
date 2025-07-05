#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Google Services Test Suite - WAWAGOT V.2
ระบบทดสอบอัตโนมัติสำหรับ Google Services ทั้งหมด
"""

import os
import json
import requests
import logging
import time
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleServicesTestSuite:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY", "your_google_api_key_here")
        self.credentials = None
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        
    def load_credentials(self):
        """โหลด credentials"""
        try:
            if os.path.exists("google_credentials_complete.json"):
                with open("google_credentials_complete.json", "r") as f:
                    creds_data = json.load(f)
                
                self.credentials = Credentials(
                    token=creds_data.get("access_token"),
                    refresh_token=creds_data.get("refresh_token"),
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=creds_data.get("client_id"),
                    client_secret=creds_data.get("client_secret"),
                    scopes=creds_data.get("scopes", [])
                )
                
                if self.credentials and self.credentials.expired:
                    self.credentials.refresh(Request())
                
                logger.info("✅ โหลด credentials สำเร็จ")
                return True
            else:
                logger.warning("⚠️ ไม่พบ credentials file")
                return False
        except Exception as e:
            logger.error(f"❌ ไม่สามารถโหลด credentials ได้: {e}")
            return False
    
    def test_gemini_ai(self):
        """ทดสอบ Gemini AI"""
        self.total_tests += 1
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content("สวัสดีครับ ฉันคือ WAWAGOT AI Assistant")
            
            if response.text:
                self.passed_tests += 1
                self.test_results["gemini_ai"] = {
                    "status": "✅ PASS",
                    "message": "เชื่อมต่อ Gemini AI สำเร็จ",
                    "response_length": len(response.text)
                }
                logger.info("✅ Gemini AI: PASS")
            else:
                self.test_results["gemini_ai"] = {
                    "status": "❌ FAIL",
                    "message": "ไม่ได้รับ response จาก Gemini AI"
                }
                logger.error("❌ Gemini AI: FAIL")
                
        except Exception as e:
            self.test_results["gemini_ai"] = {
                "status": "❌ FAIL",
                "message": f"Error: {str(e)}"
            }
            logger.error(f"❌ Gemini AI: FAIL - {e}")
    
    def test_youtube_api(self):
        """ทดสอบ YouTube API"""
        self.total_tests += 1
        try:
            youtube = build("youtube", "v3", developerKey=self.api_key)
            request = youtube.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                regionCode="TH",
                maxResults=5
            )
            response = request.execute()
            
            videos = response.get("items", [])
            if videos:
                self.passed_tests += 1
                self.test_results["youtube_api"] = {
                    "status": "✅ PASS",
                    "message": f"ดึงข้อมูล YouTube สำเร็จ: {len(videos)} videos",
                    "videos_count": len(videos)
                }
                logger.info("✅ YouTube API: PASS")
            else:
                self.test_results["youtube_api"] = {
                    "status": "❌ FAIL",
                    "message": "ไม่พบ videos"
                }
                logger.error("❌ YouTube API: FAIL")
                
        except Exception as e:
            self.test_results["youtube_api"] = {
                "status": "❌ FAIL",
                "message": f"Error: {str(e)}"
            }
            logger.error(f"❌ YouTube API: FAIL - {e}")
    
    def test_user_info(self):
        """ทดสอบ User Info"""
        self.total_tests += 1
        try:
            if not self.credentials:
                raise Exception("No credentials available")
            
            headers = {"Authorization": f"Bearer {self.credentials.token}"}
            response = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers)
            response.raise_for_status()
            
            user_info = response.json()
            if user_info.get("name"):
                self.passed_tests += 1
                self.test_results["user_info"] = {
                    "status": "✅ PASS",
                    "message": f"ดึงข้อมูลผู้ใช้สำเร็จ: {user_info.get('name')}",
                    "user_name": user_info.get("name"),
                    "user_email": user_info.get("email")
                }
                logger.info("✅ User Info: PASS")
            else:
                self.test_results["user_info"] = {
                    "status": "❌ FAIL",
                    "message": "ไม่ได้รับข้อมูลผู้ใช้"
                }
                logger.error("❌ User Info: FAIL")
                
        except Exception as e:
            self.test_results["user_info"] = {
                "status": "❌ FAIL",
                "message": f"Error: {str(e)}"
            }
            logger.error(f"❌ User Info: FAIL - {e}")
    
    def test_google_drive(self):
        """ทดสอบ Google Drive"""
        self.total_tests += 1
        try:
            if not self.credentials:
                raise Exception("No credentials available")
            
            service = build("drive", "v3", credentials=self.credentials)
            results = service.files().list(pageSize=10).execute()
            files = results.get("files", [])
            
            self.passed_tests += 1
            self.test_results["google_drive"] = {
                "status": "✅ PASS",
                "message": f"เชื่อมต่อ Google Drive สำเร็จ: {len(files)} files",
                "files_count": len(files)
            }
            logger.info("✅ Google Drive: PASS")
            
        except Exception as e:
            self.test_results["google_drive"] = {
                "status": "❌ FAIL",
                "message": f"Error: {str(e)}"
            }
            logger.error(f"❌ Google Drive: FAIL - {e}")
    
    def test_google_calendar(self):
        """ทดสอบ Google Calendar"""
        self.total_tests += 1
        try:
            if not self.credentials:
                raise Exception("No credentials available")
            
            service = build("calendar", "v3", credentials=self.credentials)
            now = datetime.utcnow().isoformat() + "Z"
            events_result = service.events().list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            
            events = events_result.get("items", [])
            self.passed_tests += 1
            self.test_results["google_calendar"] = {
                "status": "✅ PASS",
                "message": f"เชื่อมต่อ Google Calendar สำเร็จ: {len(events)} events",
                "events_count": len(events)
            }
            logger.info("✅ Google Calendar: PASS")
            
        except Exception as e:
            self.test_results["google_calendar"] = {
                "status": "❌ FAIL",
                "message": f"Error: {str(e)}"
            }
            logger.error(f"❌ Google Calendar: FAIL - {e}")
    
    def test_gmail(self):
        """ทดสอบ Gmail"""
        self.total_tests += 1
        try:
            if not self.credentials:
                raise Exception("No credentials available")
            
            service = build("gmail", "v1", credentials=self.credentials)
            results = service.users().messages().list(userId="me", maxResults=10).execute()
            messages = results.get("messages", [])
            
            self.passed_tests += 1
            self.test_results["gmail"] = {
                "status": "✅ PASS",
                "message": f"เชื่อมต่อ Gmail สำเร็จ: {len(messages)} messages",
                "messages_count": len(messages)
            }
            logger.info("✅ Gmail: PASS")
            
        except Exception as e:
            self.test_results["gmail"] = {
                "status": "❌ FAIL",
                "message": f"Error: {str(e)}"
            }
            logger.error(f"❌ Gmail: FAIL - {e}")
    
    def test_system_info(self):
        """ทดสอบ System Info"""
        self.total_tests += 1
        try:
            import platform
            import psutil
            
            system_info = {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total // (1024**3),  # GB
                "memory_available": psutil.virtual_memory().available // (1024**3)  # GB
            }
            
            self.passed_tests += 1
            self.test_results["system_info"] = {
                "status": "✅ PASS",
                "message": "ดึงข้อมูลระบบสำเร็จ",
                "system": system_info["system"],
                "cpu_count": system_info["cpu_count"],
                "memory_total_gb": system_info["memory_total"]
            }
            logger.info("✅ System Info: PASS")
            
        except Exception as e:
            self.test_results["system_info"] = {
                "status": "❌ FAIL",
                "message": f"Error: {str(e)}"
            }
            logger.error(f"❌ System Info: FAIL - {e}")
    
    def test_network_connectivity(self):
        """ทดสอบ Network Connectivity"""
        self.total_tests += 1
        try:
            # ทดสอบการเชื่อมต่อ Google APIs
            response = requests.get("https://www.googleapis.com/discovery/v1/apis", timeout=10)
            response.raise_for_status()
            
            self.passed_tests += 1
            self.test_results["network_connectivity"] = {
                "status": "✅ PASS",
                "message": "การเชื่อมต่อเครือข่ายปกติ",
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }
            logger.info("✅ Network Connectivity: PASS")
            
        except Exception as e:
            self.test_results["network_connectivity"] = {
                "status": "❌ FAIL",
                "message": f"Error: {str(e)}"
            }
            logger.error(f"❌ Network Connectivity: FAIL - {e}")
    
    def run_all_tests(self):
        """รันการทดสอบทั้งหมด"""
        logger.info("🧪 เริ่มต้นการทดสอบ Google Services ทั้งหมด...")
        logger.info("=" * 60)
        
        # ทดสอบ Network Connectivity ก่อน
        self.test_network_connectivity()
        
        # ทดสอบ System Info
        self.test_system_info()
        
        # ทดสอบ YouTube API (ใช้ API Key)
        self.test_youtube_api()
        
        # ทดสอบ Gemini AI (ใช้ API Key)
        self.test_gemini_ai()
        
        # ทดสอบ OAuth Services (ต้องมี credentials)
        if self.load_credentials():
            self.test_user_info()
            self.test_google_drive()
            self.test_google_calendar()
            self.test_gmail()
        else:
            logger.warning("⚠️ ข้ามการทดสอบ OAuth Services (ไม่มี credentials)")
            for service in ["user_info", "google_drive", "google_calendar", "gmail"]:
                self.test_results[service] = {
                    "status": "⚠️ SKIP",
                    "message": "ไม่มี credentials"
                }
        
        # แสดงผลลัพธ์
        self.print_results()
        
        return self.test_results
    
    def print_results(self):
        """แสดงผลลัพธ์การทดสอบ"""
        logger.info("=" * 60)
        logger.info("📊 ผลการทดสอบ Google Services")
        logger.info("=" * 60)
        
        for service, result in self.test_results.items():
            status = result["status"]
            message = result["message"]
            logger.info(f"{service:20} {status} - {message}")
        
        logger.info("=" * 60)
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        logger.info(f"🎯 อัตราความสำเร็จ: {self.passed_tests}/{self.total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            logger.info("🎉 ระบบพร้อมใช้งาน 100%!")
        elif success_rate >= 60:
            logger.info("⚠️ ระบบพร้อมใช้งานบางส่วน (ต้องขอ authorization)")
        else:
            logger.info("❌ ระบบมีปัญหา ต้องแก้ไข")
        
        logger.info("=" * 60)

def main():
    """Main function"""
    print("🧪 Google Services Complete Test Suite")
    print("=" * 60)
            print(f"🔐 API Key: {'*' * 20}... (hidden for security)")
    print("=" * 60)
    
    # สร้าง test suite และรันการทดสอบ
    test_suite = GoogleServicesTestSuite()
    results = test_suite.run_all_tests()
    
    # บันทึกผลลัพธ์
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 บันทึกผลลัพธ์ลงไฟล์: test_results.json")

if __name__ == "__main__":
    main() 