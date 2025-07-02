#!/usr/bin/env python3
"""
Test Supabase connection with new credentials
"""

from core.supabase_integration import SupabaseIntegration

def test_supabase():
    try:
        print("🔧 Testing Supabase Integration...")
        
        # Initialize Supabase
        supabase = SupabaseIntegration()
        
        # Display configuration
        print(f"📋 Project Name: {supabase.config.get('project_name')}")
        print(f"🌐 Project URL: {supabase.config.get('supabase_url')}")
        print(f"🔑 Anon Key: {supabase.config.get('supabase_key')[:20]}...")
        print(f"🔐 Service Key: {supabase.config.get('supabase_service_key')[:20]}...")
        
        # Test connection
        print("\n🔍 Testing connection...")
        result = supabase.connect()
        
        if result:
            print("✅ Supabase connection successful!")
            
            # Test basic operations
            print("\n🧪 Testing basic operations...")
            
            # Test inserting a test record
            test_data = {
                "cpu_percent": 25.5,
                "memory_percent": 45.2,
                "disk_percent": 60.1,
                "ready_components": 8,
                "total_components": 10,
                "status_message": "Connection test successful"
            }
            
            insert_result = supabase.save_system_status(test_data)
            if insert_result:
                print("✅ Data insertion successful!")
            else:
                print("❌ Data insertion failed!")
                
        else:
            print("❌ Supabase connection failed!")
            
    except Exception as e:
        print(f"❌ Error testing Supabase: {e}")

if __name__ == "__main__":
    test_supabase() 