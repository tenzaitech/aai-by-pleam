-- ===============================================================================
-- WAWAGOT.AI - สร้างตารางที่จำเป็นทั้งหมด
-- ===============================================================================
-- สร้างเมื่อ: 2024-12-19
-- วัตถุประสงค์: สร้างตารางที่จำเป็นสำหรับระบบ WAWAGOT.AI ใน Supabase
-- ===============================================================================

-- 1. ตารางบันทึกบทสนทนา
CREATE TABLE IF NOT EXISTS conversation_logs (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    user_message TEXT NOT NULL,
    ai_response TEXT,
    timestamp TIMESTAMP DEFAULT NOW(),
    model_used VARCHAR(100),
    tokens_used INTEGER,
    response_time_ms INTEGER,
    status VARCHAR(50) DEFAULT 'success',
    metadata JSONB
);

-- 2. ตารางข้อมูลผู้ใช้
CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255),
    username VARCHAR(100),
    full_name VARCHAR(200),
    avatar_url TEXT,
    preferences JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 3. ตารางบันทึกระบบ
CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL,
    component VARCHAR(100),
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    metadata JSONB,
    stack_trace TEXT
);

-- 4. ตารางฐานความรู้
CREATE TABLE IF NOT EXISTS knowledge_base (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    tags TEXT[],
    source VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB
);

-- 5. ตารางบันทึกการสำรองข้อมูล
CREATE TABLE IF NOT EXISTS backup_logs (
    id SERIAL PRIMARY KEY,
    backup_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    file_path TEXT,
    file_size BIGINT,
    start_time TIMESTAMP DEFAULT NOW(),
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    records_backed_up INTEGER,
    error_message TEXT,
    metadata JSONB
);

-- 6. ตารางการตรวจสอบระบบ
CREATE TABLE IF NOT EXISTS health_checks (
    id SERIAL PRIMARY KEY,
    check_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    response_time_ms INTEGER,
    timestamp TIMESTAMP DEFAULT NOW(),
    details JSONB,
    error_message TEXT
);

-- 7. ตารางการแจ้งเตือน
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    resolved_by VARCHAR(255),
    metadata JSONB
);

-- 8. ตารางข้อมูลสภาพแวดล้อม
CREATE TABLE IF NOT EXISTS environment_data (
    id SERIAL PRIMARY KEY,
    component VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value TEXT NOT NULL,
    unit VARCHAR(50),
    timestamp TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- 9. ตารางการจัดการไฟล์
CREATE TABLE IF NOT EXISTS file_management (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(100),
    mime_type VARCHAR(100),
    uploaded_by VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT NOW(),
    is_processed BOOLEAN DEFAULT FALSE,
    processing_status VARCHAR(50),
    metadata JSONB
);

-- 10. ตารางการตั้งค่าระบบ
CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(255) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    config_type VARCHAR(50) DEFAULT 'string',
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by VARCHAR(255)
);

-- ===============================================================================
-- เพิ่มข้อมูลตัวอย่าง
-- ===============================================================================

-- เพิ่มข้อมูลการตั้งค่าระบบ
INSERT INTO system_config (config_key, config_value, config_type, description) VALUES
('system_name', 'WAWAGOT.AI', 'string', 'ชื่อระบบ'),
('version', '2.0.0', 'string', 'เวอร์ชันระบบ'),
('max_conversation_length', '1000', 'integer', 'ความยาวสูงสุดของบทสนทนา'),
('ai_model', 'gpt-4', 'string', 'โมเดล AI ที่ใช้'),
('backup_retention_days', '90', 'integer', 'จำนวนวันเก็บข้อมูลสำรอง'),
('log_level', 'INFO', 'string', 'ระดับการบันทึก log'),
('max_file_size_mb', '100', 'integer', 'ขนาดไฟล์สูงสุด (MB)'),
('session_timeout_minutes', '30', 'integer', 'เวลาหมดอายุ session (นาที)'),
('enable_notifications', 'true', 'boolean', 'เปิดใช้งานการแจ้งเตือน'),
('auto_backup_enabled', 'true', 'boolean', 'เปิดใช้งานการสำรองข้อมูลอัตโนมัติ')
ON CONFLICT (config_key) DO NOTHING;

