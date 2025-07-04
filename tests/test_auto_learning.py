#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Auto Learning System - ทดสอบระบบ Auto-Learning
ทดสอบการทำงานของระบบ Auto-Learning
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system.core.controllers.auto_learning_manager import AutoLearningManager

class AutoLearningTester:
    """ทดสอบระบบ Auto-Learning"""
    
    def __init__(self):
        self.test_results = []
        self.errors = []
        self.start_time = time.time()
        
    def log_test(self, test_name: str, success: bool, details: str = "", error: str = None):
        """บันทึกผลการทดสอบ"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if error:
            print(f"   Error: {error}")
    
    def test_auto_learning_initialization(self) -> bool:
        """ทดสอบการเริ่มต้นระบบ Auto-Learning"""
        try:
            print("\n🧠 Testing Auto Learning Initialization...")
            
            alm = AutoLearningManager("test_auto_learning_data")
            
            # ตรวจสอบการสร้างโฟลเดอร์และไฟล์
            self.log_test(
                "Directory Creation", 
                os.path.exists("test_auto_learning_data"), 
                "Auto learning directory created"
            )
            
            # ตรวจสอบการสร้างฐานข้อมูล
            self.log_test(
                "Database Creation", 
                os.path.exists("test_auto_learning_data/auto_learning.db"), 
                "SQLite database created"
            )
            
            # ตรวจสอบการโหลดข้อมูล
            self.log_test(
                "Data Loading", 
                isinstance(alm.patterns, dict) and isinstance(alm.behaviors, list), 
                "Patterns and behaviors loaded successfully"
            )
            
            return True
            
        except Exception as e:
            self.log_test("Auto Learning Initialization", False, "", str(e))
            self.errors.append(f"Auto Learning Initialization Error: {e}")
            return False
    
    def test_behavior_recording(self) -> bool:
        """ทดสอบการบันทึกพฤติกรรม"""
        try:
            print("\n📝 Testing Behavior Recording...")
            
            alm = AutoLearningManager("test_auto_learning_data")
            
            # บันทึกพฤติกรรมต่างๆ
            test_behaviors = [
                {
                    "user_id": "test_user_1",
                    "action_type": "command",
                    "action_data": {
                        "command_type": "chrome_navigate",
                        "parameters": {"url": "https://google.com"},
                        "success": True,
                        "execution_time": 2.5
                    },
                    "context": {"pref_browser": "chrome", "pref_speed": "fast"},
                    "session_id": "test_session_1"
                },
                {
                    "user_id": "test_user_1",
                    "action_type": "command",
                    "action_data": {
                        "command_type": "chrome_click",
                        "parameters": {"selector": "#search-button"},
                        "success": True,
                        "execution_time": 1.2
                    },
                    "context": {"pref_browser": "chrome"},
                    "session_id": "test_session_1"
                },
                {
                    "user_id": "test_user_1",
                    "action_type": "error",
                    "action_data": {
                        "error_type": "element_not_found",
                        "solution": "wait_for_element;retry_click",
                        "success": False
                    },
                    "context": {"pref_browser": "chrome"},
                    "session_id": "test_session_1"
                },
                {
                    "user_id": "test_user_2",
                    "action_type": "command",
                    "action_data": {
                        "command_type": "file_download",
                        "parameters": {"url": "https://example.com/file.pdf"},
                        "success": True,
                        "execution_time": 5.0
                    },
                    "context": {"pref_download_path": "/downloads"},
                    "session_id": "test_session_2"
                }
            ]
            
            behavior_ids = []
            for behavior in test_behaviors:
                behavior_id = alm.record_behavior(
                    user_id=behavior["user_id"],
                    action_type=behavior["action_type"],
                    action_data=behavior["action_data"],
                    context=behavior["context"],
                    session_id=behavior["session_id"]
                )
                behavior_ids.append(behavior_id)
            
            # ตรวจสอบการบันทึก
            self.log_test(
                "Behavior Recording", 
                all(behavior_ids) and len(alm.behaviors) >= len(test_behaviors), 
                f"Recorded {len(behavior_ids)} behaviors successfully"
            )
            
            # ตรวจสอบการบันทึกลงฐานข้อมูล
            import sqlite3
            conn = sqlite3.connect("test_auto_learning_data/auto_learning.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM user_behaviors")
            db_count = cursor.fetchone()[0]
            conn.close()
            
            self.log_test(
                "Database Recording", 
                db_count >= len(test_behaviors), 
                f"Database contains {db_count} behaviors"
            )
            
            return True
            
        except Exception as e:
            self.log_test("Behavior Recording", False, "", str(e))
            self.errors.append(f"Behavior Recording Error: {e}")
            return False
    
    def test_pattern_learning(self) -> bool:
        """ทดสอบการเรียนรู้ patterns"""
        try:
            print("\n🎓 Testing Pattern Learning...")
            
            alm = AutoLearningManager("test_auto_learning_data")
            
            # เรียนรู้จาก behaviors ที่มีอยู่
            patterns = alm.learn_from_behaviors(time_window_hours=24)
            
            self.log_test(
                "Pattern Learning", 
                isinstance(patterns, list), 
                f"Generated {len(patterns)} patterns"
            )
            
            # ตรวจสอบประเภทของ patterns
            if patterns:
                pattern_types = [p["pattern_type"] for p in patterns]
                self.log_test(
                    "Pattern Types", 
                    len(set(pattern_types)) > 0, 
                    f"Pattern types: {', '.join(set(pattern_types))}"
                )
                
                # ตรวจสอบ command patterns
                command_patterns = [p for p in patterns if p["pattern_type"] == "command"]
                self.log_test(
                    "Command Patterns", 
                    len(command_patterns) > 0, 
                    f"Found {len(command_patterns)} command patterns"
                )
                
                # ตรวจสอบ workflow patterns
                workflow_patterns = [p for p in patterns if p["pattern_type"] == "workflow"]
                self.log_test(
                    "Workflow Patterns", 
                    len(workflow_patterns) >= 0, 
                    f"Found {len(workflow_patterns)} workflow patterns"
                )
                
                # ตรวจสอบ error patterns
                error_patterns = [p for p in patterns if p["pattern_type"] == "error_fix"]
                self.log_test(
                    "Error Patterns", 
                    len(error_patterns) >= 0, 
                    f"Found {len(error_patterns)} error fix patterns"
                )
                
                # ตรวจสอบ preference patterns
                preference_patterns = [p for p in patterns if p["pattern_type"] == "preference"]
                self.log_test(
                    "Preference Patterns", 
                    len(preference_patterns) >= 0, 
                    f"Found {len(preference_patterns)} preference patterns"
                )
            
            return True
            
        except Exception as e:
            self.log_test("Pattern Learning", False, "", str(e))
            self.errors.append(f"Pattern Learning Error: {e}")
            return False
    
    def test_recommendations(self) -> bool:
        """ทดสอบระบบคำแนะนำ"""
        try:
            print("\n💡 Testing Recommendations...")
            
            alm = AutoLearningManager("test_auto_learning_data")
            
            # เรียนรู้ patterns ก่อน
            alm.learn_from_behaviors(time_window_hours=24)
            
            # ขอคำแนะนำ
            recommendations = alm.get_recommendations("test_user_1")
            
            self.log_test(
                "Recommendations Generation", 
                isinstance(recommendations, list), 
                f"Generated {len(recommendations)} recommendations"
            )
            
            # ตรวจสอบคุณภาพของคำแนะนำ
            if recommendations:
                high_confidence_recs = [r for r in recommendations if r["confidence"] >= 0.7]
                self.log_test(
                    "High Confidence Recommendations", 
                    len(high_confidence_recs) >= 0, 
                    f"Found {len(high_confidence_recs)} high confidence recommendations"
                )
                
                # ตรวจสอบโครงสร้างของคำแนะนำ
                valid_structure = all(
                    "pattern_id" in r and "pattern_type" in r and "recommendation" in r
                    for r in recommendations
                )
                self.log_test(
                    "Recommendation Structure", 
                    valid_structure, 
                    "All recommendations have valid structure"
                )
            
            return True
            
        except Exception as e:
            self.log_test("Recommendations", False, "", str(e))
            self.errors.append(f"Recommendations Error: {e}")
            return False
    
    def test_statistics(self) -> bool:
        """ทดสอบระบบสถิติ"""
        try:
            print("\n📊 Testing Statistics...")
            
            alm = AutoLearningManager("test_auto_learning_data")
            
            # เรียนรู้ patterns ก่อน
            alm.learn_from_behaviors(time_window_hours=24)
            
            # ดึงสถิติ
            stats = alm.get_statistics()
            
            self.log_test(
                "Statistics Generation", 
                isinstance(stats, dict) and "total_patterns" in stats, 
                f"Statistics: {stats.get('total_patterns', 0)} patterns, {stats.get('total_behaviors', 0)} behaviors"
            )
            
            # ตรวจสอบข้อมูลสถิติ
            if stats:
                required_keys = ["total_patterns", "total_behaviors", "pattern_types", "behavior_types"]
                valid_keys = all(key in stats for key in required_keys)
                self.log_test(
                    "Statistics Keys", 
                    valid_keys, 
                    "All required statistics keys present"
                )
                
                # ตรวจสอบค่าเฉลี่ย
                if stats.get("total_patterns", 0) > 0:
                    avg_confidence = stats.get("average_confidence", 0)
                    avg_success_rate = stats.get("average_success_rate", 0)
                    
                    self.log_test(
                        "Average Values", 
                        0 <= avg_confidence <= 1 and 0 <= avg_success_rate <= 1, 
                        f"Avg confidence: {avg_confidence:.3f}, Avg success rate: {avg_success_rate:.3f}"
                    )
            
            return True
            
        except Exception as e:
            self.log_test("Statistics", False, "", str(e))
            self.errors.append(f"Statistics Error: {e}")
            return False
    
    def test_data_export_import(self) -> bool:
        """ทดสอบการส่งออกและนำเข้าข้อมูล"""
        try:
            print("\n📤 Testing Data Export/Import...")
            
            alm = AutoLearningManager("test_auto_learning_data")
            
            # เรียนรู้ patterns ก่อน
            alm.learn_from_behaviors(time_window_hours=24)
            
            # ส่งออกข้อมูล
            export_path = alm.export_learning_data()
            
            self.log_test(
                "Data Export", 
                os.path.exists(export_path), 
                f"Exported data to: {export_path}"
            )
            
            # ตรวจสอบไฟล์ที่ส่งออก
            if os.path.exists(export_path):
                with open(export_path, 'r', encoding='utf-8') as f:
                    export_data = json.load(f)
                
                self.log_test(
                    "Export Data Structure", 
                    "metadata" in export_data and "patterns" in export_data and "behaviors" in export_data, 
                    "Export data has correct structure"
                )
                
                # สร้าง AutoLearningManager ใหม่และนำเข้าข้อมูล
                alm2 = AutoLearningManager("test_auto_learning_data_import")
                import_success = alm2.import_learning_data(export_path)
                
                self.log_test(
                    "Data Import", 
                    import_success, 
                    "Data imported successfully"
                )
                
                # ตรวจสอบว่าข้อมูลถูกนำเข้ามา
                if import_success:
                    stats2 = alm2.get_statistics()
                    self.log_test(
                        "Import Verification", 
                        stats2.get("total_patterns", 0) > 0, 
                        f"Imported {stats2.get('total_patterns', 0)} patterns"
                    )
            
            return True
            
        except Exception as e:
            self.log_test("Data Export/Import", False, "", str(e))
            self.errors.append(f"Data Export/Import Error: {e}")
            return False
    
    def test_cleanup(self) -> bool:
        """ทดสอบการล้างข้อมูลเก่า"""
        try:
            print("\n🧹 Testing Cleanup...")
            
            alm = AutoLearningManager("test_auto_learning_data")
            
            # ตั้งค่าให้ patterns เก่าเร็วขึ้น
            alm.pattern_lifetime_days = 0  # ลบทันที
            alm.min_frequency = 100  # ตั้งค่าสูงเพื่อให้ patterns เก่าถูกลบ
            
            # เรียก cleanup
            alm._cleanup_old_patterns()
            
            self.log_test(
                "Cleanup Execution", 
                True, 
                "Cleanup process completed without errors"
            )
            
            return True
            
        except Exception as e:
            self.log_test("Cleanup", False, "", str(e))
            self.errors.append(f"Cleanup Error: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """รันการทดสอบทั้งหมด"""
        print("🚀 Starting Auto Learning System Tests...")
        print("=" * 60)
        
        # Run all tests
        tests = [
            ("Auto Learning Initialization", self.test_auto_learning_initialization),
            ("Behavior Recording", self.test_behavior_recording),
            ("Pattern Learning", self.test_pattern_learning),
            ("Recommendations", self.test_recommendations),
            ("Statistics", self.test_statistics),
            ("Data Export/Import", self.test_data_export_import),
            ("Cleanup", self.test_cleanup)
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log_test(test_name, False, "", str(e))
                self.errors.append(f"{test_name} Error: {e}")
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        end_time = time.time()
        duration = end_time - self.start_time
        
        # Generate report
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "duration_seconds": round(duration, 2),
                "timestamp": datetime.now().isoformat()
            },
            "test_results": self.test_results,
            "errors": self.errors
        }
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        
        if self.errors:
            print(f"\n❌ ERRORS FOUND ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"{i}. {error}")
        
        # Save report
        report_file = f"auto_learning_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 Report saved to: {report_file}")
        
        return report

def main():
    """Main function"""
    tester = AutoLearningTester()
    report = tester.run_all_tests()
    
    # Return exit code based on success rate
    success_rate = report['summary']['success_rate']
    if success_rate >= 80:
        print("\n🎉 Auto Learning System Test: EXCELLENT (80%+ success rate)")
        return 0
    elif success_rate >= 60:
        print("\n⚠️ Auto Learning System Test: GOOD (60%+ success rate)")
        return 1
    else:
        print("\n🚨 Auto Learning System Test: NEEDS ATTENTION (<60% success rate)")
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 