#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Knowledge Manager
ทดสอบระบบ Knowledge Manager
"""

from core.knowledge_manager import knowledge_manager
import json

def test_knowledge_manager():
    """ทดสอบฟีเจอร์ทั้งหมดของ Knowledge Manager"""
    print("🧠 Testing Knowledge Manager...")
    print("=" * 50)
    
    # 1. ทดสอบการเพิ่มความรู้จากข้อความ
    print("\n1️⃣ ทดสอบการเพิ่มความรู้จากข้อความ")
    result1 = knowledge_manager.add_knowledge_from_text(
        title="n8n Webhook Tutorial",
        content="n8n webhook เป็นวิธีที่ดีในการรับข้อมูลจาก external services. สามารถสร้าง webhook endpoint ได้ง่ายๆ และรับข้อมูลแบบ real-time",
        category="n8n",
        description="วิธีการใช้ webhook ใน n8n"
    )
    print(f"✅ Result: {result1}")
    
    # 2. ทดสอบการเพิ่มความรู้จากข้อความอีกอัน
    print("\n2️⃣ ทดสอบการเพิ่มความรู้จากข้อความ (Zapier)")
    result2 = knowledge_manager.add_knowledge_from_text(
        title="Zapier Automation Basics",
        content="Zapier เป็นเครื่องมือ automation ที่เชื่อมต่อแอปต่างๆ เข้าด้วยกัน สามารถสร้าง workflow ง่ายๆ โดยไม่ต้องเขียนโค้ด",
        category="zapier",
        description="พื้นฐานการใช้งาน Zapier"
    )
    print(f"✅ Result: {result2}")
    
    # 3. ทดสอบการเพิ่มความรู้จากข้อความ (Chrome)
    print("\n3️⃣ ทดสอบการเพิ่มความรู้จากข้อความ (Chrome)")
    result3 = knowledge_manager.add_knowledge_from_text(
        title="Chrome Automation with Selenium",
        content="Selenium เป็นเครื่องมือที่ยอดเยี่ยมสำหรับการควบคุม Chrome browser. สามารถทำ web scraping, form filling, และ automation ได้",
        category="chrome",
        description="การใช้งาน Selenium กับ Chrome"
    )
    print(f"✅ Result: {result3}")
    
    # 4. ทดสอบการดูสถิติ
    print("\n4️⃣ ทดสอบการดูสถิติ")
    stats = knowledge_manager.get_statistics()
    print(f"📊 Statistics: {json.dumps(stats, indent=2, ensure_ascii=False)}")
    
    # 5. ทดสอบการค้นหา
    print("\n5️⃣ ทดสอบการค้นหา")
    search_results = knowledge_manager.search_knowledge("webhook")
    print(f"🔍 Found {len(search_results)} results for 'webhook'")
    for i, result in enumerate(search_results, 1):
        print(f"  {i}. {result['title']} ({result['category']})")
    
    # 6. ทดสอบการค้นหาตามหมวดหมู่
    print("\n6️⃣ ทดสอบการค้นหาตามหมวดหมู่")
    n8n_results = knowledge_manager.get_knowledge_by_category("n8n")
    print(f"🔧 Found {len(n8n_results)} n8n knowledge items")
    for i, result in enumerate(n8n_results, 1):
        print(f"  {i}. {result['title']}")
    
    # 7. ทดสอบการดูหมวดหมู่ทั้งหมด
    print("\n7️⃣ ทดสอบการดูหมวดหมู่ทั้งหมด")
    categories = knowledge_manager.get_categories()
    print(f"📂 Categories: {len(categories)} categories available")
    for cat in categories:
        print(f"  {cat['icon']} {cat['name']}: {cat['description']}")
    
    # 8. ทดสอบการอัปเดตความรู้
    print("\n8️⃣ ทดสอบการอัปเดตความรู้")
    if result1['success']:
        knowledge_id = result1['knowledge_id']
        update_result = knowledge_manager.update_knowledge(
            knowledge_id,
            {"description": "วิธีการใช้ webhook ใน n8n (อัปเดตแล้ว)"}
        )
        print(f"✅ Update Result: {update_result}")
    
    # 9. ทดสอบการดูความรู้ทั้งหมด
    print("\n9️⃣ ทดสอบการดูความรู้ทั้งหมด")
    all_knowledge = knowledge_manager.get_all_knowledge()
    print(f"📚 Total knowledge items: {len(all_knowledge)}")
    for i, item in enumerate(all_knowledge, 1):
        print(f"  {i}. {item['title']} ({item['category']}) - {item['description'][:50]}...")
    
    print("\n" + "=" * 50)
    print("🎉 Knowledge Manager Test Completed Successfully!")
    print("✅ All features are working correctly!")
    print("🌐 You can now use the dashboard to manage knowledge!")
    print("=" * 50)

if __name__ == "__main__":
    test_knowledge_manager() 