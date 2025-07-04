-- WAWAGOT V.2 Database Schema
-- สำหรับ Supabase PostgreSQL

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS users (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(255) UNIQUE,
    full_name VARCHAR(100),
    avatar_url TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Knowledge Base table
CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    tags TEXT[],
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1536), -- สำหรับ OpenAI embeddings
    confidence_score FLOAT DEFAULT 0.0,
    source_url TEXT,
    source_type VARCHAR(50), -- 'manual', 'web_scrape', 'api', 'file_upload'
    is_public BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Commands table
CREATE TABLE IF NOT EXISTS commands (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    command_hash VARCHAR(64) UNIQUE NOT NULL,
    command_name VARCHAR(255) NOT NULL,
    description TEXT,
    parameters JSONB DEFAULT '{}',
    execution_result JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    error_message TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_name VARCHAR(255),
    session_data JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Learning Patterns table
CREATE TABLE IF NOT EXISTS learning_patterns (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    pattern_name VARCHAR(255) NOT NULL,
    pattern_type VARCHAR(100), -- 'error_fix', 'workflow', 'optimization'
    pattern_data JSONB NOT NULL,
    success_rate FLOAT DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Results table
CREATE TABLE IF NOT EXISTS results (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    command_id UUID REFERENCES commands(id) ON DELETE CASCADE,
    result_type VARCHAR(100), -- 'screenshot', 'data', 'analysis', 'report'
    result_data JSONB NOT NULL,
    file_path TEXT,
    file_size BIGINT,
    mime_type VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chrome Automation Logs
CREATE TABLE IF NOT EXISTS chrome_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    action_type VARCHAR(100), -- 'navigation', 'click', 'input', 'screenshot', 'error'
    url TEXT,
    element_selector TEXT,
    input_data TEXT,
    screenshot_path TEXT,
    error_message TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI Interactions
CREATE TABLE IF NOT EXISTS ai_interactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    interaction_type VARCHAR(100), -- 'chat', 'analysis', 'generation', 'translation'
    input_text TEXT,
    output_text TEXT,
    model_used VARCHAR(100),
    tokens_used INTEGER,
    cost_usd DECIMAL(10,6),
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- File Storage Metadata
CREATE TABLE IF NOT EXISTS file_storage (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100),
    storage_type VARCHAR(50), -- 'local', 'supabase', 'google_cloud'
    storage_url TEXT,
    metadata JSONB DEFAULT '{}',
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System Configuration
CREATE TABLE IF NOT EXISTS system_config (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    config_key VARCHAR(255) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_knowledge_base_user_id ON knowledge_base(user_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_category ON knowledge_base(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_tags ON knowledge_base USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_embedding ON knowledge_base USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_created_at ON knowledge_base(created_at);

CREATE INDEX IF NOT EXISTS idx_commands_user_id ON commands(user_id);
CREATE INDEX IF NOT EXISTS idx_commands_status ON commands(status);
CREATE INDEX IF NOT EXISTS idx_commands_created_at ON commands(created_at);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_is_active ON sessions(is_active);

CREATE INDEX IF NOT EXISTS idx_chrome_logs_user_id ON chrome_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_chrome_logs_session_id ON chrome_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_chrome_logs_action_type ON chrome_logs(action_type);

CREATE INDEX IF NOT EXISTS idx_ai_interactions_user_id ON ai_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_interactions_session_id ON ai_interactions(session_id);
CREATE INDEX IF NOT EXISTS idx_ai_interactions_created_at ON ai_interactions(created_at);

-- Create full-text search indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_base_content_fts ON knowledge_base USING GIN(to_tsvector('english', content));
CREATE INDEX IF NOT EXISTS idx_knowledge_base_title_fts ON knowledge_base USING GIN(to_tsvector('english', title));

-- Create updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_knowledge_base_updated_at BEFORE UPDATE ON knowledge_base FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_learning_patterns_updated_at BEFORE UPDATE ON learning_patterns FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;
ALTER TABLE commands ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE results ENABLE ROW LEVEL SECURITY;
ALTER TABLE chrome_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE file_storage ENABLE ROW LEVEL SECURITY;

-- Users can only access their own data
CREATE POLICY "Users can view own profile" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON users FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own knowledge" ON knowledge_base FOR SELECT USING (auth.uid() = user_id OR is_public = true);
CREATE POLICY "Users can insert own knowledge" ON knowledge_base FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own knowledge" ON knowledge_base FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own knowledge" ON knowledge_base FOR DELETE USING (auth.uid() = user_id);

-- Similar policies for other tables...
CREATE POLICY "Users can view own commands" ON commands FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own commands" ON commands FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own commands" ON commands FOR UPDATE USING (auth.uid() = user_id);

-- Insert default system configuration
INSERT INTO system_config (config_key, config_value, description) VALUES
('wawagot_version', '"2.0.0"', 'Current WAWAGOT version'),
('ai_models', '{"default": "gpt-4", "vision": "gpt-4-vision-preview", "embedding": "text-embedding-ada-002"}', 'AI model configuration'),
('chrome_settings', '{"headless": false, "timeout": 30000, "user_agent": "WAWAGOT/2.0"}', 'Chrome automation settings'),
('storage_settings', '{"local_path": "./data", "cloud_backup": true}', 'Storage configuration')
ON CONFLICT (config_key) DO NOTHING; 