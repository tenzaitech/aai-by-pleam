-- ===============================================================================
-- เพิ่ม RLS Policies สำหรับการทดสอบและพัฒนา
-- ===============================================================================
-- หมายเหตุ: ใช้สำหรับการทดสอบ/พัฒนาเท่านั้น
-- สำหรับ production ควรปรับแต่ง policy ให้เหมาะสมกับความต้องการ

-- ===============================================================================
-- ตาราง: conversation_logs
-- ===============================================================================

-- อนุญาต INSERT สำหรับทุกคน (dev)
CREATE POLICY "Allow insert for all (dev)" ON conversation_logs
    FOR INSERT WITH CHECK (true);

-- อนุญาต SELECT สำหรับทุกคน (dev)
CREATE POLICY "Allow select for all (dev)" ON conversation_logs
    FOR SELECT USING (true);

-- อนุญาต UPDATE สำหรับทุกคน (dev)
CREATE POLICY "Allow update for all (dev)" ON conversation_logs
    FOR UPDATE USING (true) WITH CHECK (true);

-- อนุญาต DELETE สำหรับทุกคน (dev)
CREATE POLICY "Allow delete for all (dev)" ON conversation_logs
    FOR DELETE USING (true);

-- ===============================================================================
-- ตาราง: user_profiles
-- ===============================================================================

-- อนุญาต INSERT สำหรับทุกคน (dev)
CREATE POLICY "Allow insert for all (dev)" ON user_profiles
    FOR INSERT WITH CHECK (true);

-- อนุญาต SELECT สำหรับทุกคน (dev)
CREATE POLICY "Allow select for all (dev)" ON user_profiles
    FOR SELECT USING (true);

-- อนุญาต UPDATE สำหรับทุกคน (dev)
CREATE POLICY "Allow update for all (dev)" ON user_profiles
    FOR UPDATE USING (true) WITH CHECK (true);

-- อนุญาต DELETE สำหรับทุกคน (dev)
CREATE POLICY "Allow delete for all (dev)" ON user_profiles
    FOR DELETE USING (true);

-- ===============================================================================
-- ตาราง: system_logs
-- ===============================================================================

-- อนุญาต INSERT สำหรับทุกคน (dev)
CREATE POLICY "Allow insert for all (dev)" ON system_logs
    FOR INSERT WITH CHECK (true);

-- อนุญาต SELECT สำหรับทุกคน (dev)
CREATE POLICY "Allow select for all (dev)" ON system_logs
    FOR SELECT USING (true);

-- อนุญาต UPDATE สำหรับทุกคน (dev)
CREATE POLICY "Allow update for all (dev)" ON system_logs
    FOR UPDATE USING (true) WITH CHECK (true);

-- อนุญาต DELETE สำหรับทุกคน (dev)
CREATE POLICY "Allow delete for all (dev)" ON system_logs
    FOR DELETE USING (true);

-- ===============================================================================
-- ตาราง: knowledge_base
-- ===============================================================================

-- อนุญาต INSERT สำหรับทุกคน (dev)
CREATE POLICY "Allow insert for all (dev)" ON knowledge_base
    FOR INSERT WITH CHECK (true);

-- อนุญาต SELECT สำหรับทุกคน (dev)
CREATE POLICY "Allow select for all (dev)" ON knowledge_base
    FOR SELECT USING (true);

-- อนุญาต UPDATE สำหรับทุกคน (dev)
CREATE POLICY "Allow update for all (dev)" ON knowledge_base
    FOR UPDATE USING (true) WITH CHECK (true);

-- อนุญาต DELETE สำหรับทุกคน (dev)
CREATE POLICY "Allow delete for all (dev)" ON knowledge_base
    FOR DELETE USING (true);

-- ===============================================================================
-- ตาราง: backup_logs
-- ===============================================================================

-- อนุญาต INSERT สำหรับทุกคน (dev)
CREATE POLICY "Allow insert for all (dev)" ON backup_logs
    FOR INSERT WITH CHECK (true);

-- อนุญาต SELECT สำหรับทุกคน (dev)
CREATE POLICY "Allow select for all (dev)" ON backup_logs
    FOR SELECT USING (true);

-- อนุญาต UPDATE สำหรับทุกคน (dev)
CREATE POLICY "Allow update for all (dev)" ON backup_logs
    FOR UPDATE USING (true) WITH CHECK (true);

-- อนุญาต DELETE สำหรับทุกคน (dev)
CREATE POLICY "Allow delete for all (dev)" ON backup_logs
    FOR DELETE USING (true);

-- ===============================================================================
-- ตาราง: health_checks
-- ===============================================================================

-- อนุญาต INSERT สำหรับทุกคน (dev)
CREATE POLICY "Allow insert for all (dev)" ON health_checks
    FOR INSERT WITH CHECK (true);