-- เพิ่มข้อมูลฐานความรู้
INSERT INTO knowledge_base (title, content, category, tags, source, created_by) VALUES
('การใช้งานระบบ WAWAGOT.AI', 'WAWAGOT.AI เป็นระบบ AI ที่ช่วยในการจัดการข้อมูลและบทสนทนา', 'system', ARRAY['ai', 'system', 'guide'], 'system', 'system'),
('การตั้งค่า Environment Variables', 'วิธีการตั้งค่า environment variables สำหรับระบบ WAWAGOT.AI', 'setup', ARRAY['setup', 'env', 'config'], 'system', 'system'),
('การเชื่อมต่อ Supabase', 'ขั้นตอนการเชื่อมต่อและใช้งาน Supabase ในระบบ WAWAGOT.AI', 'integration', ARRAY['supabase', 'database', 'integration'], 'system', 'system'),
('การใช้งาน Google API', 'วิธีการใช้งาน Google API ต่างๆ ในระบบ WAWAGOT.AI', 'integration', ARRAY['google', 'api', 'integration'], 'system', 'system'),
('การจัดการไฟล์และ Backup', 'วิธีการจัดการไฟล์และการสำรองข้อมูลในระบบ WAWAGOT.AI', 'backup', ARRAY['backup', 'file', 'management'], 'system', 'system')
ON CONFLICT DO NOTHING;

-- เพิ่มข้อมูลการตรวจสอบระบบ
INSERT INTO health_checks (check_type, status, response_time_ms, details) VALUES
('database_connection', 'success', 150, '{"database": "supabase", "connection": "stable"}'),
('api_connection', 'success', 200, '{"api": "google", "status": "connected"}'),
('file_system', 'success', 50, '{"path": "/", "available_space": "1.2TB"}'),
('memory_usage', 'success', 10, '{"usage_percent": 45, "available": "8GB"}'),
('cpu_usage', 'success', 5, '{"usage_percent": 25, "cores": 8}')
ON CONFLICT DO NOTHING;

-- ===============================================================================
-- สร้าง Indexes สำหรับประสิทธิภาพ
-- ===============================================================================

-- Index สำหรับ conversation_logs
CREATE INDEX IF NOT EXISTS idx_conversation_logs_session_id ON conversation_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_logs_user_id ON conversation_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_logs_timestamp ON conversation_logs(timestamp);

-- Index สำหรับ user_profiles
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_username ON user_profiles(username);

-- Index สำหรับ system_logs
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level);
CREATE INDEX IF NOT EXISTS idx_system_logs_component ON system_logs(component);
CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp);

-- Index สำหรับ knowledge_base
CREATE INDEX IF NOT EXISTS idx_knowledge_base_category ON knowledge_base(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_tags ON knowledge_base USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_created_at ON knowledge_base(created_at);

-- Index สำหรับ backup_logs
CREATE INDEX IF NOT EXISTS idx_backup_logs_type ON backup_logs(backup_type);
CREATE INDEX IF NOT EXISTS idx_backup_logs_status ON backup_logs(status);
CREATE INDEX IF NOT EXISTS idx_backup_logs_start_time ON backup_logs(start_time);

-- Index สำหรับ health_checks
CREATE INDEX IF NOT EXISTS idx_health_checks_type ON health_checks(check_type);
CREATE INDEX IF NOT EXISTS idx_health_checks_status ON health_checks(status);
CREATE INDEX IF NOT EXISTS idx_health_checks_timestamp ON health_checks(timestamp);

-- Index สำหรับ alerts
CREATE INDEX IF NOT EXISTS idx_alerts_type ON alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp);
CREATE INDEX IF NOT EXISTS idx_alerts_resolved ON alerts(is_resolved);

