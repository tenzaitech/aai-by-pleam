#!/usr/bin/env python3
"""
WAWAGOT V.2 Database Migration Script
สำหรับ migrate schema ไปยัง Supabase
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.cloud_manager import CloudManager

class DatabaseMigrator:
    """จัดการ database migration"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.cloud_manager = None
        self.migration_files = []
        
    def _setup_logging(self) -> logging.Logger:
        """ตั้งค่า logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    async def setup_connection(self) -> bool:
        """ตั้งค่า connection กับ database"""
        try:
            self.cloud_manager = CloudManager()
            success = await self.cloud_manager.setup_all()
            
            if success:
                self.logger.info("Database connection established")
                return True
            else:
                self.logger.error("Failed to establish database connection")
                return False
                
        except Exception as e:
            self.logger.error(f"Error setting up connection: {e}")
            return False
    
    def load_migration_files(self) -> List[Path]:
        """โหลด migration files"""
        migrations_dir = Path(__file__).parent / "migrations"
        
        if not migrations_dir.exists():
            migrations_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created migrations directory: {migrations_dir}")
        
        # Get all .sql files
        migration_files = sorted(migrations_dir.glob("*.sql"))
        self.migration_files = migration_files
        
        self.logger.info(f"Found {len(migration_files)} migration files")
        return migration_files
    
    async def execute_migration(self, migration_file: Path) -> bool:
        """execute migration file"""
        try:
            self.logger.info(f"Executing migration: {migration_file.name}")
            
            # Read migration file
            with open(migration_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Split into individual statements
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            # Execute each statement
            engine = self.cloud_manager.get_db_engine()
            
            with engine.connect() as conn:
                for i, statement in enumerate(statements):
                    if statement:
                        try:
                            conn.execute(statement)
                            self.logger.info(f"Executed statement {i+1}/{len(statements)}")
                        except Exception as e:
                            self.logger.warning(f"Statement {i+1} failed (might be already executed): {e}")
                
                conn.commit()
            
            self.logger.info(f"Migration {migration_file.name} completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Migration {migration_file.name} failed: {e}")
            return False
    
    async def run_migrations(self) -> bool:
        """run migrations ทั้งหมด"""
        try:
            # Setup connection
            if not await self.setup_connection():
                return False
            
            # Load migration files
            migration_files = self.load_migration_files()
            
            if not migration_files:
                self.logger.info("No migration files found")
                return True
            
            # Execute migrations
            success_count = 0
            for migration_file in migration_files:
                if await self.execute_migration(migration_file):
                    success_count += 1
            
            self.logger.info(f"Migration completed: {success_count}/{len(migration_files)} successful")
            return success_count == len(migration_files)
            
        except Exception as e:
            self.logger.error(f"Migration process failed: {e}")
            return False
        finally:
            if self.cloud_manager:
                await self.cloud_manager.close_connections()
    
    async def create_initial_schema(self) -> bool:
        """สร้าง initial schema"""
        try:
            self.logger.info("Creating initial database schema...")
            
            # Setup connection
            if not await self.setup_connection():
                return False
            
            # Read schema file
            schema_file = Path(__file__).parent / "schema.sql"
            
            if not schema_file.exists():
                self.logger.error(f"Schema file not found: {schema_file}")
                return False
            
            # Execute schema
            success = await self.execute_migration(schema_file)
            
            if success:
                self.logger.info("Initial schema created successfully")
            else:
                self.logger.error("Failed to create initial schema")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error creating initial schema: {e}")
            return False
        finally:
            if self.cloud_manager:
                await self.cloud_manager.close_connections()
    
    async def verify_schema(self) -> Dict[str, Any]:
        """ตรวจสอบ schema ที่มีอยู่"""
        try:
            if not await self.setup_connection():
                return {"success": False, "error": "Connection failed"}
            
            engine = self.cloud_manager.get_db_engine()
            
            # Check if tables exist
            tables_to_check = [
                'users', 'knowledge_base', 'commands', 'sessions',
                'learning_patterns', 'results', 'chrome_logs',
                'ai_interactions', 'file_storage', 'system_config'
            ]
            
            existing_tables = []
            missing_tables = []
            
            with engine.connect() as conn:
                for table in tables_to_check:
                    try:
                        result = conn.execute(f"SELECT 1 FROM {table} LIMIT 1")
                        existing_tables.append(table)
                    except Exception:
                        missing_tables.append(table)
            
            return {
                "success": True,
                "existing_tables": existing_tables,
                "missing_tables": missing_tables,
                "total_tables": len(tables_to_check),
                "existing_count": len(existing_tables),
                "missing_count": len(missing_tables)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if self.cloud_manager:
                await self.cloud_manager.close_connections()

async def main():
    """Main function"""
    migrator = DatabaseMigrator()
    
    print("WAWAGOT V.2 Database Migration")
    print("=" * 40)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "verify":
            print("Verifying database schema...")
            result = await migrator.verify_schema()
            
            if result["success"]:
                print(f"✅ Schema verification completed")
                print(f"   Existing tables: {result['existing_count']}/{result['total_tables']}")
                print(f"   Missing tables: {result['missing_count']}")
                
                if result["missing_tables"]:
                    print(f"   Missing: {', '.join(result['missing_tables'])}")
            else:
                print(f"❌ Schema verification failed: {result['error']}")
        
        elif command == "init":
            print("Creating initial schema...")
            success = await migrator.create_initial_schema()
            
            if success:
                print("✅ Initial schema created successfully")
            else:
                print("❌ Failed to create initial schema")
        
        elif command == "migrate":
            print("Running migrations...")
            success = await migrator.run_migrations()
            
            if success:
                print("✅ All migrations completed successfully")
            else:
                print("❌ Some migrations failed")
        
        else:
            print("Unknown command. Available commands: verify, init, migrate")
    
    else:
        print("Available commands:")
        print("  verify  - Check existing schema")
        print("  init    - Create initial schema")
        print("  migrate - Run all migrations")
        print("\nUsage: python migrate.py [command]")

if __name__ == "__main__":
    asyncio.run(main()) 