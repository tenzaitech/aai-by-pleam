#!/usr/bin/env python3
"""
WAWAGOT V.2 SQL Executor
สำหรับ execute SQL commands ใน Supabase
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.cloud_manager import CloudManager

class SQLExecutor:
    """จัดการ SQL execution ใน Supabase"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.cloud_manager = None
        
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
    
    async def execute_sql_file(self, sql_file_path: str) -> Dict[str, Any]:
        """execute SQL file"""
        try:
            sql_path = Path(sql_file_path)
            
            if not sql_path.exists():
                return {
                    "success": False,
                    "error": f"SQL file not found: {sql_path}"
                }
            
            self.logger.info(f"Executing SQL file: {sql_path.name}")
            
            # Read SQL file
            with open(sql_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            return await self.execute_sql(sql_content, sql_path.name)
            
        except Exception as e:
            self.logger.error(f"Error executing SQL file: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_sql(self, sql_content: str, description: str = "SQL") -> Dict[str, Any]:
        """execute SQL content"""
        try:
            # Split into individual statements
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            engine = self.cloud_manager.get_db_engine()
            if not engine:
                return {
                    "success": False,
                    "error": "Database engine not available"
                }
            results = []
            
            with engine.connect() as conn:
                for i, statement in enumerate(statements):
                    if statement:
                        try:
                            # Execute statement using text()
                            result = conn.execute(text(statement))
                            
                            # Handle different types of results
                            if result.returns_rows:
                                rows = result.fetchall()
                                if rows:
                                    # Convert to list of dicts for JSON serialization
                                    columns = result.keys()
                                    row_data = [dict(zip(columns, row)) for row in rows]
                                    results.append({
                                        "statement": i + 1,
                                        "type": "SELECT",
                                        "rows": len(row_data),
                                        "data": row_data
                                    })
                                else:
                                    results.append({
                                        "statement": i + 1,
                                        "type": "SELECT",
                                        "rows": 0,
                                        "data": []
                                    })
                            else:
                                results.append({
                                    "statement": i + 1,
                                    "type": "DML/DDL",
                                    "rows_affected": result.rowcount if hasattr(result, 'rowcount') else None
                                })
                            
                            self.logger.info(f"Executed statement {i+1}/{len(statements)}")
                            
                        except Exception as e:
                            self.logger.warning(f"Statement {i+1} failed: {e}")
                            results.append({
                                "statement": i + 1,
                                "error": str(e)
                            })
                
                conn.commit()
            
            return {
                "success": True,
                "description": description,
                "total_statements": len(statements),
                "results": results
            }
            
        except Exception as e:
            self.logger.error(f"SQL execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cleanup_all_data(self) -> Dict[str, Any]:
        """ล้างข้อมูลทั้งหมด"""
        try:
            self.logger.warning("⚠️ Starting database cleanup - this will DELETE ALL DATA!")
            
            # Execute cleanup script
            cleanup_file = Path(__file__).parent / "cleanup_all_data.sql"
            result = await self.execute_sql_file(str(cleanup_file))
            
            if result["success"]:
                self.logger.info("✅ Database cleanup completed successfully")
            else:
                self.logger.error(f"❌ Database cleanup failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def show_table_info(self) -> Dict[str, Any]:
        """แสดงข้อมูล tables"""
        try:
            sql = """
            SELECT 
                table_name,
                COUNT(*) as row_count
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            GROUP BY table_name
            ORDER BY table_name;
            """
            
            result = await self.execute_sql(sql, "Table Information")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get table info: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def print_results(self, result: Dict[str, Any]):
        """แสดงผลการ execute SQL"""
        if not result.get("success", False):
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            return
        
        print(f"\n✅ {result.get('description', 'SQL')} executed successfully!")
        print(f"📊 Total statements: {result.get('total_statements', 0)}")
        
        for res in result.get("results", []):
            if "error" in res:
                print(f"   Statement {res['statement']}: ❌ {res['error']}")
            elif res.get("type") == "SELECT":
                print(f"   Statement {res['statement']}: 📋 {res['rows']} rows returned")
                if res.get("data"):
                    # Show first few rows as preview
                    for i, row in enumerate(res["data"][:3]):
                        print(f"      Row {i+1}: {row}")
                    if len(res["data"]) > 3:
                        print(f"      ... and {len(res['data']) - 3} more rows")
            else:
                print(f"   Statement {res['statement']}: ✅ {res.get('rows_affected', 'N/A')} rows affected")

async def main():
    """Main function"""
    executor = SQLExecutor()
    
    print("WAWAGOT V.2 SQL Executor")
    print("=" * 30)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "cleanup":
            print("🗑️ Database Cleanup")
            print("⚠️ This will DELETE ALL DATA permanently!")
            confirm = input("Are you sure? Type 'YES' to confirm: ")
            
            if confirm == "YES":
                if await executor.setup_connection():
                    result = await executor.cleanup_all_data()
                    executor.print_results(result)
                else:
                    print("❌ Failed to establish database connection")
            else:
                print("❌ Cleanup cancelled")
        
        elif command == "info":
            print("📋 Database Information")
            if await executor.setup_connection():
                result = await executor.show_table_info()
                executor.print_results(result)
            else:
                print("❌ Failed to establish database connection")
        
        elif command == "execute":
            if len(sys.argv) > 2:
                sql_file = sys.argv[2]
                print(f"🔧 Executing SQL file: {sql_file}")
                if await executor.setup_connection():
                    result = await executor.execute_sql_file(sql_file)
                    executor.print_results(result)
                else:
                    print("❌ Failed to establish database connection")
            else:
                print("❌ Please specify SQL file path")
        
        else:
            print("Unknown command. Available commands:")
            print("  cleanup  - Delete all data")
            print("  info     - Show table information")
            print("  execute <file> - Execute SQL file")
    
    else:
        print("Available commands:")
        print("  cleanup  - Delete all data")
        print("  info     - Show table information")
        print("  execute <file> - Execute SQL file")
        print("\nUsage: python sql_executor.py [command]")

if __name__ == "__main__":
    asyncio.run(main()) 