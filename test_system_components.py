#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test System Components - ตรวจสอบว่าระบบทำงานได้จริง
"""

import sys
import os
import traceback
import logging
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system_components_test.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def test_chrome_controller():
    """ทดสอบ Chrome Controller"""
    logger.info("Starting Chrome Controller test")
    print("🔍 Testing Chrome Controller...")
    try:
        from core.chrome_controller import AIChromeController
        controller = AIChromeController()
        
        # ทดสอบ is_ready
        is_ready = controller.is_ready()
        print(f"   ✅ Chrome Controller loaded: {is_ready}")
        logger.info(f"Chrome Controller ready status: {is_ready}")
        
        # ทดสอบการสร้าง driver
        import asyncio
        result = asyncio.run(controller.start_ai_browser(headless=True))
        print(f"   ✅ Chrome browser started: {result}")
        logger.info(f"Chrome browser started successfully: {result}")
        
        return True
    except ImportError as e:
        error_msg = f"Chrome Controller import error: {e}"
        logger.error(error_msg)
        print(f"   ❌ Chrome Controller import error: {e}")
        return False
    except Exception as e:
        error_msg = f"Chrome Controller error: {e}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"   ❌ Chrome Controller error: {e}")
        return False

def test_ai_integration():
    """ทดสอบ AI Integration"""
    logger.info("Starting AI Integration test")
    print("🔍 Testing AI Integration...")
    try:
        from core.ai_integration import MultimodalAIIntegration
        ai = MultimodalAIIntegration()
        print("   ✅ AI Integration loaded successfully")
        logger.info("AI Integration loaded successfully")
        return True
    except ImportError as e:
        error_msg = f"AI Integration import error: {e}"
        logger.error(error_msg)
        print(f"   ❌ AI Integration import error: {e}")
        return False
    except Exception as e:
        error_msg = f"AI Integration error: {e}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"   ❌ AI Integration error: {e}")
        return False

def test_thai_processor():
    """ทดสอบ Thai Processor"""
    logger.info("Starting Thai Processor test")
    print("🔍 Testing Thai Processor...")
    try:
        from core.thai_processor import FullThaiProcessor
        processor = FullThaiProcessor()
        print("   ✅ Thai Processor loaded successfully")
        logger.info("Thai Processor loaded successfully")
        return True
    except ImportError as e:
        error_msg = f"Thai Processor import error: {e}"
        logger.error(error_msg)
        print(f"   ❌ Thai Processor import error: {e}")
        return False
    except Exception as e:
        error_msg = f"Thai Processor error: {e}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"   ❌ Thai Processor error: {e}")
        return False

def test_visual_recognition():
    """ทดสอบ Visual Recognition"""
    logger.info("Starting Visual Recognition test")
    print("🔍 Testing Visual Recognition...")
    try:
        from core.visual_recognition import VisualRecognition
        vr = VisualRecognition()
        print("   ✅ Visual Recognition loaded successfully")
        logger.info("Visual Recognition loaded successfully")
        return True
    except ImportError as e:
        error_msg = f"Visual Recognition import error: {e}"
        logger.error(error_msg)
        print(f"   ❌ Visual Recognition import error: {e}")
        return False
    except Exception as e:
        error_msg = f"Visual Recognition error: {e}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"   ❌ Visual Recognition error: {e}")
        return False

def test_backup_controller():
    """ทดสอบ Backup Controller"""
    logger.info("Starting Backup Controller test")
    print("🔍 Testing Backup Controller...")
    try:
        from core.backup_controller import BackupController
        bc = BackupController()
        print("   ✅ Backup Controller loaded successfully")
        logger.info("Backup Controller loaded successfully")
        return True
    except ImportError as e:
        error_msg = f"Backup Controller import error: {e}"
        logger.error(error_msg)
        print(f"   ❌ Backup Controller import error: {e}")
        return False
    except Exception as e:
        error_msg = f"Backup Controller error: {e}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"   ❌ Backup Controller error: {e}")
        return False

def test_supabase_integration():
    """ทดสอบ Supabase Integration"""
    logger.info("Starting Supabase Integration test")
    print("🔍 Testing Supabase Integration...")
    try:
        from core.supabase_integration import SupabaseIntegration
        supabase = SupabaseIntegration()
        print("   ✅ Supabase Integration loaded successfully")
        logger.info("Supabase Integration loaded successfully")
        return True
    except ImportError as e:
        error_msg = f"Supabase Integration import error: {e}"
        logger.error(error_msg)
        print(f"   ❌ Supabase Integration import error: {e}")
        return False
    except Exception as e:
        error_msg = f"Supabase Integration error: {e}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"   ❌ Supabase Integration error: {e}")
        return False

def test_environment_cards():
    """ทดสอบ Environment Cards"""
    logger.info("Starting Environment Cards test")
    print("🔍 Testing Environment Cards...")
    try:
        from core.environment_cards import EnvironmentCards
        ec = EnvironmentCards()
        print("   ✅ Environment Cards loaded successfully")
        logger.info("Environment Cards loaded successfully")
        return True
    except ImportError as e:
        error_msg = f"Environment Cards import error: {e}"
        logger.error(error_msg)
        print(f"   ❌ Environment Cards import error: {e}")
        return False
    except Exception as e:
        error_msg = f"Environment Cards error: {e}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"   ❌ Environment Cards error: {e}")
        return False

def test_knowledge_manager():
    """ทดสอบ Knowledge Manager"""
    logger.info("Starting Knowledge Manager test")
    print("🔍 Testing Knowledge Manager...")
    try:
        from core.knowledge_manager import KnowledgeManager
        km = KnowledgeManager()
        print("   ✅ Knowledge Manager loaded successfully")
        logger.info("Knowledge Manager loaded successfully")
        return True
    except ImportError as e:
        error_msg = f"Knowledge Manager import error: {e}"
        logger.error(error_msg)
        print(f"   ❌ Knowledge Manager import error: {e}")
        return False
    except Exception as e:
        error_msg = f"Knowledge Manager error: {e}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"   ❌ Knowledge Manager error: {e}")
        return False

def test_godmode_knowledge():
    """ทดสอบ God Mode Knowledge"""
    logger.info("Starting God Mode Knowledge test")
    print("🔍 Testing God Mode Knowledge...")
    try:
        from alldata_godmode.god_mode_knowledge_manager import GodModeKnowledgeManager
        gkm = GodModeKnowledgeManager()
        print("   ✅ God Mode Knowledge loaded successfully")
        logger.info("God Mode Knowledge loaded successfully")
        return True
    except ImportError as e:
        error_msg = f"God Mode Knowledge import error: {e}"
        logger.error(error_msg)
        print(f"   ❌ God Mode Knowledge import error: {e}")
        return False
    except Exception as e:
        error_msg = f"God Mode Knowledge error: {e}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"   ❌ God Mode Knowledge error: {e}")
        return False

def main():
    """ทดสอบระบบทั้งหมด"""
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    logger.info("Starting System Components Test Suite")
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
        if result:
            logger.info(f"Component {component}: PASS")
        else:
            logger.error(f"Component {component}: FAIL")
    
    print(f"\n📈 Overall: {passed_tests}/{total_tests} components working")
    logger.info(f"Test completed: {passed_tests}/{total_tests} components passed")
    
    if passed_tests == total_tests:
        success_msg = "All components are working correctly!"
        print(f"🎉 {success_msg}")
        logger.info(success_msg)
    else:
        warning_msg = f"Some components have issues. {total_tests - passed_tests} components failed."
        print(f"⚠️ {warning_msg}")
        logger.warning(warning_msg)
    
    return passed_tests == total_tests

if __name__ == "__main__":
    try:
    main() 
    except Exception as e:
        error_msg = f"Critical error in test suite: {e}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"❌ Critical Error: {e}")
        sys.exit(1) 