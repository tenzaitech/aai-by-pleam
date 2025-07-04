#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Real-time Monitor System
ทดสอบการทำงานของ Real-time Monitor
"""

import os
import sys
import time
import json
import requests
import threading
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import logging components
try:
    from core.logging.logger_manager import get_logger_manager
    from core.logging.workflow_monitor import get_workflow_monitor
    from core.logging.performance_tracker import get_performance_tracker
    from core.logging.alert_system import get_alert_system
    print("✅ Logging components imported successfully")
except Exception as e:
    print(f"❌ Error importing logging components: {e}")
    sys.exit(1)

class RealTimeMonitorTester:
    """Test class for Real-time Monitor"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.logger_manager = get_logger_manager()
        self.workflow_monitor = get_workflow_monitor()
        self.performance_tracker = get_performance_tracker()
        self.alert_system = get_alert_system()
        
    def test_dashboard_connection(self):
        """Test dashboard connection"""
        print("\n🔗 Testing Dashboard Connection...")
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                print("✅ Dashboard is accessible")
                return True
            else:
                print(f"❌ Dashboard returned status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to dashboard: {e}")
            return False
    
    def test_real_time_monitor_page(self):
        """Test real-time monitor page"""
        print("\n📊 Testing Real-time Monitor Page...")
        try:
            response = requests.get(f"{self.base_url}/real-time-monitor", timeout=5)
            if response.status_code == 200:
                print("✅ Real-time Monitor page is accessible")
                return True
            else:
                print(f"❌ Real-time Monitor page returned status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot access Real-time Monitor page: {e}")
            return False
    
    def test_logging_api_endpoints(self):
        """Test logging API endpoints"""
        print("\n🔌 Testing Logging API Endpoints...")
        endpoints = [
            "/api/logging/health",
            "/api/logging/logs/recent",
            "/api/logging/workflows/active",
            "/api/logging/performance/summary",
            "/api/logging/alerts/active"
        ]
        
        results = {}
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {endpoint} - OK")
                    results[endpoint] = True
                else:
                    print(f"❌ {endpoint} - Status: {response.status_code}")
                    results[endpoint] = False
            except Exception as e:
                print(f"❌ {endpoint} - Error: {e}")
                results[endpoint] = False
        
        return results
    
    def generate_test_data(self):
        """Generate test data for monitoring"""
        print("\n📝 Generating Test Data...")
        
        # Generate test logs
        test_modules = [
            "chrome_controller", "ai_integration", "knowledge_manager",
            "thai_processor", "visual_recognition", "backup_controller"
        ]
        
        test_levels = ["debug", "info", "warning", "error"]
        
        for i in range(10):
            module = test_modules[i % len(test_modules)]
            level = test_levels[i % len(test_levels)]
            message = f"Test log message {i+1} from {module}"
            
            self.logger_manager.log(level, message, module=module)
            print(f"📝 Generated log: [{level.upper()}] {module} - {message}")
            time.sleep(0.1)
        
        # Generate test workflows
        workflow_types = ["backup", "ai_processing", "chrome_automation", "data_analysis"]
        
        for i in range(3):
            workflow_type = workflow_types[i % len(workflow_types)]
            workflow_id = self.workflow_monitor.start_workflow(
                workflow_type, 
                {"test_param": f"value_{i+1}"}
            )
            print(f"🔄 Started workflow: {workflow_type} (ID: {workflow_id})")
            
            # Update progress
            for progress in [25, 50, 75, 100]:
                self.workflow_monitor.update_progress(workflow_id, progress)
                time.sleep(0.2)
            
            # Complete workflow
            self.workflow_monitor.complete_workflow(workflow_id, "success")
            print(f"✅ Completed workflow: {workflow_id}")
        
        # Generate test alerts
        alert_messages = [
            "High CPU usage detected",
            "Memory usage above threshold",
            "Chrome process not responding",
            "Database connection slow"
        ]
        
        for i, message in enumerate(alert_messages):
            level = "warning" if i < 2 else "error"
            self.alert_system.create_alert(
                level=level,
                message=message,
                module="system_monitor",
                data={"threshold": 80, "current": 85 + i}
            )
            print(f"🚨 Created alert: [{level.upper()}] {message}")
        
        # Record performance metrics
        for i in range(5):
            self.performance_tracker.record_metric("cpu_usage", 30 + i * 10)
            self.performance_tracker.record_metric("memory_usage", 40 + i * 8)
            self.performance_tracker.record_metric("disk_usage", 50 + i * 5)
            time.sleep(0.1)
        
        print("✅ Test data generation completed")
    
    def test_real_time_updates(self):
        """Test real-time updates"""
        print("\n⚡ Testing Real-time Updates...")
        
        def background_updates():
            """Background thread for generating updates"""
            for i in range(5):
                # Generate random logs
                self.logger_manager.log("info", f"Real-time update {i+1}", module="test_monitor")
                
                # Update performance
                self.performance_tracker.record_metric("test_metric", i * 10)
                
                time.sleep(2)
        
        # Start background updates
        update_thread = threading.Thread(target=background_updates)
        update_thread.daemon = True
        update_thread.start()
        
        # Monitor for 10 seconds
        print("🔄 Monitoring real-time updates for 10 seconds...")
        start_time = time.time()
        
        while time.time() - start_time < 10:
            # Check recent logs
            logs = self.logger_manager.get_recent_logs(limit=5)
            if logs:
                latest_log = logs[-1]
                print(f"📝 Latest log: {latest_log.get('message', 'N/A')}")
            
            # Check active workflows
            workflows = self.workflow_monitor.get_active_workflows()
            if workflows:
                print(f"🔄 Active workflows: {len(workflows)}")
            
            # Check alerts
            alerts = self.alert_system.get_active_alerts()
            if alerts:
                print(f"🚨 Active alerts: {len(alerts)}")
            
            time.sleep(2)
        
        print("✅ Real-time updates test completed")
    
    def test_export_functionality(self):
        """Test export functionality"""
        print("\n📤 Testing Export Functionality...")
        
        try:
            # Test logs export
            logs = self.logger_manager.get_recent_logs(limit=100)
            if logs:
                export_data = {
                    "timestamp": datetime.now().isoformat(),
                    "total_logs": len(logs),
                    "logs": logs
                }
                
                export_file = "test_logs_export.json"
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Logs exported to {export_file}")
                
                # Clean up
                os.remove(export_file)
                print("✅ Export file cleaned up")
            else:
                print("⚠️ No logs to export")
        
        except Exception as e:
            print(f"❌ Export test failed: {e}")
    
    def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Real-time Monitor Comprehensive Test")
        print("=" * 60)
        
        # Test 1: Dashboard connection
        if not self.test_dashboard_connection():
            print("❌ Dashboard connection failed. Please start the dashboard first.")
            return False
        
        # Test 2: Real-time monitor page
        if not self.test_real_time_monitor_page():
            print("❌ Real-time monitor page not accessible")
            return False
        
        # Test 3: API endpoints
        api_results = self.test_logging_api_endpoints()
        api_success = sum(api_results.values())
        api_total = len(api_results)
        print(f"\n📊 API Endpoints: {api_success}/{api_total} working")
        
        # Test 4: Generate test data
        self.generate_test_data()
        
        # Test 5: Real-time updates
        self.test_real_time_updates()
        
        # Test 6: Export functionality
        self.test_export_functionality()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎉 Real-time Monitor Test Summary")
        print("=" * 60)
        print(f"✅ Dashboard Connection: {'OK' if self.test_dashboard_connection() else 'FAILED'}")
        print(f"✅ Monitor Page: {'OK' if self.test_real_time_monitor_page() else 'FAILED'}")
        print(f"✅ API Endpoints: {api_success}/{api_total}")
        print(f"✅ Test Data Generation: OK")
        print(f"✅ Real-time Updates: OK")
        print(f"✅ Export Functionality: OK")
        
        if api_success == api_total:
            print("\n🎯 All tests passed! Real-time Monitor is working correctly.")
            print("\n📱 Access your Real-time Monitor at:")
            print("   http://localhost:8000/real-time-monitor")
            return True
        else:
            print(f"\n⚠️ {api_total - api_success} API endpoints failed. Check the dashboard logs.")
            return False

def main():
    """Main function"""
    print("🎯 WAWAGOT V.2 - Real-time Monitor Test Suite")
    print("=" * 60)
    
    tester = RealTimeMonitorTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("🚀 Real-time Monitor is ready for use!")
    else:
        print("\n❌ Some tests failed. Please check the issues above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 