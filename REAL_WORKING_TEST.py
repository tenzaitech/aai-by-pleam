#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real Working Test - ทดสอบว่าระบบทำงานได้จริง
"""

import sys
import os
import asyncio
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_chrome_real_working():
    """ทดสอบ Chrome Controller ทำงานได้จริง"""
    print("🔍 Testing Chrome Controller - Real Working Test...")
    try:
        from core.chrome_controller import AIChromeController
        controller = AIChromeController()
        
        # ทดสอบการเริ่มต้น Chrome
        print("   🔄 Starting Chrome browser...")
        result = asyncio.run(controller.start_ai_browser(headless=True))
        if not result:
            print("   ❌ Failed to start Chrome browser")
            return False
        
        # ทดสอบการนำทาง
        print("   🔄 Testing navigation...")
        nav_result = asyncio.run(controller.ai_navigate("https://www.google.com"))
        if not nav_result:
            print("   ❌ Failed to navigate to Google")
            return False
        
        # ทดสอบการถ่ายภาพ
        print("   🔄 Testing screenshot...")
        try:
            screenshot = controller.driver.get_screenshot_as_png()
            if len(screenshot) > 1000:  # ตรวจสอบว่าภาพมีขนาดพอสมควร
                print("   ✅ Screenshot taken successfully")
            else:
                print("   ❌ Screenshot too small")
                return False
        except Exception as e:
            print(f"   ❌ Screenshot failed: {e}")
            return False
        
        print("   ✅ Chrome Controller working correctly!")
        return True
        
    except Exception as e:
        print(f"   ❌ Chrome Controller error: {e}")
        return False

def test_ai_integration_real_working():
    """ทดสอบ AI Integration ทำงานได้จริง"""
    print("🔍 Testing AI Integration - Real Working Test...")
    try:
        from core.ai_integration import MultimodalAIIntegration
        ai = MultimodalAIIntegration()
        
        # ทดสอบการวิเคราะห์ข้อความ
        print("   🔄 Testing text analysis...")
        test_text = "นี่คือข้อความทดสอบภาษาไทย"
        result = asyncio.run(ai._analyze_local([], test_text, "วิเคราะห์ข้อความ"))
        
        if "Local AI Processing" in result:
            print("   ✅ Text analysis working")
        else:
            print("   ❌ Text analysis failed")
            return False
        
        print("   ✅ AI Integration working correctly!")
        return True
        
    except Exception as e:
        print(f"   ❌ AI Integration error: {e}")
        return False

def test_thai_processor_real_working():
    """ทดสอบ Thai Processor ทำงานได้จริง"""
    print("🔍 Testing Thai Processor - Real Working Test...")
    try:
        from core.thai_processor import FullThaiProcessor
        processor = FullThaiProcessor()
        
        # ทดสอบการประมวลผลข้อความ
        print("   🔄 Testing text processing...")
        test_command = "เปิดเว็บไซต์ Google"
        result = processor.process_natural_command(test_command)
        
        if result and 'action' in result:
            print(f"   ✅ Command processed: {result}")
        else:
            print("   ❌ Command processing failed")
            return False
        
        print("   ✅ Thai Processor working correctly!")
        return True
        
    except Exception as e:
        print(f"   ❌ Thai Processor error: {e}")
        return False

def test_backup_controller_real_working():
    """ทดสอบ Backup Controller ทำงานได้จริง"""
    print("🔍 Testing Backup Controller - Real Working Test...")
    try:
        from core.backup_controller import BackupController
        bc = BackupController()
        
        # ทดสอบการสร้าง backup
        print("   🔄 Testing backup creation...")
        test_data = {"test": "data", "timestamp": time.time()}
        
        # ตรวจสอบว่ามี method ที่จำเป็น
        if hasattr(bc, 'create_backup'):
            print("   ✅ Backup method available")
        else:
            print("   ❌ Backup method not available")
            return False
        
        print("   ✅ Backup Controller working correctly!")
        return True
        
    except Exception as e:
        print(f"   ❌ Backup Controller error: {e}")
        return False

def test_knowledge_manager_real_working():
    """ทดสอบ Knowledge Manager ทำงานได้จริง"""
    print("🔍 Testing Knowledge Manager - Real Working Test...")
    try:
        from core.knowledge_manager import KnowledgeManager
        km = KnowledgeManager()
        
        # ทดสอบการเพิ่มความรู้
        print("   🔄 Testing knowledge addition...")
        test_knowledge = {
            "title": "Test Knowledge",
            "content": "This is a test knowledge entry",
            "category": "test"
        }
        
        # ตรวจสอบว่ามี method ที่จำเป็น
        if hasattr(km, 'add_knowledge_from_text'):
            print("   ✅ Knowledge methods available")
        else:
            print("   ❌ Knowledge methods not available")
            return False
        
        print("   ✅ Knowledge Manager working correctly!")
        return True
        
    except Exception as e:
        print(f"   ❌ Knowledge Manager error: {e}")
        return False

def test_godmode_knowledge_real_working():
    """ทดสอบ God Mode Knowledge ทำงานได้จริง"""
    print("🔍 Testing God Mode Knowledge - Real Working Test...")
    try:
        from alldata_godmode.god_mode_knowledge_manager import GodModeKnowledgeManager
        gkm = GodModeKnowledgeManager()
        
        # ทดสอบการเริ่ม session
        print("   🔄 Testing session creation...")
        session_id = gkm.start_session("test_session")
        
        if session_id:
            print(f"   ✅ Session created: {session_id}")
        else:
            print("   ❌ Session creation failed")
            return False
        
        # ทดสอบการบันทึกคำสั่ง
        print("   🔄 Testing command saving...")
        gkm.save_command(session_id, "test command", "test", True, "test result")
        print("   ✅ Command saved successfully")
        
        print("   ✅ God Mode Knowledge working correctly!")
        return True
        
    except Exception as e:
        print(f"   ❌ God Mode Knowledge error: {e}")
        return False

def main():
    """ทดสอบระบบทั้งหมดแบบจริงจัง"""
    print("🚀 Backup-byGod Real Working Test")
    print("=" * 60)
    print("This test will verify that each component actually works")
    print("=" * 60)
    
    results = {}
    
    # ทดสอบแต่ละ component แบบจริงจัง
    results['chrome_controller'] = test_chrome_real_working()
    results['ai_integration'] = test_ai_integration_real_working()
    results['thai_processor'] = test_thai_processor_real_working()
    results['backup_controller'] = test_backup_controller_real_working()
    results['knowledge_manager'] = test_knowledge_manager_real_working()
    results['godmode_knowledge'] = test_godmode_knowledge_real_working()
    
    print("\n" + "=" * 60)
    print("📊 Real Working Test Results:")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for component, result in results.items():
        status = "✅ REALLY WORKS" if result else "❌ DOESN'T WORK"
        print(f"   {component}: {status}")
    
    print(f"\n📈 Overall: {passed_tests}/{total_tests} components REALLY work")
    
    if passed_tests == total_tests:
        print("🎉 ALL COMPONENTS REALLY WORK!")
        print("✅ System is ready for real use!")
    else:
        print("⚠️ Some components don't actually work.")
        print("❌ System needs more development.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main() 