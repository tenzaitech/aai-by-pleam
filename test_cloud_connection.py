#!/usr/bin/env python3
"""
WAWAGOT V.2 Cloud Connection Test
ทดสอบ connection กับ Supabase และ Google Cloud APIs
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from core.cloud_manager import CloudManager

class CloudConnectionTester:
    """ทดสอบ cloud connections"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.cloud_manager = None
        self.test_results = {}
        
    def _setup_logging(self) -> logging.Logger:
        """ตั้งค่า logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    async def setup_connection(self) -> bool:
        """ตั้งค่า connection"""
        try:
            self.cloud_manager = CloudManager()
            success = await self.cloud_manager.setup_all()
            
            if success:
                self.logger.info("✅ Cloud manager setup successful")
                return True
            else:
                self.logger.error("❌ Cloud manager setup failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Connection setup error: {e}")
            return False
    
    async def test_supabase_connection(self) -> Dict[str, Any]:
        """ทดสอบ Supabase connection"""
        try:
            self.logger.info("Testing Supabase connection...")
            
            client = self.cloud_manager.get_supabase_client()
            if not client:
                return {"success": False, "error": "Supabase client not available"}
            
            # Test basic query
            response = client.table('knowledge_base').select('*').limit(1).execute()
            
            self.logger.info("✅ Supabase connection successful")
            return {
                "success": True,
                "message": "Supabase connection working",
                "data": response.data if hasattr(response, 'data') else "Query executed"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Supabase test failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_database_connection(self) -> Dict[str, Any]:
        """ทดสอบ database connection"""
        try:
            self.logger.info("Testing database connection...")
            
            engine = self.cloud_manager.get_db_engine()
            if not engine:
                return {"success": False, "error": "Database engine not available"}
            
            # Test connection
            with engine.connect() as conn:
                result = conn.execute("SELECT version()")
                version = result.fetchone()[0]
            
            self.logger.info("✅ Database connection successful")
            return {
                "success": True,
                "message": "Database connection working",
                "version": version
            }
            
        except Exception as e:
            self.logger.error(f"❌ Database test failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_google_vision_api(self) -> Dict[str, Any]:
        """ทดสอบ Google Vision API"""
        try:
            self.logger.info("Testing Google Vision API...")
            
            client = self.cloud_manager.get_google_vision_client()
            if not client:
                return {"success": False, "error": "Vision client not available"}
            
            # Test with a simple image (you can replace with actual image)
            from google.cloud import vision
            
            # Create a simple test image
            import base64
            test_image_data = base64.b64encode(b"test image data").decode('utf-8')
            
            image = vision.Image(content=test_image_data)
            
            # Test text detection
            response = client.text_detection(image=image)
            
            self.logger.info("✅ Google Vision API test successful")
            return {
                "success": True,
                "message": "Google Vision API working",
                "texts_found": len(response.text_annotations) if response.text_annotations else 0
            }
            
        except Exception as e:
            self.logger.error(f"❌ Google Vision API test failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_google_storage(self) -> Dict[str, Any]:
        """ทดสอบ Google Cloud Storage"""
        try:
            self.logger.info("Testing Google Cloud Storage...")
            
            client = self.cloud_manager.get_google_storage_client()
            if not client:
                return {"success": False, "error": "Storage client not available"}
            
            # List buckets
            buckets = list(client.list_buckets())
            
            self.logger.info("✅ Google Cloud Storage test successful")
            return {
                "success": True,
                "message": "Google Cloud Storage working",
                "buckets_count": len(buckets),
                "buckets": [bucket.name for bucket in buckets[:5]]  # Show first 5 buckets
            }
            
        except Exception as e:
            self.logger.error(f"❌ Google Cloud Storage test failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_schema_tables(self) -> Dict[str, Any]:
        """ทดสอบ database schema"""
        try:
            self.logger.info("Testing database schema...")
            
            engine = self.cloud_manager.get_db_engine()
            if not engine:
                return {"success": False, "error": "Database engine not available"}
            
            # Check required tables
            required_tables = [
                'users', 'knowledge_base', 'commands', 'sessions',
                'learning_patterns', 'results', 'chrome_logs',
                'ai_interactions', 'file_storage', 'system_config'
            ]
            
            existing_tables = []
            missing_tables = []
            
            with engine.connect() as conn:
                for table in required_tables:
                    try:
                        result = conn.execute(f"SELECT 1 FROM {table} LIMIT 1")
                        existing_tables.append(table)
                    except Exception:
                        missing_tables.append(table)
            
            success = len(missing_tables) == 0
            
            if success:
                self.logger.info("✅ Database schema test successful")
            else:
                self.logger.warning(f"⚠️ Some tables missing: {missing_tables}")
            
            return {
                "success": success,
                "message": f"Schema check: {len(existing_tables)}/{len(required_tables)} tables exist",
                "existing_tables": existing_tables,
                "missing_tables": missing_tables,
                "total_tables": len(required_tables)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Schema test failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """run tests ทั้งหมด"""
        try:
            self.logger.info("🚀 Starting cloud connection tests...")
            
            # Setup connection
            if not await self.setup_connection():
                return {"success": False, "error": "Failed to setup connection"}
            
            # Run tests
            tests = [
                ("supabase", self.test_supabase_connection),
                ("database", self.test_database_connection),
                ("google_vision", self.test_google_vision_api),
                ("google_storage", self.test_google_storage),
                ("schema", self.test_schema_tables)
            ]
            
            results = {}
            success_count = 0
            
            for test_name, test_func in tests:
                self.logger.info(f"\n--- Testing {test_name.upper()} ---")
                result = await test_func()
                results[test_name] = result
                
                if result.get("success", False):
                    success_count += 1
            
            # Summary
            total_tests = len(tests)
            overall_success = success_count == total_tests
            
            summary = {
                "success": overall_success,
                "total_tests": total_tests,
                "successful_tests": success_count,
                "failed_tests": total_tests - success_count,
                "results": results
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Test execution failed: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if self.cloud_manager:
                await self.cloud_manager.close_connections()
    
    def print_results(self, results: Dict[str, Any]):
        """แสดงผลการทดสอบ"""
        print("\n" + "="*60)
        print("WAWAGOT V.2 CLOUD CONNECTION TEST RESULTS")
        print("="*60)
        
        if not results.get("success", False):
            print(f"❌ Overall Test Failed: {results.get('error', 'Unknown error')}")
            return
        
        print(f"✅ Overall Test Status: PASSED")
        print(f"📊 Test Summary:")
        print(f"   Total Tests: {results['total_tests']}")
        print(f"   Successful: {results['successful_tests']}")
        print(f"   Failed: {results['failed_tests']}")
        
        print(f"\n📋 Detailed Results:")
        
        for test_name, result in results['results'].items():
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            print(f"   {test_name.upper():15} {status}")
            
            if not result.get("success", False):
                print(f"      Error: {result.get('error', 'Unknown error')}")
            else:
                message = result.get("message", "Test passed")
                print(f"      {message}")
        
        print("\n" + "="*60)

async def main():
    """Main function"""
    tester = CloudConnectionTester()
    
    print("WAWAGOT V.2 Cloud Connection Test")
    print("=" * 40)
    
    results = await tester.run_all_tests()
    tester.print_results(results)
    
    if results.get("success", False):
        print("\n🎉 All cloud connections are working properly!")
        print("You can now use WAWAGOT V.2 with cloud services.")
    else:
        print("\n⚠️ Some connections failed. Please check your configuration.")
        print("Refer to docs/CLOUD_SETUP_GUIDE.md for troubleshooting.")

if __name__ == "__main__":
    asyncio.run(main()) 