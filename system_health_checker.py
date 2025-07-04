"""
System Health Checker for WAWAGOT.AI
ระบบตรวจสอบสุขภาพระบบแบบครบวงจร
"""

import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Import core components
try:
    from core.logger import wawa_logger
    from core.performance_monitor import performance_monitor
    from core.chrome_controller import AIChromeController
    from core.thai_processor import FullThaiProcessor
    from core.ai_integration import MultimodalAIIntegration
    from core.visual_recognition import VisualRecognition
    from core.backup_controller import BackupController
except ImportError as e:
    print(f"❌ Import Error: {e}")
    exit(1)

class SystemHealthChecker:
    def __init__(self):
        self.check_results = {}
        self.overall_health = 0
        self.start_time = time.time()
        
    def run_full_health_check(self) -> Dict:
        """รันการตรวจสอบสุขภาพระบบแบบครบวงจร"""
        print("🏥 เริ่มต้นการตรวจสอบสุขภาพระบบ...")
        
        # เริ่ม Performance Monitor
        performance_monitor.start_monitoring(interval=2.0)
        
        # รันการตรวจสอบต่างๆ
        checks = [
            ("system_resources", self._check_system_resources),
            ("core_components", self._check_core_components),
            ("chrome_controller", self._check_chrome_controller),
            ("ai_components", self._check_ai_components),
            ("file_system", self._check_file_system),
            ("network_connectivity", self._check_network_connectivity),
            ("performance_metrics", self._check_performance_metrics)
        ]
        
        for check_name, check_func in checks:
            try:
                print(f"🔍 ตรวจสอบ {check_name}...")
                result = check_func()
                self.check_results[check_name] = result
                
                if result['status'] == 'healthy':
                    print(f"✅ {check_name}: {result['message']}")
                elif result['status'] == 'warning':
                    print(f"⚠️ {check_name}: {result['message']}")
                else:
                    print(f"❌ {check_name}: {result['message']}")
                    
            except Exception as e:
                error_result = {
                    'status': 'error',
                    'message': f'การตรวจสอบผิดพลาด: {e}',
                    'details': str(e)
                }
                self.check_results[check_name] = error_result
                print(f"❌ {check_name}: {error_result['message']}")
        
        # คำนวณสุขภาพโดยรวม
        self._calculate_overall_health()
        
        # หยุด Performance Monitor
        performance_monitor.stop_monitoring()
        
        # สร้างรายงาน
        report = self._generate_health_report()
        
        # บันทึก log
        wawa_logger.log_system(f"Health Check เสร็จสิ้น - Overall Health: {self.overall_health}%")
        
        return report
    
    def _check_system_resources(self) -> Dict:
        """ตรวจสอบทรัพยากรระบบ"""
        try:
            import psutil
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_healthy = cpu_percent < 80
            
            # Memory
            memory = psutil.virtual_memory()
            memory_healthy = memory.percent < 85
            
            # Disk
            disk = psutil.disk_usage('/')
            disk_healthy = (disk.used / disk.total) * 100 < 90
            
            # ประเมินผล
            if cpu_healthy and memory_healthy and disk_healthy:
                status = 'healthy'
                message = 'ทรัพยากรระบบปกติ'
            elif cpu_percent > 90 or memory.percent > 95:
                status = 'critical'
                message = 'ทรัพยากรระบบวิกฤต'
            else:
                status = 'warning'
                message = 'ทรัพยากรระบบสูง'
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': (disk.used / disk.total) * 100,
                    'memory_available_gb': memory.available / (1024**3)
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'ไม่สามารถตรวจสอบทรัพยากรระบบได้: {e}',
                'details': str(e)
            }
    
    def _check_core_components(self) -> Dict:
        """ตรวจสอบ core components"""
        try:
            components = []
            
            # ตรวจสอบ Thai Processor
            try:
                thai_processor = FullThaiProcessor()
                thai_test = thai_processor.process_thai_text("ทดสอบภาษาไทย")
                components.append(('Thai Processor', True, 'ทำงานปกติ'))
            except Exception as e:
                components.append(('Thai Processor', False, str(e)))
            
            # ตรวจสอบ AI Integration
            try:
                ai_integration = MultimodalAIIntegration()
                ai_test = ai_integration.process_text("test text")
                components.append(('AI Integration', True, 'ทำงานปกติ'))
            except Exception as e:
                components.append(('AI Integration', False, str(e)))
            
            # ตรวจสอบ Visual Recognition
            try:
                visual_recognition = VisualRecognition()
                components.append(('Visual Recognition', True, 'ทำงานปกติ'))
            except Exception as e:
                components.append(('Visual Recognition', False, str(e)))
            
            # ตรวจสอบ Backup Controller
            try:
                backup_controller = BackupController()
                components.append(('Backup Controller', True, 'ทำงานปกติ'))
            except Exception as e:
                components.append(('Backup Controller', False, str(e)))
            
            # ประเมินผล
            working_components = sum(1 for _, working, _ in components if working)
            total_components = len(components)
            
            if working_components == total_components:
                status = 'healthy'
                message = f'Core Components ทำงานปกติ ({working_components}/{total_components})'
            elif working_components >= total_components * 0.7:
                status = 'warning'
                message = f'Core Components ส่วนใหญ่ทำงานได้ ({working_components}/{total_components})'
            else:
                status = 'critical'
                message = f'Core Components มีปัญหา ({working_components}/{total_components})'
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'components': components,
                    'working_count': working_components,
                    'total_count': total_components
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'ไม่สามารถตรวจสอบ core components ได้: {e}',
                'details': str(e)
            }
    
    def _check_chrome_controller(self) -> Dict:
        """ตรวจสอบ Chrome Controller"""
        try:
            chrome_controller = AIChromeController()
            
            # ตรวจสอบว่า Chrome ทำงานได้หรือไม่
            if chrome_controller.driver:
                status = 'healthy'
                message = 'Chrome Controller ทำงานปกติ'
                details = {
                    'driver_session': chrome_controller.driver.session_id,
                    'current_url': chrome_controller.driver.current_url
                }
            else:
                status = 'critical'
                message = 'Chrome Controller ไม่สามารถเริ่มต้นได้'
                details = {'error': 'Driver not initialized'}
            
            return {
                'status': status,
                'message': message,
                'details': details
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'ไม่สามารถตรวจสอบ Chrome Controller ได้: {e}',
                'details': str(e)
            }
    
    def _check_ai_components(self) -> Dict:
        """ตรวจสอบ AI Components"""
        try:
            ai_tests = []
            
            # ทดสอบ Thai Processor
            try:
                thai_processor = FullThaiProcessor()
                test_text = "ระบบ AI ทำงานได้ดี"
                result = thai_processor.process_thai_text(test_text)
                ai_tests.append(('Thai Text Processing', True, f'Confidence: {result.get("confidence", 0):.2f}'))
            except Exception as e:
                ai_tests.append(('Thai Text Processing', False, str(e)))
            
            # ทดสอบ AI Integration
            try:
                ai_integration = MultimodalAIIntegration()
                test_data = {'text': 'test data for AI analysis'}
                result = ai_integration.smart_analysis(test_data)
                ai_tests.append(('AI Analysis', True, f'Confidence: {result.get("confidence", 0):.2f}'))
            except Exception as e:
                ai_tests.append(('AI Analysis', False, str(e)))
            
            # ประเมินผล
            working_tests = sum(1 for _, working, _ in ai_tests if working)
            total_tests = len(ai_tests)
            
            if working_tests == total_tests:
                status = 'healthy'
                message = f'AI Components ทำงานปกติ ({working_tests}/{total_tests})'
            elif working_tests >= total_tests * 0.5:
                status = 'warning'
                message = f'AI Components บางส่วนทำงานได้ ({working_tests}/{total_tests})'
            else:
                status = 'critical'
                message = f'AI Components มีปัญหา ({working_tests}/{total_tests})'
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'ai_tests': ai_tests,
                    'working_count': working_tests,
                    'total_count': total_tests
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'ไม่สามารถตรวจสอบ AI Components ได้: {e}',
                'details': str(e)
            }
    
    def _check_file_system(self) -> Dict:
        """ตรวจสอบระบบไฟล์"""
        try:
            required_dirs = [
                'logs',
                'data',
                'config',
                'core',
                'dashboard',
                'templates'
            ]
            
            missing_dirs = []
            existing_dirs = []
            
            for dir_name in required_dirs:
                if Path(dir_name).exists():
                    existing_dirs.append(dir_name)
                else:
                    missing_dirs.append(dir_name)
            
            if not missing_dirs:
                status = 'healthy'
                message = 'ระบบไฟล์ครบถ้วน'
            elif len(missing_dirs) <= 2:
                status = 'warning'
                message = f'ระบบไฟล์ขาดหายไปบางส่วน ({len(missing_dirs)} directories)'
            else:
                status = 'critical'
                message = f'ระบบไฟล์ขาดหายไปมาก ({len(missing_dirs)} directories)'
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'existing_dirs': existing_dirs,
                    'missing_dirs': missing_dirs,
                    'total_required': len(required_dirs)
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'ไม่สามารถตรวจสอบระบบไฟล์ได้: {e}',
                'details': str(e)
            }
    
    def _check_network_connectivity(self) -> Dict:
        """ตรวจสอบการเชื่อมต่อเครือข่าย"""
        try:
            import requests
            
            test_urls = [
                'https://www.google.com',
                'https://github.com',
                'https://api.github.com'
            ]
            
            successful_connections = 0
            connection_results = []
            
            for url in test_urls:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        successful_connections += 1
                        connection_results.append((url, True, f'Status: {response.status_code}'))
                    else:
                        connection_results.append((url, False, f'Status: {response.status_code}'))
                except Exception as e:
                    connection_results.append((url, False, str(e)))
            
            if successful_connections == len(test_urls):
                status = 'healthy'
                message = 'การเชื่อมต่อเครือข่ายปกติ'
            elif successful_connections >= len(test_urls) * 0.5:
                status = 'warning'
                message = f'การเชื่อมต่อเครือข่ายบางส่วน ({successful_connections}/{len(test_urls)})'
            else:
                status = 'critical'
                message = f'การเชื่อมต่อเครือข่ายมีปัญหา ({successful_connections}/{len(test_urls)})'
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'connection_results': connection_results,
                    'successful_connections': successful_connections,
                    'total_tests': len(test_urls)
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'ไม่สามารถตรวจสอบการเชื่อมต่อเครือข่ายได้: {e}',
                'details': str(e)
            }
    
    def _check_performance_metrics(self) -> Dict:
        """ตรวจสอบ performance metrics"""
        try:
            # รอให้ performance monitor เก็บข้อมูล
            time.sleep(3)
            
            health = performance_monitor.get_system_health()
            metrics_summary = performance_monitor.get_metrics_summary(minutes=2)
            
            health_score = health.get('health_score', 0)
            
            if health_score >= 80:
                status = 'healthy'
                message = f'Performance ดีเยี่ยม (Score: {health_score})'
            elif health_score >= 60:
                status = 'warning'
                message = f'Performance ปกติ (Score: {health_score})'
            else:
                status = 'critical'
                message = f'Performance มีปัญหา (Score: {health_score})'
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'health_score': health_score,
                    'health_status': health.get('status'),
                    'metrics_summary': metrics_summary,
                    'recent_alerts': health.get('recent_alerts', [])
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'ไม่สามารถตรวจสอบ performance metrics ได้: {e}',
                'details': str(e)
            }
    
    def _calculate_overall_health(self):
        """คำนวณสุขภาพโดยรวม"""
        status_scores = {
            'healthy': 100,
            'warning': 60,
            'critical': 20,
            'error': 0
        }
        
        total_score = 0
        valid_checks = 0
        
        for check_name, result in self.check_results.items():
            if result['status'] in status_scores:
                total_score += status_scores[result['status']]
                valid_checks += 1
        
        if valid_checks > 0:
            self.overall_health = total_score / valid_checks
        else:
            self.overall_health = 0
    
    def _generate_health_report(self) -> Dict:
        """สร้างรายงานสุขภาพระบบ"""
        duration = time.time() - self.start_time
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'overall_health_score': self.overall_health,
            'overall_status': self._get_overall_status(),
            'check_results': self.check_results,
            'recommendations': self._generate_recommendations(),
            'summary': {
                'total_checks': len(self.check_results),
                'healthy_checks': sum(1 for r in self.check_results.values() if r['status'] == 'healthy'),
                'warning_checks': sum(1 for r in self.check_results.values() if r['status'] == 'warning'),
                'critical_checks': sum(1 for r in self.check_results.values() if r['status'] == 'critical'),
                'error_checks': sum(1 for r in self.check_results.values() if r['status'] == 'error')
            }
        }
        
        return report
    
    def _get_overall_status(self) -> str:
        """กำหนดสถานะโดยรวม"""
        if self.overall_health >= 80:
            return 'excellent'
        elif self.overall_health >= 60:
            return 'good'
        elif self.overall_health >= 40:
            return 'fair'
        else:
            return 'poor'
    
    def _generate_recommendations(self) -> List[str]:
        """สร้างคำแนะนำ"""
        recommendations = []
        
        # ตรวจสอบ critical issues
        critical_checks = [name for name, result in self.check_results.items() 
                          if result['status'] == 'critical']
        
        if critical_checks:
            recommendations.append(f"⚠️ แก้ไขปัญหา critical ใน: {', '.join(critical_checks)}")
        
        # ตรวจสอบ warning issues
        warning_checks = [name for name, result in self.check_results.items() 
                         if result['status'] == 'warning']
        
        if warning_checks:
            recommendations.append(f"🔧 ปรับปรุงใน: {', '.join(warning_checks)}")
        
        # คำแนะนำทั่วไป
        if self.overall_health < 60:
            recommendations.append("🚨 ระบบต้องการการบำรุงรักษาเร่งด่วน")
        elif self.overall_health < 80:
            recommendations.append("🔧 ควรปรับปรุงประสิทธิภาพระบบ")
        else:
            recommendations.append("✅ ระบบทำงานได้ดี ควรทำการตรวจสอบเป็นประจำ")
        
        return recommendations
    
    def save_report(self, filepath: str = None):
        """บันทึกรายงาน"""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"data/system_health_report_{timestamp}.json"
        
        report = self._generate_health_report()
        
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"✅ บันทึกรายงานไปยัง: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ ไม่สามารถบันทึกรายงานได้: {e}")
            return None

def main():
    """Main function"""
    print("🏥 WAWAGOT.AI System Health Checker")
    print("=" * 50)
    
    checker = SystemHealthChecker()
    report = checker.run_full_health_check()
    
    print("\n" + "=" * 50)
    print("📊 สรุปผลการตรวจสอบ:")
    print(f"🏥 สุขภาพโดยรวม: {report['overall_health_score']:.1f}% ({report['overall_status']})")
    print(f"⏱️ เวลาที่ใช้: {report['duration_seconds']:.2f} วินาที")
    print(f"🔍 จำนวนการตรวจสอบ: {report['summary']['total_checks']}")
    print(f"✅ ผ่าน: {report['summary']['healthy_checks']}")
    print(f"⚠️ เตือน: {report['summary']['warning_checks']}")
    print(f"❌ วิกฤต: {report['summary']['critical_checks']}")
    print(f"💥 ผิดพลาด: {report['summary']['error_checks']}")
    
    print("\n📋 คำแนะนำ:")
    for rec in report['recommendations']:
        print(f"  {rec}")
    
    # บันทึกรายงาน
    checker.save_report()
    
    return report

if __name__ == "__main__":
    main() 