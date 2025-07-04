#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Integration - ทดสอบการทำงานของระบบ real-time logging
ทดสอบ LoggerManager, WorkflowMonitor, PerformanceTracker และ AlertSystem
"""

import time
import threading
import random
import uuid
from datetime import datetime, timedelta
import sys
import os

# เพิ่ม path สำหรับ import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logger_manager import get_logger_manager, LoggerManager
from workflow_monitor import get_workflow_monitor, WorkflowMonitor, WorkflowStatus, StepStatus
from performance_tracker import get_performance_tracker, PerformanceTracker
from alert_system import get_alert_system, AlertSystem, AlertType, AlertSeverity

class LoggingSystemTester:
    """ทดสอบระบบ logging แบบครบวงจร"""
    
    def __init__(self):
        self.logger_manager = get_logger_manager()
        self.workflow_monitor = get_workflow_monitor()
        self.performance_tracker = get_performance_tracker()
        self.alert_system = get_alert_system()
        
        self.test_results = {
            "logger_manager": {"passed": 0, "failed": 0, "tests": []},
            "workflow_monitor": {"passed": 0, "failed": 0, "tests": []},
            "performance_tracker": {"passed": 0, "failed": 0, "tests": []},
            "alert_system": {"passed": 0, "failed": 0, "tests": []}
        }
        
        print("🧪 Logging System Tester initialized")
    
    def run_all_tests(self):
        """รันการทดสอบทั้งหมด"""
        print("\n" + "="*60)
        print("🚀 STARTING COMPREHENSIVE LOGGING SYSTEM TEST")
        print("="*60)
        
        # ทดสอบ Logger Manager
        self.test_logger_manager()
        
        # ทดสอบ Workflow Monitor
        self.test_workflow_monitor()
        
        # ทดสอบ Performance Tracker
        self.test_performance_tracker()
        
        # ทดสอบ Alert System
        self.test_alert_system()
        
        # ทดสอบการทำงานร่วมกัน
        self.test_integration()
        
        # แสดงผลลัพธ์
        self.print_results()
        
        print("\n" + "="*60)
        print("✅ COMPREHENSIVE TEST COMPLETED")
        print("="*60)
    
    def test_logger_manager(self):
        """ทดสอบ Logger Manager"""
        print("\n📝 Testing Logger Manager...")
        
        # ทดสอบการสร้าง logger
        try:
            logger = self.logger_manager.get_logger("test_module")
            logger.info("Test log message")
            self.add_test_result("logger_manager", "Create logger", True)
        except Exception as e:
            self.add_test_result("logger_manager", "Create logger", False, str(e))
        
        # ทดสอบการบันทึก log ระดับต่างๆ
        levels = ["debug", "info", "warning", "error", "critical"]
        for level in levels:
            try:
                self.logger_manager.log(
                    module="test_module",
                    level=level,
                    message=f"Test {level} message",
                    workflow_id="test_workflow",
                    step="test_step",
                    duration_ms=random.randint(10, 1000),
                    status="completed",
                    context={"test": True, "level": level},
                    metadata={"timestamp": datetime.now().isoformat()}
                )
                self.add_test_result("logger_manager", f"Log {level} level", True)
            except Exception as e:
                self.add_test_result("logger_manager", f"Log {level} level", False, str(e))
        
        # ทดสอบการดึง log ล่าสุด
        try:
            logs = self.logger_manager.get_recent_logs(limit=10)
            assert len(logs) > 0, "No logs retrieved"
            self.add_test_result("logger_manager", "Get recent logs", True)
        except Exception as e:
            self.add_test_result("logger_manager", "Get recent logs", False, str(e))
        
        # ทดสอบการ cleanup
        try:
            self.logger_manager.cleanup_old_logs()
            self.add_test_result("logger_manager", "Cleanup old logs", True)
        except Exception as e:
            self.add_test_result("logger_manager", "Cleanup old logs", False, str(e))
    
    def test_workflow_monitor(self):
        """ทดสอบ Workflow Monitor"""
        print("\n🔄 Testing Workflow Monitor...")
        
        # ทดสอบการสร้าง workflow
        try:
            workflow_id = self.workflow_monitor.create_workflow(
                workflow_type="test_workflow",
                metadata={"test": True, "created_at": datetime.now().isoformat()}
            )
            assert workflow_id is not None, "Workflow ID is None"
            self.add_test_result("workflow_monitor", "Create workflow", True)
        except Exception as e:
            self.add_test_result("workflow_monitor", "Create workflow", False, str(e))
            return
        
        # ทดสอบการเริ่มต้น workflow
        try:
            success = self.workflow_monitor.start_workflow(workflow_id)
            assert success, "Failed to start workflow"
            self.add_test_result("workflow_monitor", "Start workflow", True)
        except Exception as e:
            self.add_test_result("workflow_monitor", "Start workflow", False, str(e))
        
        # ทดสอบการเพิ่ม steps
        step_ids = []
        for i in range(3):
            try:
                step_id = self.workflow_monitor.add_step(
                    workflow_id=workflow_id,
                    step_name=f"test_step_{i}",
                    module="test_module",
                    metadata={"step_number": i}
                )
                step_ids.append(step_id)
                self.add_test_result("workflow_monitor", f"Add step {i}", True)
            except Exception as e:
                self.add_test_result("workflow_monitor", f"Add step {i}", False, str(e))
        
        # ทดสอบการทำงานของ steps
        for i, step_id in enumerate(step_ids):
            try:
                # เริ่ม step
                self.workflow_monitor.start_step(workflow_id, step_id)
                time.sleep(0.1)  # จำลองการทำงาน
                
                # เสร็จสิ้น step
                if i == 1:  # ให้ step ที่ 2 ล้มเหลว
                    self.workflow_monitor.fail_step(
                        workflow_id, step_id, 
                        error_message="Simulated failure"
                    )
                else:
                    self.workflow_monitor.complete_step(
                        workflow_id, step_id,
                        duration_ms=random.randint(100, 500)
                    )
                
                self.add_test_result("workflow_monitor", f"Process step {i}", True)
            except Exception as e:
                self.add_test_result("workflow_monitor", f"Process step {i}", False, str(e))
        
        # ทดสอบการดึงสถานะ workflow
        try:
            status = self.workflow_monitor.get_workflow_status(workflow_id)
            assert status is not None, "Workflow status is None"
            self.add_test_result("workflow_monitor", "Get workflow status", True)
        except Exception as e:
            self.add_test_result("workflow_monitor", "Get workflow status", False, str(e))
        
        # ทดสอบการดึง workflows ที่กำลังทำงาน
        try:
            active_workflows = self.workflow_monitor.get_active_workflows()
            assert isinstance(active_workflows, list), "Active workflows is not a list"
            self.add_test_result("workflow_monitor", "Get active workflows", True)
        except Exception as e:
            self.add_test_result("workflow_monitor", "Get active workflows", False, str(e))
        
        # ทดสอบการเสร็จสิ้น workflow
        try:
            success = self.workflow_monitor.complete_workflow(workflow_id)
            assert success, "Failed to complete workflow"
            self.add_test_result("workflow_monitor", "Complete workflow", True)
        except Exception as e:
            self.add_test_result("workflow_monitor", "Complete workflow", False, str(e))
    
    def test_performance_tracker(self):
        """ทดสอบ Performance Tracker"""
        print("\n📊 Testing Performance Tracker...")
        
        # ทดสอบการติดตาม system metrics
        try:
            metrics = self.performance_tracker.track_system_metrics()
            assert metrics is not None, "System metrics is None"
            self.add_test_result("performance_tracker", "Track system metrics", True)
        except Exception as e:
            self.add_test_result("performance_tracker", "Track system metrics", False, str(e))
        
        # ทดสอบการติดตาม module operations
        modules = ["test_module_1", "test_module_2", "test_module_3"]
        for module in modules:
            try:
                self.performance_tracker.track_module_operation(
                    module=module,
                    operation="test_operation",
                    duration_ms=random.randint(50, 200),
                    memory_usage_mb=random.uniform(10, 100),
                    cpu_usage_percent=random.uniform(1, 20),
                    status="completed",
                    metadata={"test": True, "module": module}
                )
                self.add_test_result("performance_tracker", f"Track {module} operation", True)
            except Exception as e:
                self.add_test_result("performance_tracker", f"Track {module} operation", False, str(e))
        
        # ทดสอบการดึง performance metrics
        try:
            metrics = self.performance_tracker.get_system_metrics(hours=1)
            assert isinstance(metrics, list), "System metrics is not a list"
            self.add_test_result("performance_tracker", "Get system metrics", True)
        except Exception as e:
            self.add_test_result("performance_tracker", "Get system metrics", False, str(e))
        
        # ทดสอบการดึง module metrics
        try:
            module_metrics = self.performance_tracker.get_module_metrics(hours=1)
            assert isinstance(module_metrics, list), "Module metrics is not a list"
            self.add_test_result("performance_tracker", "Get module metrics", True)
        except Exception as e:
            self.add_test_result("performance_tracker", "Get module metrics", False, str(e))
        
        # ทดสอบการดึง performance summary
        try:
            summary = self.performance_tracker.get_performance_summary()
            assert isinstance(summary, dict), "Performance summary is not a dict"
            self.add_test_result("performance_tracker", "Get performance summary", True)
        except Exception as e:
            self.add_test_result("performance_tracker", "Get performance summary", False, str(e))
    
    def test_alert_system(self):
        """ทดสอบ Alert System"""
        print("\n🚨 Testing Alert System...")
        
        # ทดสอบการสร้าง alerts ระดับต่างๆ
        alert_types = [
            (AlertType.SYSTEM, AlertSeverity.INFO, "System Info Alert"),
            (AlertType.PERFORMANCE, AlertSeverity.WARNING, "Performance Warning"),
            (AlertType.WORKFLOW, AlertSeverity.ERROR, "Workflow Error"),
            (AlertType.SECURITY, AlertSeverity.CRITICAL, "Security Critical")
        ]
        
        alert_ids = []
        for alert_type, severity, title in alert_types:
            try:
                alert_id = self.alert_system.create_alert(
                    alert_type=alert_type,
                    severity=severity,
                    title=title,
                    message=f"Test {severity.value} alert for {alert_type.value}",
                    module="test_module",
                    workflow_id="test_workflow",
                    metadata={"test": True, "type": alert_type.value},
                    auto_dismiss=True,
                    dismiss_after_hours=1
                )
                alert_ids.append(alert_id)
                self.add_test_result("alert_system", f"Create {severity.value} alert", True)
            except Exception as e:
                self.add_test_result("alert_system", f"Create {severity.value} alert", False, str(e))
        
        # ทดสอบการดึง active alerts
        try:
            active_alerts = self.alert_system.get_active_alerts()
            assert isinstance(active_alerts, list), "Active alerts is not a list"
            self.add_test_result("alert_system", "Get active alerts", True)
        except Exception as e:
            self.add_test_result("alert_system", "Get active alerts", False, str(e))
        
        # ทดสอบการยืนยันการรับทราบ alert
        if alert_ids:
            try:
                success = self.alert_system.acknowledge_alert(alert_ids[0], "test_user")
                assert success, "Failed to acknowledge alert"
                self.add_test_result("alert_system", "Acknowledge alert", True)
            except Exception as e:
                self.add_test_result("alert_system", "Acknowledge alert", False, str(e))
        
        # ทดสอบการดึง alert summary
        try:
            summary = self.alert_system.get_alert_summary()
            assert isinstance(summary, dict), "Alert summary is not a dict"
            self.add_test_result("alert_system", "Get alert summary", True)
        except Exception as e:
            self.add_test_result("alert_system", "Get alert summary", False, str(e))
        
        # ทดสอบการปิด alert
        if alert_ids:
            try:
                success = self.alert_system.dismiss_alert(alert_ids[-1], "test_user")
                assert success, "Failed to dismiss alert"
                self.add_test_result("alert_system", "Dismiss alert", True)
            except Exception as e:
                self.add_test_result("alert_system", "Dismiss alert", False, str(e))
    
    def test_integration(self):
        """ทดสอบการทำงานร่วมกันของระบบ"""
        print("\n🔗 Testing System Integration...")
        
        # ทดสอบการทำงานร่วมกันระหว่าง workflow และ logging
        try:
            # สร้าง workflow
            workflow_id = self.workflow_monitor.create_workflow("integration_test")
            self.workflow_monitor.start_workflow(workflow_id)
            
            # เพิ่ม step
            step_id = self.workflow_monitor.add_step(workflow_id, "integration_step", "test_module")
            
            # เริ่ม step
            self.workflow_monitor.start_step(workflow_id, step_id)
            
            # บันทึก log ระหว่างการทำงาน
            self.logger_manager.log(
                module="test_module",
                level="info",
                message="Integration test in progress",
                workflow_id=workflow_id,
                step=step_id,
                status="running"
            )
            
            # ติดตาม performance
            self.performance_tracker.track_module_operation(
                module="test_module",
                operation="integration_test",
                duration_ms=150,
                status="completed"
            )
            
            # สร้าง alert
            self.alert_system.create_alert(
                alert_type=AlertType.WORKFLOW,
                severity=AlertSeverity.INFO,
                title="Integration Test",
                message="Integration test completed successfully",
                workflow_id=workflow_id
            )
            
            # เสร็จสิ้น step และ workflow
            self.workflow_monitor.complete_step(workflow_id, step_id, duration_ms=150)
            self.workflow_monitor.complete_workflow(workflow_id)
            
            self.add_test_result("integration", "Workflow-Logging-Performance-Alert integration", True)
        except Exception as e:
            self.add_test_result("integration", "Workflow-Logging-Performance-Alert integration", False, str(e))
        
        # ทดสอบการดึงข้อมูลแบบรวม
        try:
            # ดึงข้อมูลจากทุกระบบ
            logs = self.logger_manager.get_recent_logs(limit=5)
            workflows = self.workflow_monitor.get_active_workflows()
            performance = self.performance_tracker.get_performance_summary()
            alerts = self.alert_system.get_active_alerts()
            
            # ตรวจสอบว่าข้อมูลถูกดึงได้
            assert isinstance(logs, list), "Logs is not a list"
            assert isinstance(workflows, list), "Workflows is not a list"
            assert isinstance(performance, dict), "Performance is not a dict"
            assert isinstance(alerts, list), "Alerts is not a list"
            
            self.add_test_result("integration", "Data retrieval integration", True)
        except Exception as e:
            self.add_test_result("integration", "Data retrieval integration", False, str(e))
    
    def add_test_result(self, component, test_name, passed, error=None):
        """เพิ่มผลการทดสอบ"""
        result = {
            "test": test_name,
            "passed": passed,
            "error": error
        }
        
        if component in self.test_results:
            self.test_results[component]["tests"].append(result)
            if passed:
                self.test_results[component]["passed"] += 1
            else:
                self.test_results[component]["failed"] += 1
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if error:
            print(f"    Error: {error}")
    
    def print_results(self):
        """แสดงผลการทดสอบ"""
        print("\n" + "="*60)
        print("📊 TEST RESULTS SUMMARY")
        print("="*60)
        
        total_passed = 0
        total_failed = 0
        
        for component, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total = passed + failed
            
            total_passed += passed
            total_failed += failed
            
            success_rate = (passed / total * 100) if total > 0 else 0
            
            print(f"\n{component.upper().replace('_', ' ')}:")
            print(f"  ✅ Passed: {passed}")
            print(f"  ❌ Failed: {failed}")
            print(f"  📈 Success Rate: {success_rate:.1f}%")
            
            # แสดงรายละเอียดการทดสอบที่ล้มเหลว
            failed_tests = [test for test in results["tests"] if not test["passed"]]
            if failed_tests:
                print("  Failed Tests:")
                for test in failed_tests:
                    print(f"    - {test['test']}: {test['error']}")
        
        # สรุปรวม
        total_tests = total_passed + total_failed
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n" + "="*60)
        print("OVERALL SUMMARY:")
        print(f"  ✅ Total Passed: {total_passed}")
        print(f"  ❌ Total Failed: {total_failed}")
        print(f"  📈 Overall Success Rate: {overall_success_rate:.1f}%")
        print("="*60)
        
        # แนะนำ
        if overall_success_rate >= 90:
            print("🎉 Excellent! System is working perfectly!")
        elif overall_success_rate >= 80:
            print("👍 Good! System is working well with minor issues.")
        elif overall_success_rate >= 70:
            print("⚠️ Fair! System needs some improvements.")
        else:
            print("🚨 Poor! System needs significant fixes.")
    
    def cleanup(self):
        """ทำความสะอาดหลังการทดสอบ"""
        try:
            # ลบ test data
            self.logger_manager.cleanup_old_logs()
            print("🧹 Test cleanup completed")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")


def main():
    """Main function"""
    print("🧪 Starting Logging System Integration Test")
    
    # สร้าง tester
    tester = LoggingSystemTester()
    
    try:
        # รันการทดสอบ
        tester.run_all_tests()
        
        # ทำความสะอาด
        tester.cleanup()
        
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
    finally:
        print("\n🏁 Test completed")


if __name__ == "__main__":
    main() 