-- WAWAGOT V.2 Database Cleanup Script
-- ล้างข้อมูลทั้งหมดใน Supabase Database
-- ⚠️  WARNING: This will DELETE ALL DATA permanently!

-- Disable triggers temporarily to avoid foreign key conflicts
SET session_replication_role = replica;

-- Clear all data from tables (in reverse dependency order)
-- 1. Clear results (depends on commands)
TRUNCATE TABLE results CASCADE;

-- 2. Clear chrome_logs (depends on sessions)
TRUNCATE TABLE chrome_logs CASCADE;

-- 3. Clear ai_interactions (depends on sessions)
TRUNCATE TABLE ai_interactions CASCADE;

-- 4. Clear commands (depends on users)
TRUNCATE TABLE commands CASCADE;

-- 5. Clear learning_patterns (depends on users)
TRUNCATE TABLE learning_patterns CASCADE;

-- 6. Clear knowledge_base (depends on users)
TRUNCATE TABLE knowledge_base CASCADE;

-- 7. Clear file_storage (depends on users)
TRUNCATE TABLE file_storage CASCADE;

-- 8. Clear sessions (depends on users)
TRUNCATE TABLE sessions CASCADE;

-- 9. Clear users (keep auth.users, just clear our custom user data)
TRUNCATE TABLE users CASCADE;

-- 10. Clear system_config (keep default configs)
DELETE FROM system_config WHERE config_key NOT IN (
    'wawagot_version',
    'ai_models', 
    'chrome_settings',
    'storage_settings'
);

-- Re-enable triggers
SET session_replication_role = DEFAULT;

-- Reset sequences (auto-increment counters)
ALTER SEQUENCE IF EXISTS users_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS knowledge_base_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS commands_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS sessions_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS learning_patterns_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS results_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS chrome_logs_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS ai_interactions_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS file_storage_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS system_config_id_seq RESTART WITH 1;

-- Verify cleanup
SELECT 
    'users' as table_name, COUNT(*) as remaining_rows FROM users
UNION ALL
SELECT 'knowledge_base', COUNT(*) FROM knowledge_base
UNION ALL
SELECT 'commands', COUNT(*) FROM commands
UNION ALL
SELECT 'sessions', COUNT(*) FROM sessions
UNION ALL
SELECT 'learning_patterns', COUNT(*) FROM learning_patterns
UNION ALL
SELECT 'results', COUNT(*) FROM results
UNION ALL
SELECT 'chrome_logs', COUNT(*) FROM chrome_logs
UNION ALL
SELECT 'ai_interactions', COUNT(*) FROM ai_interactions
UNION ALL
SELECT 'file_storage', COUNT(*) FROM file_storage
UNION ALL
SELECT 'system_config', COUNT(*) FROM system_config
ORDER BY table_name;

-- Show message
SELECT '✅ Database cleanup completed successfully!' as status; 