-- อนุญาต SELECT สำหรับทุกคน (dev)
CREATE POLICY "Allow select for all (dev)" ON health_checks
    FOR SELECT USING (true);

-- อนุญาต UPDATE สำหรับทุกคน (dev)
CREATE POLICY "Allow update for all (dev)" ON health_checks
    FOR UPDATE USING (true) WITH CHECK (true);

-- อนุญาต DELETE สำหรับทุกคน (dev)
CREATE POLICY "Allow delete for all (dev)" ON health_checks
    FOR DELETE USING (true);

-- ===============================================================================
-- ตาราง: alerts
-- ===============================================================================

-- อนุญาต INSERT สำหรับทุกคน (dev)
CREATE POLICY "Allow insert for all (dev)" ON alerts
    FOR INSERT WITH CHECK (true);

-- อนุญาต SELECT สำหรับทุกคน (dev)
CREATE POLICY "Allow select for all (dev)" ON alerts
    FOR SELECT USING (true);

-- อนุญาต UPDATE สำหรับทุกคน (dev)
CREATE POLICY "Allow update for all (dev)" ON alerts
    FOR UPDATE USING (true) WITH CHECK (true);

-- อนุญาต DELETE สำหรับทุกคน (dev)
CREATE POLICY "Allow delete for all (dev)" ON alerts
    FOR DELETE USING (true);

-- ===============================================================================
-- ตาราง: environment_data
-- ===============================================================================

-- อนุญาต INSERT สำหรับทุกคน (dev)
CREATE POLICY "Allow insert for all (dev)" ON environment_data
    FOR INSERT WITH CHECK (true);

-- อนุญาต SELECT สำหรับทุกคน (dev)
CREATE POLICY "Allow select for all (dev)" ON environment_data
    FOR SELECT USING (true);

-- อนุญาต UPDATE สำหรับทุกคน (dev)
CREATE POLICY "Allow update for all (dev)" ON environment_data
    FOR UPDATE USING (true) WITH CHECK (true);

-- อนุญาต DELETE สำหรับทุกคน (dev)
CREATE POLICY "Allow delete for all (dev)" ON environment_data
    FOR DELETE USING (true);

-- ===============================================================================
-- ตาราง: file_management
-- ===============================================================================

-- อนุญาต INSERT สำหรับทุกคน (dev)
CREATE POLICY "Allow insert for all (dev)" ON file_management
    FOR INSERT WITH CHECK (true);

-- อนุญาต SELECT สำหรับทุกคน (dev)
CREATE POLICY "Allow select for all (dev)" ON file_management
    FOR SELECT USING (true);

-- อนุญาต UPDATE สำหรับทุกคน (dev)
CREATE POLICY "Allow update for all (dev)" ON file_management
    FOR UPDATE USING (true) WITH CHECK (true);

-- อนุญาต DELETE สำหรับทุกคน (dev)
CREATE POLICY "Allow delete for all (dev)" ON file_management
    FOR DELETE USING (true);

-- ===============================================================================
-- ตาราง: system_config
-- ===============================================================================

-- อนุญาต INSERT สำหรับทุกคน (dev)
CREATE POLICY "Allow insert for all (dev)" ON system_config
    FOR INSERT WITH CHECK (true);

-- อนุญาต SELECT สำหรับทุกคน (dev)
CREATE POLICY "Allow select for all (dev)" ON system_config
    FOR SELECT USING (true);

-- อนุญาต UPDATE สำหรับทุกคน (dev)
CREATE POLICY "Allow update for all (dev)" ON system_config
    FOR UPDATE USING (true) WITH CHECK (true);

-- อนุญาต DELETE สำหรับทุกคน (dev)
CREATE POLICY "Allow delete for all (dev)" ON system_config
    FOR DELETE USING (true);

-- ===============================================================================
-- ตรวจสอบ Policies ที่สร้าง
-- ===============================================================================

-- ตรวจสอบ policies ที่มีอยู่
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE schemaname = 'public' 
ORDER BY tablename, policyname;

-- ===============================================================================
-- หมายเหตุสำคัญ
-- ===============================================================================

/*
⚠️ หมายเหตุสำคัญ:
1. Policies เหล่านี้เหมาะสำหรับการทดสอบ/พัฒนาเท่านั้น
2. สำหรับ production ควรปรับแต่งให้เหมาะสม เช่น:
   - จำกัดสิทธิ์ตาม user_id
   - ใช้ auth.uid() สำหรับ user ที่ login
   - จำกัดสิทธิ์ตาม role หรือ organization
3. หากต้องการลบ policies เหล่านี้:
   DROP POLICY "Allow insert for all (dev)" ON table_name;
   DROP POLICY "Allow select for all (dev)" ON table_name;
   DROP POLICY "Allow update for all (dev)" ON table_name;
   DROP POLICY "Allow delete for all (dev)" ON table_name;
*/ 