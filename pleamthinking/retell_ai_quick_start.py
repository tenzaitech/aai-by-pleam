#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Retell.AI Quick Start Implementation for WAWAGOT.AI
===============================================================================
Created: 2024-12-19
Purpose: Simple implementation example for Retell.AI integration
===============================================================================
"""

import os
import asyncio
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RetellAIQuickStart:
    """Retell.AI Quick Start Implementation"""
    
    def __init__(self):
        self.api_key = os.getenv("RETELL_API_KEY")
        self.from_number = os.getenv("RETELL_FROM_NUMBER", "+14157774444")
        self.base_url = "https://api.retellai.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if not self.api_key:
            print("⚠️  Warning: RETELL_API_KEY not found in environment variables")
            print("   Please set RETELL_API_KEY in your .env file")
    
    def create_phone_call(self, to_number, agent_id=None):
        """สร้างการโทรออก"""
        print(f"📞 Creating call to {to_number}...")
        
        payload = {
            "from_number": self.from_number,
            "to_number": to_number
        }
        
        if agent_id:
            payload["agent_id"] = agent_id
            print(f"🤖 Using agent: {agent_id}")
        
        try:
            response = requests.post(
                f"{self.base_url}/create-phone-call",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Call created successfully!")
                print(f"   Call ID: {result.get('call_id')}")
                print(f"   Agent ID: {result.get('agent_id')}")
                return result
            else:
                print(f"❌ Failed to create call: {response.status_code}")
                print(f"   Response: {response.text}")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Error creating call: {e}")
            return {"error": str(e)}
    
    def get_call_status(self, call_id):
        """ดูสถานะการโทร"""
        print(f"📊 Checking status for call {call_id}...")
        
        try:
            response = requests.get(
                f"{self.base_url}/calls/{call_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                status = result.get("call_status", "unknown")
                duration = result.get("duration_ms", 0)
                
                print(f"✅ Call status: {status}")
                if duration > 0:
                    print(f"   Duration: {duration/1000:.1f} seconds")
                
                return result
            else:
                print(f"❌ Failed to get call status: {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Error getting call status: {e}")
            return {"error": str(e)}
    
    def end_call(self, call_id):
        """จบการโทร"""
        print(f"🔚 Ending call {call_id}...")
        
        try:
            response = requests.post(
                f"{self.base_url}/calls/{call_id}/end",
                headers=self.headers
            )
            
            if response.status_code == 200:
                print(f"✅ Call ended successfully!")
                return response.json()
            else:
                print(f"❌ Failed to end call: {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Error ending call: {e}")
            return {"error": str(e)}
    
    def monitor_call(self, call_id, max_duration=300):
        """ติดตามการโทรแบบ real-time"""
        print(f"👀 Monitoring call {call_id}...")
        print(f"   Max duration: {max_duration} seconds")
        
        start_time = datetime.now()
        
        while True:
            try:
                status = self.get_call_status(call_id)
                
                if "error" in status:
                    print(f"❌ Monitoring error: {status['error']}")
                    break
                
                call_status = status.get("call_status", "unknown")
                duration = status.get("duration_ms", 0) / 1000
                
                print(f"   Status: {call_status} | Duration: {duration:.1f}s")
                
                # ตรวจสอบการจบ
                if call_status in ["ended", "failed"]:
                    print(f"✅ Call completed with status: {call_status}")
                    
                    # แสดงผลการวิเคราะห์
                    analysis = status.get("call_analysis", {})
                    if analysis:
                        print(f"   Summary: {analysis.get('call_summary', 'N/A')}")
                        print(f"   Sentiment: {analysis.get('user_sentiment', 'N/A')}")
                        print(f"   Success: {analysis.get('call_successful', 'N/A')}")
                    
                    break
                
                # ตรวจสอบเวลาสูงสุด
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed > max_duration:
                    print(f"⏰ Max duration reached ({max_duration}s), ending call...")
                    self.end_call(call_id)
                    break
                
                # รอ 5 วินาทีก่อนตรวจสอบอีกครั้ง
                asyncio.sleep(5)
                
            except KeyboardInterrupt:
                print(f"\n🛑 Monitoring interrupted by user")
                self.end_call(call_id)
                break
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                break
    
    def get_call_analytics(self, call_id):
        """ดึงการวิเคราะห์การโทร"""
        print(f"📈 Getting analytics for call {call_id}...")
        
        status = self.get_call_status(call_id)
        
        if "error" in status:
            return status
        
        # สร้างการวิเคราะห์
        analytics = {
            "call_id": call_id,
            "status": status.get("call_status"),
            "duration_seconds": status.get("duration_ms", 0) / 1000,
            "transcript": status.get("transcript", ""),
            "analysis": status.get("call_analysis", {}),
            "recording_url": status.get("recording_url"),
            "cost": status.get("call_cost", {})
        }
        
        print(f"✅ Analytics retrieved:")
        print(f"   Duration: {analytics['duration_seconds']:.1f} seconds")
        print(f"   Status: {analytics['status']}")
        
        if analytics["analysis"]:
            print(f"   Sentiment: {analytics['analysis'].get('user_sentiment', 'N/A')}")
            print(f"   Success: {analytics['analysis'].get('call_successful', 'N/A')}")
        
        return analytics

def main():
    """Main function for quick start demo"""
    print("🚀 Retell.AI Quick Start Demo")
    print("=" * 50)
    
    # สร้าง instance
    retell = RetellAIQuickStart()
    
    # ตรวจสอบ API key
    if not retell.api_key:
        print("❌ Cannot proceed without API key")
        return
    
    # ตัวอย่างการใช้งาน
    print("\n📋 Example Usage:")
    print("1. Create a phone call")
    print("2. Monitor call status")
    print("3. Get call analytics")
    print("4. End call")
    
    # ตัวอย่างหมายเลขโทร (ใช้หมายเลขทดสอบ)
    test_number = "+15551234567"  # หมายเลขทดสอบ
    
    print(f"\n📞 Test phone number: {test_number}")
    print("   (This is a test number - replace with real number for actual calls)")
    
    # สร้างการโทร
    print(f"\n1️⃣ Creating call...")
    call_result = retell.create_phone_call(test_number)
    
    if "error" in call_result:
        print(f"❌ Failed to create call: {call_result['error']}")
        return
    
    call_id = call_result.get("call_id")
    print(f"✅ Call created with ID: {call_id}")
    
    # ติดตามการโทร (จำกัดเวลา 30 วินาทีสำหรับ demo)
    print(f"\n2️⃣ Monitoring call (30 seconds max)...")
    retell.monitor_call(call_id, max_duration=30)
    
    # ดึงการวิเคราะห์
    print(f"\n3️⃣ Getting call analytics...")
    analytics = retell.get_call_analytics(call_id)
    
    if "error" not in analytics:
        print(f"✅ Analytics retrieved successfully")
        
        # แสดง transcript (ถ้ามี)
        transcript = analytics.get("transcript", "")
        if transcript:
            print(f"\n📝 Transcript:")
            print(f"   {transcript[:200]}..." if len(transcript) > 200 else f"   {transcript}")
    
    print(f"\n🎉 Demo completed!")

def test_api_connection():
    """ทดสอบการเชื่อมต่อ API"""
    print("🔍 Testing Retell.AI API connection...")
    
    retell = RetellAIQuickStart()
    
    if not retell.api_key:
        print("❌ No API key found")
        return False
    
    try:
        # ทดสอบการเชื่อมต่อโดยดูรายการ agents
        response = requests.get(
            f"{retell.base_url}/agents",
            headers=retell.headers
        )
        
        if response.status_code == 200:
            print("✅ API connection successful!")
            agents = response.json()
            print(f"   Available agents: {len(agents)}")
            return True
        else:
            print(f"❌ API connection failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API connection error: {e}")
        return False

if __name__ == "__main__":
    # ทดสอบการเชื่อมต่อก่อน
    if test_api_connection():
        # รัน demo
        main()
    else:
        print("\n❌ Cannot run demo without valid API connection")
        print("   Please check your RETELL_API_KEY and internet connection") 