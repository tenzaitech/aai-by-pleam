#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Chrome Controller
ตรวจสอบปัญหา Chrome ที่เปิดเองเรื่อยๆ
"""

import asyncio
import logging
import traceback
import threading
import time
from pathlib import Path

# ตั้งค่า logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def debug_chrome_controller():
    """ทดสอบ Chrome Controller แบบ debug"""
    logger.info("🔍 เริ่มต้น Debug Chrome Controller")
    
    try:
        # ใช้ Singleton
        from core.chrome_controller import AIChromeController
        chrome_controller = AIChromeController()
        
        # ทดสอบการเริ่ม browser
        logger.info("🚀 ทดสอบการเริ่ม browser...")
        success = await chrome_controller.start_ai_browser(headless=True)
        
        if success:
            logger.info("✅ Browser เริ่มต้นสำเร็จ")
            
            # ทดสอบการนำทาง
            logger.info("🌐 ทดสอบการนำทาง...")
            nav_success = await chrome_controller.ai_navigate("https://www.google.com", "ทดสอบ")
            
            if nav_success:
                logger.info("✅ การนำทางสำเร็จ")
            else:
                logger.error("❌ การนำทางล้มเหลว")
            
            # รอสักครู่
            await asyncio.sleep(2)
            
            # ทดสอบการปิด browser - DISABLED
            logger.info("🔌 ทดสอบการปิด browser - DISABLED")
            logger.debug(f"[DEBUG] cleanup() called from: {traceback.format_stack()}")
            # chrome_controller.cleanup()  # DISABLED - ไม่ให้ปิด Chrome อัตโนมัติ
            logger.info("✅ Browser cleanup disabled by user preference")
            
        else:
            logger.error("❌ ไม่สามารถเริ่ม browser ได้")
            
    except Exception as e:
        logger.error(f"❌ เกิดข้อผิดพลาด: {e}")
        logger.error(f"🔍 Traceback: {traceback.format_exc()}")

async def debug_multiple_instances():
    """ทดสอบการสร้าง Chrome Controller หลายตัว"""
    logger.info("🔍 ทดสอบการสร้าง Chrome Controller หลายตัว")
    
    try:
        # ใช้ Singleton
        from core.chrome_controller import AIChromeController
        
        controllers = []
        
        for i in range(3):
            logger.info(f"🔧 สร้าง Chrome Controller #{i+1}...")
            controller = AIChromeController()
            controllers.append(controller)
            
            # เริ่ม browser
            success = await controller.start_ai_browser(headless=True)
            if success:
                logger.info(f"✅ Controller #{i+1} เริ่มต้นสำเร็จ")
            else:
                logger.error(f"❌ Controller #{i+1} เริ่มต้นล้มเหลว")
            
            # รอสักครู่
            await asyncio.sleep(1)
        
        # ปิดทั้งหมด - DISABLED
        logger.info("🔌 ปิด controllers ทั้งหมด - DISABLED")
        for i, controller in enumerate(controllers):
            logger.debug(f"[DEBUG] cleanup() called from: {traceback.format_stack()}")
            # controller.cleanup()  # DISABLED - ไม่ให้ปิด Chrome อัตโนมัติ
            logger.info(f"✅ Controller #{i+1} cleanup disabled by user preference")
            
    except Exception as e:
        logger.error(f"❌ เกิดข้อผิดพลาด: {e}")
        logger.error(f"🔍 Traceback: {traceback.format_exc()}")

async def debug_master_controller():
    """ทดสอบ Master Controller"""
    logger.info("🔍 ทดสอบ Master Controller")
    
    try:
        from master_controller import FullSystemLauncher
        
        launcher = FullSystemLauncher()
        
        # เริ่มต้น components
        logger.info("🔧 เริ่มต้น components...")
        await launcher.initialize_components()
        
        # ตรวจสอบสถานะ
        status = launcher.get_system_status()
        logger.info(f"📊 สถานะระบบ: {status}")
        
        # ทดสอบการเริ่ม Chrome
        logger.info("🚀 ทดสอบการเริ่ม Chrome...")
        success = await launcher.start_chrome_browser(headless=True)
        
        if success:
            logger.info("✅ Chrome เริ่มต้นสำเร็จ")
            
            # รอสักครู่
            await asyncio.sleep(2)
            
            # ปิด Chrome - DISABLED
            logger.info("🔌 ปิด Chrome - DISABLED")
            logger.debug(f"[DEBUG] stop_chrome_browser() called from: {traceback.format_stack()}")
            await launcher.stop_chrome_browser()
            logger.info("✅ Chrome cleanup disabled by user preference")
            
        else:
            logger.error("❌ ไม่สามารถเริ่ม Chrome ได้")
            
    except Exception as e:
        logger.error(f"❌ เกิดข้อผิดพลาด: {e}")
        logger.error(f"🔍 Traceback: {traceback.format_exc()}")

async def main():
    """ฟังก์ชันหลัก"""
    logger.info("🚀 เริ่มต้น Debug Session")
    
    # ทดสอบ 1: Chrome Controller เดี่ยว
    logger.info("\n" + "="*50)
    logger.info("ทดสอบ 1: Chrome Controller เดี่ยว")
    logger.info("="*50)
    await debug_chrome_controller()
    
    # รอสักครู่
    await asyncio.sleep(3)
    
    # ทดสอบ 2: Chrome Controller หลายตัว
    logger.info("\n" + "="*50)
    logger.info("ทดสอบ 2: Chrome Controller หลายตัว")
    logger.info("="*50)
    await debug_multiple_instances()
    
    # รอสักครู่
    await asyncio.sleep(3)
    
    # ทดสอบ 3: Master Controller
    logger.info("\n" + "="*50)
    logger.info("ทดสอบ 3: Master Controller")
    logger.info("="*50)
    await debug_master_controller()
    
    logger.info("\n🎉 Debug Session เสร็จสิ้น")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n🛑 Debug Session ถูกหยุดโดยผู้ใช้")
    except Exception as e:
        logger.error(f"\n❌ Debug Session เกิดข้อผิดพลาด: {e}") 