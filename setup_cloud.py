#!/usr/bin/env python3
"""
WAWAGOT V.2 Cloud Setup Script
ตั้งค่า connection กับ Supabase และ Google Cloud APIs
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

class CloudSetup:
    """จัดการ cloud setup"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.config_path = Path("config/cloud_config.json")
        self.env_template_path = Path("config/.env.template")
        
    def _setup_logging(self) -> logging.Logger:
        """ตั้งค่า logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def create_env_template(self) -> bool:
        """สร้าง .env template file"""
        try:
            env_content = """# WAWAGOT V.2 Environment Variables
# Copy this file to .env and fill in your values

# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Supabase Database (for direct access)
SUPABASE_DB_HOST=your_supabase_db_host
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your_supabase_db_password

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT_ID=your_google_cloud_project_id
GOOGLE_CLOUD_CREDENTIALS_FILE=path/to/service-account-key.json

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# System Configuration
WAWAGOT_ENVIRONMENT=development
WAWAGOT_DEBUG=true
WAWAGOT_LOG_LEVEL=INFO

# Storage Configuration
LOCAL_STORAGE_PATH=./data
CLOUD_BACKUP_ENABLED=true

# Security
JWT_SECRET_KEY=your_jwt_secret_key
ENCRYPTION_KEY=your_encryption_key
"""
            
            self.env_template_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.env_template_path, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            self.logger.info(f"Created .env template: {self.env_template_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create .env template: {e}")
            return False
    
    def create_config_template(self) -> bool:
        """สร้าง config template"""
        try:
            config_content = {
                "supabase": {
                    "url": "${SUPABASE_URL}",
                    "key": "${SUPABASE_ANON_KEY}",
                    "service_role_key": "${SUPABASE_SERVICE_ROLE_KEY}",
                    "database": {
                        "host": "${SUPABASE_DB_HOST}",
                        "port": 5432,
                        "database": "postgres",
                        "user": "postgres",
                        "password": "${SUPABASE_DB_PASSWORD}"
                    }
                },
                "google_cloud": {
                    "project_id": "${GOOGLE_CLOUD_PROJECT_ID}",
                    "credentials_file": "${GOOGLE_CLOUD_CREDENTIALS_FILE}",
                    "apis": {
                        "vision": {
                            "enabled": True,
                            "features": ["TEXT_DETECTION", "OBJECT_LOCALIZATION", "FACE_DETECTION"]
                        },
                        "speech": {
                            "enabled": True,
                            "language_code": "th-TH"
                        },
                        "translation": {
                            "enabled": True,
                            "source_language": "th",
                            "target_language": "en"
                        },
                        "natural_language": {
                            "enabled": True,
                            "features": ["SENTIMENT_ANALYSIS", "ENTITY_ANALYSIS"]
                        },
                        "storage": {
                            "enabled": True,
                            "bucket_name": "wawagot-v2-storage"
                        }
                    }
                },
                "wawagot": {
                    "environment": "${WAWAGOT_ENVIRONMENT}",
                    "features": {
                        "real_time_sync": True,
                        "cloud_storage": True,
                        "ai_enhancement": True,
                        "multi_user": True
                    }
                }
            }
            
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_content, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Created config template: {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create config template: {e}")
            return False
    
    def create_directories(self) -> bool:
        """สร้าง directories ที่จำเป็น"""
        try:
            directories = [
                "config",
                "data",
                "logs",
                "temp",
                "screenshots",
                "database/migrations",
                "backups"
            ]
            
            for directory in directories:
                dir_path = Path(directory)
                dir_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created directory: {dir_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create directories: {e}")
            return False
    
    def create_requirements_cloud(self) -> bool:
        """สร้าง requirements file สำหรับ cloud dependencies"""
        try:
            requirements_content = """# WAWAGOT V.2 Cloud Dependencies
# Supabase
supabase>=2.0.0
postgrest>=0.13.0

# Google Cloud
google-cloud-vision>=3.4.0
google-cloud-speech>=2.21.0
google-cloud-translate>=3.11.0
google-cloud-language>=2.11.0
google-cloud-storage>=2.10.0
google-auth>=2.17.0

# Database
sqlalchemy>=2.0.0
asyncpg>=0.28.0
psycopg2-binary>=2.9.0

# Vector Database
pgvector>=0.2.0

# AI/ML
openai>=1.0.0
langchain>=0.1.0
transformers>=4.30.0
torch>=2.0.0
tensorflow>=2.13.0

