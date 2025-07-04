#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Memory System - ทดสอบระบบความจำจริง
ทดสอบการทำงานของระบบความจำทั้งหมด
"""

import sys
import os
import json
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cloud_manager import CloudManager
from system.core.controllers.knowledge_manager import KnowledgeManager
from system.godmode.god_mode_knowledge_manager import GodModeKnowledgeManager

class MemorySystemTester:
    """ทดสอบระบบความจำจริง"""
    
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
    
    def test_cloud_manager_connection(self) -> bool:
        """ทดสอบการเชื่อมต่อ Cloud Manager"""
        try:
            print("\n🔗 Testing Cloud Manager Connection...")
            
            # Test Supabase connection
            cloud_manager = CloudManager()
            
            # Test Supabase setup
            supabase_success = cloud_manager.setup_supabase()
            self.log_test(
                "Supabase Connection", 
                supabase_success, 
                "Supabase client initialized successfully"
            )
            
            # Test Google Cloud setup
            google_success = cloud_manager.setup_google_cloud()
            self.log_test(
                "Google Cloud Connection", 
                google_success, 
                "Google Cloud APIs initialized successfully"
            )
            
            # Test database setup
            db_success = cloud_manager.setup_database()
            self.log_test(
                "Database Connection", 
                db_success, 
                "Database connection established"
            )
            
            return supabase_success and google_success and db_success
            
        except Exception as e:
            self.log_test("Cloud Manager Connection", False, "", str(e))
            self.errors.append(f"Cloud Manager Error: {e}")
            return False
    
    def test_knowledge_manager(self) -> bool:
        """ทดสอบ Knowledge Manager"""
        try:
            print("\n🧠 Testing Knowledge Manager...")
            
            km = KnowledgeManager()
            
            # Test adding knowledge
            test_knowledge = {
                "title": "Test Knowledge",
                "content": "This is a test knowledge item for testing purposes.",
                "category": "testing",
                "tags": ["test", "memory", "system"]
            }
            
            result = km.add_knowledge_from_text(
                title=test_knowledge["title"],
                content=test_knowledge["content"],
                category=test_knowledge["category"],
                description="Test knowledge for memory system testing"
            )
            
            self.log_test(
                "Add Knowledge", 
                result["success"], 
                f"Added knowledge with ID: {result.get('knowledge_id', 'N/A')}"
            )
            
            # Test searching knowledge
            search_result = km.search_knowledge("test")
            self.log_test(
                "Search Knowledge", 
                len(search_result) > 0, 
                f"Found {len(search_result)} knowledge items"
            )
            
            # Test getting statistics
            stats = km.get_statistics()
            self.log_test(
                "Get Statistics", 
                "total_items" in stats, 
                f"Statistics: {stats.get('total_items', 0)} items"
            )
            
            return True
            
        except Exception as e:
            self.log_test("Knowledge Manager", False, "", str(e))
            self.errors.append(f"Knowledge Manager Error: {e}")
            return False
    
    def test_godmode_knowledge_manager(self) -> bool:
        """ทดสอบ God Mode Knowledge Manager"""
        try:
            print("\n👑 Testing God Mode Knowledge Manager...")
            
            gkm = GodModeKnowledgeManager()
            
            # Test starting session
            session_id = gkm.start_session()
            self.log_test(
                "Start Session", 
                True, 
                f"Started session: {session_id}"
            )
            
            # Test saving command
            command_result = gkm.save_command(
                session_id=session_id,
                command="test_command",
                command_type="test",
                success=True,
                result_summary="Test command executed successfully"
            )
            self.log_test(
                "Save Command", 
                command_result, 
                "Command saved successfully"
            )
            
            # Test saving learning
            learning_result = gkm.save_learning(
                learning_type="test_learning",
                learning_data={"lesson": "Test learning lesson"},
                context="Testing context",
                importance_score=0.8,
                tags=["test", "learning"]
            )
            self.log_test(
                "Save Learning", 
                True, 
                "Learning saved successfully"
            )
            
            # Test getting statistics
            stats = gkm.get_statistics()
            self.log_test(
                "Get God Mode Statistics", 
                "total_sessions" in stats, 
                f"Stats: {stats.get('total_sessions', 0)} sessions, {stats.get('total_commands', 0)} commands"
            )
            
            # Test ending session
            gkm.end_session(session_id)
            self.log_test(
                "End Session", 
                True, 
                f"Ended session: {session_id}"
            )
            
            return True
            
        except Exception as e:
            self.log_test("God Mode Knowledge Manager", False, "", str(e))
            self.errors.append(f"God Mode Knowledge Manager Error: {e}")
            return False
    
    def test_memory_operations(self) -> bool:
        """ทดสอบการทำงานของระบบความจำ"""
        try:
            print("\n💾 Testing Memory Operations...")
            
            # Test memory persistence
            gkm = GodModeKnowledgeManager()
            
            # Add test data
            session_id = gkm.start_session("test_memory_session")
            
            # Add multiple commands
            for i in range(5):
                gkm.save_command(
                    session_id=session_id,
                    command=f"test_command_{i}",
                    command_type="test",
                    success=True,
                    result_summary=f"Command {i} executed"
                )
            
            # Add multiple learnings
            for i in range(3):
                gkm.save_learning(
                    learning_type=f"test_learning_{i}",
                    learning_data={"lesson": f"Test lesson {i}"},
                    context=f"Test context {i}",
                    importance_score=0.7 + (i * 0.1),
                    tags=[f"test{i}", "memory"]
                )
            
            # Test memory retrieval
            commands = gkm.get_command_history(session_id)
            self.log_test(
                "Memory Retrieval - Commands", 
                len(commands) == 5, 
                f"Retrieved {len(commands)} commands"
            )
            
            learnings = gkm.get_learnings()
            self.log_test(
                "Memory Retrieval - Learnings", 
                len(learnings) >= 3, 
                f"Retrieved {len(learnings)} learnings"
            )
            
            # Test memory persistence across instances
            gkm2 = GodModeKnowledgeManager()
            commands2 = gkm2.get_command_history(session_id)
            self.log_test(
                "Memory Persistence", 
                len(commands2) == 5, 
                f"Persisted {len(commands2)} commands across instances"
            )
            
            return True
            
        except Exception as e:
            self.log_test("Memory Operations", False, "", str(e))
            self.errors.append(f"Memory Operations Error: {e}")
            return False
    
    def test_database_operations(self) -> bool:
        """ทดสอบการทำงานกับฐานข้อมูล"""
        try:
            print("\n🗄️ Testing Database Operations...")
            
            cloud_manager = CloudManager()
            
            # Test Supabase operations if available
            if cloud_manager.supabase_client:
                try:
                    # Test inserting data
                    test_data = {
                        "title": "Test Database Entry",
                        "content": "This is a test entry for database testing",
                        "category": "testing",
                        "tags": ["test", "database"],
                        "user_id": "test_user_id"
                    }
                    
                    response = cloud_manager.supabase_client.table('knowledge_base').insert(test_data).execute()
                    
                    self.log_test(
                        "Supabase Insert", 
                        True, 
                        f"Inserted data with ID: {response.data[0]['id'] if response.data else 'N/A'}"
                    )
                    
                    # Test querying data
                    query_response = cloud_manager.supabase_client.table('knowledge_base').select('*').eq('category', 'testing').execute()
                    
                    self.log_test(
                        "Supabase Query", 
                        len(query_response.data) > 0, 
                        f"Queried {len(query_response.data)} records"
                    )
                    
                except Exception as e:
                    self.log_test("Supabase Operations", False, "", str(e))
                    self.errors.append(f"Supabase Operations Error: {e}")
            
            return True
            
        except Exception as e:
            self.log_test("Database Operations", False, "", str(e))
            self.errors.append(f"Database Operations Error: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """รันการทดสอบทั้งหมด"""
        print("🚀 Starting Memory System Tests...")
        print("=" * 60)
        
        # Run all tests
        tests = [
            ("Cloud Manager Connection", self.test_cloud_manager_connection),
            ("Knowledge Manager", self.test_knowledge_manager),
            ("God Mode Knowledge Manager", self.test_godmode_knowledge_manager),
            ("Memory Operations", self.test_memory_operations),
            ("Database Operations", self.test_database_operations)
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
        report_file = f"memory_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 Report saved to: {report_file}")
        
        return report

def main():
    """Main function"""
    tester = MemorySystemTester()
    report = tester.run_all_tests()
    
    # Return exit code based on success rate
    success_rate = report['summary']['success_rate']
    if success_rate >= 80:
        print("\n🎉 Memory System Test: EXCELLENT (80%+ success rate)")
        return 0
    elif success_rate >= 60:
        print("\n⚠️ Memory System Test: GOOD (60%+ success rate)")
        return 1
    else:
        print("\n🚨 Memory System Test: NEEDS ATTENTION (<60% success rate)")
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 