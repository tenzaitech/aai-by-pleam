import os
import re
import requests

# โหลด environment variables จากไฟล์ .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ โหลดไฟล์ .env สำเร็จ")
except ImportError:
    print("⚠️ ไม่พบ python-dotenv กรุณารัน: pip install python-dotenv")
except Exception as e:
    print(f"⚠️ ไม่สามารถโหลดไฟล์ .env: {e}")

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = None

print("\n==============================")
print("🔍 ENVIRONMENT VARIABLES TEST")
print("==============================\n")

# 1. อ่านค่าจาก environment
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase_service_role = os.getenv('SUPABASE_SERVICE_ROLE')
supabase_db_password = os.getenv('SUPABASE_DB_PASSWORD')
google_client_id = os.getenv('GOOGLE_CLIENT_ID')
google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
google_api_key = os.getenv('GOOGLE_API_KEY')
odoo_username = os.getenv('ODOO_USERNAME')
odoo_db = os.getenv('ODOO_DB')
odoo_url = os.getenv('ODOO_URL')
odoo_api_key = os.getenv('ODOO_API_KEY')

# 2. ตรวจสอบรูปแบบเบื้องต้น
results = []
def check(key, value, pattern=None, required=True):
    if not value:
        results.append((key, False, '❌ ไม่พบค่าใน environment'))
        return False
    if pattern and not re.match(pattern, value):
        results.append((key, False, '⚠️ รูปแบบไม่ถูกต้อง'))
        return False
    results.append((key, True, '✅'))
    return True

# SUPABASE
check('SUPABASE_URL', supabase_url, r'^https://[a-z0-9]+\.supabase\.co$')
check('SUPABASE_KEY', supabase_key, r'^[A-Za-z0-9\._-]+$')
check('SUPABASE_SERVICE_ROLE', supabase_service_role, r'^[A-Za-z0-9\._-]+$')
check('SUPABASE_DB_PASSWORD', supabase_db_password, r'^[A-Za-z0-9]+$')

# GOOGLE
check('GOOGLE_CLIENT_ID', google_client_id, r'^[0-9]+-[a-z0-9]+\.apps\.googleusercontent\.com$')
check('GOOGLE_CLIENT_SECRET', google_client_secret, r'^[A-Za-z0-9-_]+$')
check('GOOGLE_API_KEY', google_api_key, r'^AIza[0-9A-Za-z_-]{35,}$')

# ODOO
check('ODOO_USERNAME', odoo_username, r'^.+@.+\..+$')
check('ODOO_DB', odoo_db, r'^[A-Za-z0-9_]+$')
check('ODOO_URL', odoo_url, r'^https://.+$')
check('ODOO_API_KEY', odoo_api_key, r'^[A-Za-z0-9]+$')

# 3. ทดสอบการเชื่อมต่อ SUPABASE
supabase_connect = False
if supabase_url and supabase_key and create_client:
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        data = supabase.table('test').select('*').limit(1).execute()
        supabase_connect = True
        results.append(('SUPABASE_CONNECTION', True, '✅ เชื่อมต่อ Supabase สำเร็จ'))
    except Exception as e:
        results.append(('SUPABASE_CONNECTION', False, f'❌ เชื่อมต่อ Supabase ไม่สำเร็จ: {e}'))
else:
    results.append(('SUPABASE_CONNECTION', False, '⚠️ ไม่สามารถทดสอบการเชื่อมต่อ Supabase'))

# 4. ทดสอบ Google API Key (format only)
if google_api_key:
    try:
        resp = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?address=Bangkok&key={google_api_key}', timeout=5)
        if resp.status_code == 200:
            results.append(('GOOGLE_API_KEY_TEST', True, '✅ Google API Key ใช้งานได้ (HTTP 200)'))
        else:
            results.append(('GOOGLE_API_KEY_TEST', False, f'⚠️ Google API Key อาจไม่ถูกต้อง (HTTP {resp.status_code})'))
    except Exception as e:
        results.append(('GOOGLE_API_KEY_TEST', False, f'❌ ทดสอบ Google API Key ไม่สำเร็จ: {e}'))
else:
    results.append(('GOOGLE_API_KEY_TEST', False, '⚠️ ไม่สามารถทดสอบ Google API Key'))

# 5. ทดสอบ Odoo API Key (format only)
if odoo_url and odoo_api_key:
    results.append(('ODOO_API_KEY_TEST', True, '✅ ตรวจสอบรูปแบบ Odoo API Key สำเร็จ (format only)'))
else:
    results.append(('ODOO_API_KEY_TEST', False, '⚠️ ไม่สามารถทดสอบ Odoo API Key'))

# 6. สรุปผล
print("\n📋 ผลการตรวจสอบ ENVIRONMENT VARIABLES\n------------------------------")
for key, ok, msg in results:
    print(f"{key:28} : {msg}")

print("\nเสร็จสิ้นการตรวจสอบ ENVIRONMENT VARIABLES\n") 