# Utilities
python-dotenv>=1.0.0
pydantic>=2.0.0
httpx>=0.24.0
aiofiles>=23.0.0
"""
            
            requirements_path = Path("requirements_cloud.txt")
            
            with open(requirements_path, 'w', encoding='utf-8') as f:
                f.write(requirements_content)
            
            self.logger.info(f"Created cloud requirements: {requirements_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create cloud requirements: {e}")
            return False
    
    def create_setup_guide(self) -> bool:
        """สร้าง setup guide"""
        try:
            guide_content = """# WAWAGOT V.2 Cloud Setup Guide

## Prerequisites

1. **Supabase Account**
   - สร้าง project ที่ https://supabase.com
   - เปิดใช้งาน PostgreSQL database
   - เปิดใช้งาน Storage
   - เปิดใช้งาน Authentication

2. **Google Cloud Account**
   - สร้าง project ที่ https://console.cloud.google.com
   - เปิดใช้งาน APIs ที่จำเป็น:
     - Cloud Vision API
     - Cloud Speech API
     - Cloud Translation API
     - Natural Language API
     - Cloud Storage API
   - สร้าง Service Account และ download credentials

3. **OpenAI Account**
   - สร้าง account ที่ https://platform.openai.com
   - สร้าง API key

## Setup Steps

### 1. Environment Configuration

```bash
# Copy environment template
cp config/.env.template .env

# Edit .env file with your credentials
nano .env
```

### 2. Supabase Setup

1. ไปที่ Supabase Dashboard
2. Copy Project URL และ API Keys
3. เปิดใช้งาน Row Level Security (RLS)
4. เปิดใช้งาน Storage buckets

### 3. Google Cloud Setup

1. เปิดใช้งาน APIs ที่จำเป็น
2. สร้าง Service Account
3. Download credentials JSON file
4. วางไฟล์ใน `config/` directory

### 4. Database Migration

```bash
# Install cloud dependencies
pip install -r requirements_cloud.txt

# Run database migration
python database/migrate.py init
```

### 5. Test Connection

```bash
# Test cloud connections
python -c "import asyncio; from core.cloud_manager import get_cloud_manager; asyncio.run(get_cloud_manager())"
```

## Configuration Files

- `config/cloud_config.json` - Cloud service configuration
- `config/.env` - Environment variables
- `database/schema.sql` - Database schema
- `requirements_cloud.txt` - Cloud dependencies

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - ตรวจสอบ API keys และ URLs
   - ตรวจสอบ network connectivity
   - ตรวจสอบ service account permissions

2. **Database Migration Failed**
   - ตรวจสอบ database credentials
   - ตรวจสอบ RLS policies
   - ตรวจสอบ extensions (uuid-ossp, pg_trgm, vector)

3. **Google Cloud API Errors**
   - ตรวจสอบ API enablement
   - ตรวจสอบ billing setup
   - ตรวจสอบ service account permissions

### Support

- Documentation: `docs/`
- Logs: `logs/`
- Configuration: `config/`
"""
            
            guide_path = Path("docs/CLOUD_SETUP_GUIDE.md")
            guide_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(guide_path, 'w', encoding='utf-8') as f:
                f.write(guide_content)
            
            self.logger.info(f"Created setup guide: {guide_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create setup guide: {e}")
            return False
    
    def run_setup(self) -> bool:
        """run setup ทั้งหมด"""
        try:
            self.logger.info("Starting WAWAGOT V.2 Cloud Setup...")
            
            # Create directories
            if not self.create_directories():
                return False
            
            # Create templates
            if not self.create_env_template():
                return False
            
            if not self.create_config_template():
                return False
            
            # Create requirements
            if not self.create_requirements_cloud():
                return False
            
            # Create setup guide
            if not self.create_setup_guide():
                return False
            
            self.logger.info("✅ Cloud setup completed successfully!")
            self.logger.info("📝 Next steps:")
            self.logger.info("   1. Edit config/.env.template and save as .env")
            self.logger.info("   2. Configure your Supabase and Google Cloud credentials")
            self.logger.info("   3. Run: pip install -r requirements_cloud.txt")
            self.logger.info("   4. Run: python database/migrate.py init")
            self.logger.info("   5. Check docs/CLOUD_SETUP_GUIDE.md for detailed instructions")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False

def main():
    """Main function"""
    setup = CloudSetup()
    
    print("WAWAGOT V.2 Cloud Setup")
    print("=" * 30)
    
    success = setup.run_setup()
    
    if success:
        print("\n🎉 Setup completed successfully!")
        print("Please follow the next steps above to configure your cloud services.")
    else:
        print("\n❌ Setup failed. Please check the logs above.")

if __name__ == "__main__":
    main() 