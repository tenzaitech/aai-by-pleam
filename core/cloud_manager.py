#!/usr/bin/env python3
"""
WAWAGOT V.2 Cloud Manager
จัดการ connection กับ Supabase และ Google Cloud APIs
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import asyncio
import re

# Supabase
from supabase import create_client, Client
# from supabase.lib.client_options import ClientOptions  # ลบออกถ้าไม่จำเป็น

# Google Cloud
from google.cloud import vision, speech, translate, language_v1, storage
from google.oauth2 import service_account

# Database
import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

class CloudManager:
    """จัดการ connection กับ cloud services"""
    
    def __init__(self, config_path: str = "config/cloud_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.logger = self._setup_logging()
        
        # Initialize connections
        self.supabase_client: Optional[Client] = None
        self.google_vision_client: Optional[vision.ImageAnnotatorClient] = None
        self.google_speech_client: Optional[speech.SpeechClient] = None
        self.google_translate_client: Optional[translate.TranslationServiceClient] = None
        self.google_language_client: Optional[language_v1.LanguageServiceClient] = None
        self.google_storage_client: Optional[storage.Client] = None
        
        # Database connections
        self.db_engine = None
        self.async_db_engine = None
        
    def _resolve_secret(self, value):
        """Utility: resolve __LOAD_FROM__ syntax to load secret from file"""
        if isinstance(value, str) and value.startswith("__LOAD_FROM__:"):
            # Format: __LOAD_FROM__:file_path:key
            m = re.match(r"__LOAD_FROM__:(.*?):(.*)", value)
            if m:
                file_path, key = m.group(1), m.group(2)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    return data[key]
                except Exception as e:
                    self.logger.error(f"Failed to load secret {key} from {file_path}: {e}")
                    return None
        return value

    def _resolve_config(self, config):
        """Recursively resolve all __LOAD_FROM__ values in config dict"""
        if isinstance(config, dict):
            return {k: self._resolve_config(self._resolve_secret(v)) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._resolve_config(self._resolve_secret(i)) for i in config]
        else:
            return self._resolve_secret(config)

    def _load_config(self) -> Any:
        """โหลด configuration (resolve secrets)"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        return self._resolve_config(raw)
    
    def _setup_logging(self) -> logging.Logger:
        """ตั้งค่า logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def setup_supabase(self) -> bool:
        """ตั้งค่า Supabase connection"""
        try:
            supabase_config = self.config['supabase']
            
            # Check if credentials are placeholder values
            if (supabase_config['url'] == 'your_supabase_project_url' or 
                supabase_config['key'] == 'your_supabase_anon_key' or
                supabase_config['url'].startswith('your_') or
                supabase_config['key'].startswith('your_')):
                self.logger.warning("Supabase credentials not configured - skipping Supabase setup")
                return True  # Return True to continue with other services
            
            # Validate URL format
            if not supabase_config['url'].startswith('https://'):
                self.logger.warning("Invalid Supabase URL format - skipping Supabase setup")
                return True
            
            # Create Supabase client (ไม่ต้องใช้ ClientOptions ถ้าไม่จำเป็น)
            self.supabase_client = create_client(
                supabase_config['url'],
                supabase_config['key']
            )
            
            # Test connection (skip if table doesn't exist yet)
            try:
                response = self.supabase_client.table('knowledge_base').select('*').limit(1).execute()
                self.logger.info("Supabase connection successful")
            except Exception as e:
                if "does not exist" in str(e):
                    self.logger.info("Supabase connection successful (table not created yet)")
                else:
                    raise e
            return True
            
        except Exception as e:
            self.logger.error(f"Supabase connection failed: {e}")
            return False
    
    def setup_google_cloud(self) -> bool:
        """ตั้งค่า Google Cloud APIs"""
        try:
            google_config = self.config['google_cloud']
            
            # Check if credentials are placeholder values
            if (google_config['project_id'] == 'your_google_cloud_project_id' or 
                google_config['credentials_file'] == 'path/to/service-account-key.json'):
                self.logger.warning("Google Cloud credentials not configured - skipping Google Cloud setup")
                return True  # Return True to continue with other services
            
            # Check if credentials file exists
            credentials_path = Path(google_config['credentials_file'])
            if not credentials_path.exists():
                self.logger.warning(f"Google Cloud credentials file not found: {credentials_path}")
                return True
            
            # Load service account credentials
            credentials = service_account.Credentials.from_service_account_file(
                google_config['credentials_file']
            )
            
            # Initialize Vision API
            if google_config['apis']['vision']['enabled']:
                self.google_vision_client = vision.ImageAnnotatorClient(credentials=credentials)
                self.logger.info("Google Vision API initialized")
            
            # Initialize Speech API (ใช้ from_service_account_json)
            if google_config['apis']['speech']['enabled']:
                self.google_speech_client = speech.SpeechClient.from_service_account_json(
                    google_config['credentials_file']
                )
                self.logger.info("Google Speech API initialized")
            
            # Initialize Translation API (ใช้ from_service_account_json)
            if google_config['apis']['translation']['enabled']:
                self.google_translate_client = translate.TranslationServiceClient.from_service_account_json(
                    google_config['credentials_file']
                )
                self.logger.info("Google Translation API initialized")
            
            # Initialize Natural Language API (ใช้ from_service_account_json)
            if google_config['apis']['natural_language']['enabled']:
                self.google_language_client = language_v1.LanguageServiceClient.from_service_account_json(
                    google_config['credentials_file']
                )
                self.logger.info("Google Natural Language API initialized")
            
            # Initialize Cloud Storage
            if google_config['apis']['storage']['enabled']:
                self.google_storage_client = storage.Client.from_service_account_json(
                    google_config['credentials_file']
                )
                self.logger.info("Google Cloud Storage initialized")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Google Cloud setup failed: {e}")
            return False
    
    def setup_database(self) -> bool:
        """ตั้งค่า database connection"""
        try:
            supabase_config = self.config['supabase']
            
            # Check if credentials are placeholder values
            if (supabase_config['database']['host'] == 'your_supabase_db_host' or 
                supabase_config['database']['password'] == 'your_supabase_db_password'):
                self.logger.warning("Database credentials not configured - skipping database setup")
                return True  # Return True to continue with other services
            
            # Create SQLAlchemy engine for direct database access
            database_url = f"postgresql://{supabase_config['database']['user']}:{supabase_config['database']['password']}@{supabase_config['database']['host']}:{supabase_config['database']['port']}/{supabase_config['database']['database']}"
            
            self.db_engine = create_engine(database_url)
            
            # Create async engine
            async_database_url = f"postgresql+asyncpg://{supabase_config['database']['user']}:{supabase_config['database']['password']}@{supabase_config['database']['host']}:{supabase_config['database']['port']}/{supabase_config['database']['database']}"
            self.async_db_engine = create_async_engine(async_database_url)
            
            # Test connection
            with self.db_engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            self.logger.info("Database connection successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            return False
    
    async def setup_all(self) -> bool:
        """ตั้งค่า connection ทั้งหมด"""
        self.logger.info("Setting up cloud connections...")
        
        # Setup Supabase
        if not self.setup_supabase():
            return False
        
        # Setup Google Cloud
        if not self.setup_google_cloud():
            return False
        
        # Setup Database
        if not self.setup_database():
            return False
        
        self.logger.info("All cloud connections setup successfully")
        return True
    
    def get_supabase_client(self) -> Optional[Client]:
        """Get Supabase client"""
        return self.supabase_client
    
    def get_google_vision_client(self) -> Optional[vision.ImageAnnotatorClient]:
        """Get Google Vision client"""
        return self.google_vision_client
    
    def get_google_speech_client(self) -> Optional[speech.SpeechClient]:
        """Get Google Speech client"""
        return self.google_speech_client
    
    def get_google_translate_client(self) -> Optional[translate.TranslationServiceClient]:
        """Get Google Translation client"""
        return self.google_translate_client
    
    def get_google_language_client(self) -> Optional[language_v1.LanguageServiceClient]:
        """Get Google Natural Language client"""
        return self.google_language_client
    
    def get_google_storage_client(self) -> Optional[storage.Client]:
        """Get Google Cloud Storage client"""
        return self.google_storage_client
    
    def get_db_engine(self):
        """Get database engine"""
        return self.db_engine
    
    def get_async_db_engine(self):
        """Get async database engine"""
        return self.async_db_engine
    
    async def close_connections(self):
        """ปิด connections ทั้งหมด"""
        try:
            if self.async_db_engine:
                await self.async_db_engine.dispose()
            
            if self.db_engine:
                self.db_engine.dispose()
            
            self.logger.info("All connections closed")
            
        except Exception as e:
            self.logger.error(f"Error closing connections: {e}")

# Global instance
cloud_manager: Optional[CloudManager] = None

async def get_cloud_manager() -> CloudManager:
    """Get global cloud manager instance"""
    global cloud_manager
    
    if cloud_manager is None:
        cloud_manager = CloudManager()
        await cloud_manager.setup_all()
    
    return cloud_manager 