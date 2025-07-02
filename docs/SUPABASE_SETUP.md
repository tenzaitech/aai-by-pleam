# 🚀 Supabase Setup Guide สำหรับ Backup-byGod

## 📋 ภาพรวม
Supabase เป็น Cloud Database ที่ให้บริการ PostgreSQL พร้อม Real-time Features สำหรับ Backup-byGod system

## 🔧 การตั้งค่า

### 1. **สร้าง Supabase Project**
1. ไปที่ [supabase.com](https://supabase.com)
2. สร้าง account และ project ใหม่
3. เลือก Pro Plan (แนะนำ)
4. เก็บ URL และ API Keys ไว้

### 2. **ตั้งค่า Database Tables**

#### Table: `backup_logs`
```sql
CREATE TABLE backup_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    backup_type VARCHAR(50),
    status VARCHAR(20),
    file_count INTEGER,
    total_size BIGINT,
    duration INTEGER,
    details JSONB
);
```

#### Table: `system_status`
```sql
CREATE TABLE system_status (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cpu_usage DECIMAL(5,2),
    memory_usage DECIMAL(5,2),
    disk_usage DECIMAL(5,2),
    components_ready INTEGER,
    total_components INTEGER,
    system_status VARCHAR(100)
);
```

#### Table: `environment_cards`
```sql
CREATE TABLE environment_cards (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    card_type VARCHAR(50),
    card_data JSONB,
    status VARCHAR(20)
);
```

### 3. **ตั้งค่า API Keys**
1. ไปที่ Project Settings > API
2. คัดลอก:
   - **Project URL**
   - **anon public key**
   - **service_role key** (สำหรับ admin operations)

### 4. **อัปเดต Config File**
แก้ไขไฟล์ `config/supabase_config.json`:

```json
{
  "supabase_url": "https://your-project.supabase.co",
  "supabase_key": "your-anon-key",
  "supabase_service_key": "your-service-key",
  "database_tables": {
    "backup_logs": "backup_logs",
    "system_status": "system_status",
    "environment_cards": "environment_cards"
  },
  "features": {
    "real_time": true,
    "analytics": true,
    "backup_history": true,
    "system_monitoring": true
  }
}
```

## 🚀 การใช้งาน

### 1. **ติดตั้ง Dependencies**
```bash
pip install supabase python-dotenv
```

### 2. **ทดสอบการเชื่อมต่อ**
```python
from core.supabase_integration import supabase_integration

# เชื่อมต่อ
if supabase_integration.connect():
    print("✅ Supabase connected!")
else:
    print("❌ Connection failed")
```

### 3. **บันทึก Backup Log**
```python
backup_data = {
    "type": "full_backup",
    "status": "success",
    "file_count": 150,
    "total_size": 1024000,
    "duration": 30,
    "details": {"source": "local", "compression": "gzip"}
}

supabase_integration.save_backup_log(backup_data)
```

### 4. **ดึงประวัติ Backup**
```python
history = supabase_integration.get_backup_history(limit=10)
for backup in history:
    print(f"{backup['timestamp']}: {backup['backup_type']} - {backup['status']}")
```

### 5. **ดึง Analytics**
```python
analytics = supabase_integration.get_system_analytics()
print(f"Backup Success Rate: {analytics['backup_success_rate']}%")
print(f"Average CPU Usage: {analytics['avg_cpu_usage']}%")
```

## 📊 Features ที่ได้

### 1. **Real-time Backup Logging**
- บันทึกทุกการ backup อัตโนมัติ
- เก็บประวัติการทำงาน
- วิเคราะห์ประสิทธิภาพ

### 2. **System Monitoring**
- เก็บข้อมูล CPU, Memory, Disk usage
- ติดตามสถานะระบบ
- แจ้งเตือนเมื่อมีปัญหา

### 3. **Analytics Dashboard**
- Backup success rate
- Performance metrics
- Usage statistics

### 4. **Environment Cards**
- เก็บข้อมูล environment
- ติดตามการเปลี่ยนแปลง
- แจ้งเตือนเมื่อมีปัญหา

## 🔒 Security

### 1. **Row Level Security (RLS)**
```sql
-- เปิดใช้งาน RLS
ALTER TABLE backup_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_status ENABLE ROW LEVEL SECURITY;

-- สร้าง policy
CREATE POLICY "Allow read access" ON backup_logs
    FOR SELECT USING (true);

CREATE POLICY "Allow insert access" ON backup_logs
    FOR INSERT WITH CHECK (true);
```

### 2. **API Key Management**
- ใช้ anon key สำหรับ client operations
- ใช้ service key สำหรับ admin operations
- เก็บ keys ใน environment variables

## 🚨 Troubleshooting

### 1. **Connection Failed**
- ตรวจสอบ URL และ API keys
- ตรวจสอบ network connection
- ตรวจสอบ Supabase project status

### 2. **Table Not Found**
- ตรวจสอบ table names ใน config
- สร้าง tables ตาม SQL schema
- ตรวจสอบ permissions

### 3. **Permission Denied**
- ตรวจสอบ RLS policies
- ตรวจสอบ API key permissions
- ตรวจสอบ table access rights

## 📈 Monitoring

### 1. **Supabase Dashboard**
- ไปที่ Project Dashboard
- ดู Database usage
- ตรวจสอบ API calls

### 2. **Logs**
- ดู logs ใน Supabase Dashboard
- ตรวจสอบ error messages
- ติดตาม performance

## 🔄 Backup Strategy

### 1. **Automatic Backups**
- Supabase มี automatic backups
- เก็บข้อมูล 7 วัน (Pro Plan)
- Point-in-time recovery

### 2. **Manual Backups**
```sql
-- Export data
pg_dump "postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres" > backup.sql
```

## 💡 Best Practices

1. **ใช้ Environment Variables** สำหรับ sensitive data
2. **เปิดใช้งาน RLS** เพื่อความปลอดภัย
3. **Monitor API usage** เพื่อควบคุมค่าใช้จ่าย
4. **Regular backups** ของ configuration
5. **Error handling** ในทุก operations

## 📞 Support

- **Supabase Docs**: [docs.supabase.com](https://docs.supabase.com)
- **Community**: [github.com/supabase/supabase](https://github.com/supabase/supabase)
- **Discord**: [discord.supabase.com](https://discord.supabase.com) 