-- Index สำหรับ environment_data
CREATE INDEX IF NOT EXISTS idx_environment_data_component ON environment_data(component);
CREATE INDEX IF NOT EXISTS idx_environment_data_metric ON environment_data(metric_name);
CREATE INDEX IF NOT EXISTS idx_environment_data_timestamp ON environment_data(timestamp);

-- Index สำหรับ file_management
CREATE INDEX IF NOT EXISTS idx_file_management_type ON file_management(file_type);
CREATE INDEX IF NOT EXISTS idx_file_management_uploaded_by ON file_management(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_file_management_uploaded_at ON file_management(uploaded_at);

-- Index สำหรับ system_config
CREATE INDEX IF NOT EXISTS idx_system_config_key ON system_config(config_key);
CREATE INDEX IF NOT EXISTS idx_system_config_type ON system_config(config_type);
CREATE INDEX IF NOT EXISTS idx_system_config_active ON system_config(is_active);

-- ===============================================================================
-- สร้าง RLS (Row Level Security) Policies
-- ===============================================================================

-- เปิดใช้งาน RLS สำหรับทุกตาราง
ALTER TABLE conversation_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;
ALTER TABLE backup_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_checks ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE environment_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE file_management ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_config ENABLE ROW LEVEL SECURITY;

-- สร้าง Policy สำหรับการเข้าถึงข้อมูล (ตัวอย่าง)
-- หมายเหตุ: ปรับแต่งตามความต้องการของระบบ

-- Policy สำหรับ conversation_logs - ผู้ใช้สามารถดูข้อมูลของตัวเอง
CREATE POLICY "Users can view own conversation logs" ON conversation_logs
    FOR SELECT USING (auth.uid()::text = user_id);

-- Policy สำหรับ user_profiles - ผู้ใช้สามารถดูและแก้ไขข้อมูลของตัวเอง
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid()::text = user_id);

-- Policy สำหรับ system_config - อ่านได้ทุกคน แก้ไขได้เฉพาะ admin
CREATE POLICY "Anyone can view system config" ON system_config
    FOR SELECT USING (true);

-- ===============================================================================
-- สร้าง Functions และ Triggers
-- ===============================================================================

-- Function สำหรับอัพเดท updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger สำหรับอัพเดท updated_at ในตารางที่มีฟิลด์นี้
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_base_updated_at BEFORE UPDATE ON knowledge_base
    FOR EOW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ===============================================================================
-- สร้าง Views สำหรับการใช้งานทั่วไป
-- ===============================================================================

-- View สำหรับสรุปข้อมูลระบบ
CREATE OR REPLACE VIEW system_summary AS
SELECT 
    (SELECT COUNT(*) FROM conversation_logs) as total_conversations,
    (SELECT COUNT(*) FROM user_profiles WHERE is_active = true) as active_users,
    (SELECT COUNT(*) FROM system_logs WHERE level = 'ERROR' AND timestamp > NOW() - INTERVAL '24 hours') as errors_last_24h,
    (SELECT COUNT(*) FROM alerts WHERE is_resolved = false) as active_alerts,
    (SELECT COUNT(*) FROM backup_logs WHERE status = 'success' AND start_time > NOW() - INTERVAL '7 days') as successful_backups_7d;

-- View สำหรับข้อมูลการใช้งานล่าสุด
CREATE OR REPLACE VIEW recent_activity AS
SELECT 
    'conversation' as activity_type,
    session_id,
    user_id,
    timestamp,
    'User message: ' || LEFT(user_message, 50) as description
FROM conversation_logs 
WHERE timestamp > NOW() - INTERVAL '24 hours'
UNION ALL
SELECT 
    'system_log' as activity_type,
    session_id,
    user_id,
    timestamp,
    'System log: ' || LEFT(message, 50) as description
FROM system_logs 
WHERE timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;

-- ===============================================================================
-- เสร็จสิ้นการสร้างตาราง
-- ===============================================================================
SELECT 'WAWAGOT.AI tables created successfully!' as status; 