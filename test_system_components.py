#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test System Components - ตรวจสอบว่าระบบทำงานได้จริง
"""

import sys
import os
import traceback

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_chrome_controller():
    """ทดสอบ Chrome Controller"""
    print("🔍 Testing Chrome Controller...")
    try:
        from core.chrome_controller import AIChromeController
        controller = AIChromeController()
        
        # ทดสอบ is_ready
        is_ready = controller.is_ready()
        print(f"   ✅ Chrome Controller loaded: {is_ready}")
        
        # ทดสอบการสร้าง driver
        import asyncio
        result = asyncio.run(controller.start_ai_browser(headless=True))
        print(f"   ✅ Chrome browser started: {result}")
        
        return True
    except Exception as e:
        print(f"   ❌ Chrome Controller error: {e}")
        return False

def test_ai_integration():
    """ทดสอบ AI Integration"""
    print("🔍 Testing AI Integration...")
    try:
        from core.ai_integration import MultimodalAIIntegration
        ai = MultimodalAIIntegration()
        print("   ✅ AI Integration loaded successfully")
        return True
    except Exception as e:
        print(f"   ❌ AI Integration error: {e}")
        return False

def test_thai_processor():
    """ทดสอบ Thai Processor"""
    print("🔍 Testing Thai Processor...")
    try:
        from core.thai_processor import FullThaiProcessor
        processor = FullThaiProcessor()
        print("   ✅ Thai Processor loaded successfully")
        return True
    except Exception as e:
        print(f"   ❌ Thai Processor error: {e}")
        return False

def test_visual_recognition():
    """ทดสอบ Visual Recognition"""
    print("🔍 Testing Visual Recognition...")
    try:
        from core.visual_recognition import VisualRecognition
        vr = VisualRecognition()
        print("   ✅ Visual Recognition loaded successfully")
        return True
    except Exception as e:
        print(f"   ❌ Visual Recognition error: {e}")
        return False

def test_backup_controller():
    """ทดสอบ Backup Controller"""
    print("🔍 Testing Backup Controller...")
    try:
        from core.backup_controller import BackupController
        bc = BackupController()
        print("   ✅ Backup Controller loaded successfully")
        return True
    except Exception as e:
        print(f"   ❌ Backup Controller error: {e}")
        return False

def test_supabase_integration():
    """ทดสอบ Supabase Integration"""
    print("🔍 Testing Supabase Integration...")
    try:
        from core.supabase_integration import SupabaseIntegration
        supabase = SupabaseIntegration()
        print("   ✅ Supabase Integration loaded successfully")
        return True
    except Exception as e:
        print(f"   ❌ Supabase Integration error: {e}")
        return False

def test_environment_cards():
    """ทดสอบ Environment Cards"""
    print("🔍 Testing Environment Cards...")
    try:
        from core.environment_cards import EnvironmentCards
        ec = EnvironmentCards()
        print("   ✅ Environment Cards loaded successfully")
        return True
    except Exception as e:
        print(f"   ❌ Environment Cards error: {e}")
        return False

def test_knowledge_manager():
    """ทดสอบ Knowledge Manager"""
    print("🔍 Testing Knowledge Manager...")
    try:
        from core.knowledge_manager import KnowledgeManager
        km = KnowledgeManager()
        print("   ✅ Knowledge Manager loaded successfully")
        return True
    except Exception as e:
        print(f"   ❌ Knowledge Manager error: {e}")
        return False

def test_godmode_knowledge():
    """ทดสอบ God Mode Knowledge"""
    print("🔍 Testing God Mode Knowledge...")
    try:
        from alldata_godmode.god_mode_knowledge_manager import GodModeKnowledgeManager
        gkm = GodModeKnowledgeManager()
        print("   ✅ God Mode Knowledge loaded successfully")
        return True
    except Exception as e:
        print(f"   ❌ God Mode Knowledge error: {e}")
        return False

def main():
    """ทดสอบระบบทั้งหมด"""
    print("🚀 Backup-byGod System Component Test")
    print("=" * 50)
    
    results = {}
    
    # ทดสอบแต่ละ component
    results['chrome_controller'] = test_chrome_controller()
    results['ai_integration'] = test_ai_integration()
    results['thai_processor'] = test_thai_processor()
    results['visual_recognition'] = test_visual_recognition()
    results['backup_controller'] = test_backup_controller()
    results['supabase_integration'] = test_supabase_integration()
    results['environment_cards'] = test_environment_cards()
    results['knowledge_manager'] = test_knowledge_manager()
    results['godmode_knowledge'] = test_godmode_knowledge()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for component, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {component}: {status}")
    
    print(f"\n📈 Overall: {passed_tests}/{total_tests} components working")
    
    if passed_tests == total_tests:
        print("🎉 All components are working correctly!")
    else:
        print("⚠️ Some components have issues. Check the errors above.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main() 