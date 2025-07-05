#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO CLEANUP SYSTEM - ระบบทำความสะอาดไฟล์ขยะอัตโนมัติ
สร้างเมื่อ: 2025-07-04 23:47
ระดับความสำคัญ: สูงสุด

ระบบนี้จะ:
1. วิเคราะห์ไฟล์ขยะ
2. เก็บข้อมูลสำคัญ
3. ลบไฟล์ที่ไม่จำเป็น
4. บันทึกการทำงาน
"""

import os
import json
import shutil
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_cleanup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoCleanupSystem:
    """ระบบทำความสะอาดไฟล์ขยะอัตโนมัติ"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backups" / "auto_cleanup"
        self.analysis_file = self.project_root / "cleanup_analysis.json"
        self.important_patterns = [
            "credentials", "config", "settings", "api_key", "token",
            "password", "secret", "private", "sensitive"
        ]
        self.junk_patterns = [
            "temp_", "debug_", "test_", "*.log", "*.tmp", "*.bak",
            "__pycache__", ".pytest_cache", "node_modules"
        ]
        
        # สร้างโฟลเดอร์ backup
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def analyze_files(self) -> Dict:
        """วิเคราะห์ไฟล์ทั้งหมดในโปรเจกต์"""
        logger.info("🔍 เริ่มวิเคราะห์ไฟล์...")
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "total_files": 0,
            "important_files": [],
            "junk_files": [],
            "large_files": [],
            "duplicate_files": [],
            "analysis_summary": {}
        }
        
        # วิเคราะห์ไฟล์ทั้งหมด
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                analysis["total_files"] += 1
                
                # ตรวจสอบไฟล์สำคัญ
                if self._is_important_file(file_path):
                    analysis["important_files"].append(str(file_path))
                
                # ตรวจสอบไฟล์ขยะ
                if self._is_junk_file(file_path):
                    analysis["junk_files"].append(str(file_path))
                
                # ตรวจสอบไฟล์ขนาดใหญ่
                if file_path.stat().st_size > 10 * 1024 * 1024:  # > 10MB
                    analysis["large_files"].append({
                        "path": str(file_path),
                        "size_mb": file_path.stat().st_size / (1024 * 1024)
                    })
        
        # ตรวจสอบไฟล์ซ้ำ
        analysis["duplicate_files"] = self._find_duplicates()
        
        # สรุปการวิเคราะห์
        analysis["analysis_summary"] = {
            "important_count": len(analysis["important_files"]),
            "junk_count": len(analysis["junk_files"]),
            "large_count": len(analysis["large_files"]),
            "duplicate_count": len(analysis["duplicate_files"]),
            "estimated_cleanup_size_mb": self._calculate_cleanup_size(analysis)
        }
        
        # บันทึกการวิเคราะห์
        with open(self.analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ วิเคราะห์เสร็จสิ้น: {analysis['total_files']} ไฟล์")
        logger.info(f"📊 ไฟล์สำคัญ: {analysis['analysis_summary']['important_count']}")
        logger.info(f"🗑️ ไฟล์ขยะ: {analysis['analysis_summary']['junk_count']}")
        logger.info(f"💾 ขนาดที่ประหยัดได้: {analysis['analysis_summary']['estimated_cleanup_size_mb']:.2f} MB")
        
        return analysis
    
    def _is_important_file(self, file_path: Path) -> bool:
        """ตรวจสอบว่าเป็นไฟล์สำคัญหรือไม่"""
        file_name = file_path.name.lower()
        file_content = ""
        
        # อ่านเนื้อหาไฟล์ (เฉพาะไฟล์ข้อความ)
        if file_path.suffix in ['.txt', '.json', '.py', '.md', '.yml', '.yaml', '.env']:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read().lower()
            except:
                pass
        
        # ตรวจสอบชื่อไฟล์
        for pattern in self.important_patterns:
            if pattern in file_name:
                return True
        
        # ตรวจสอบเนื้อหาไฟล์
        for pattern in self.important_patterns:
            if pattern in file_content:
                return True
        
        return False
    
    def _is_junk_file(self, file_path: Path) -> bool:
        """ตรวจสอบว่าเป็นไฟล์ขยะหรือไม่"""
        file_name = file_path.name.lower()
        
        # ตรวจสอบ pattern ไฟล์ขยะ
        for pattern in self.junk_patterns:
            if pattern.startswith("*"):
                if file_name.endswith(pattern[1:]):
                    return True
            elif pattern in file_name:
                return True
        
        # ตรวจสอบโฟลเดอร์ขยะ
        if file_path.is_dir():
            if file_name in ["__pycache__", ".pytest_cache", "node_modules", "logs", "temp"]:
                return True
        
        return False
    
    def _find_duplicates(self) -> List[Dict]:
        """หาฟิล์ซ้ำ"""
        duplicates = []
        file_hashes = {}
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and file_path.stat().st_size > 1024:  # > 1KB
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    
                    if file_hash in file_hashes:
                        duplicates.append({
                            "hash": file_hash,
                            "files": [str(file_hashes[file_hash]), str(file_path)]
                        })
                    else:
                        file_hashes[file_hash] = file_path
                except:
                    pass
        
        return duplicates
    
    def _calculate_cleanup_size(self, analysis: Dict) -> float:
        """คำนวณขนาดที่ประหยัดได้"""
        total_size = 0
        
        for file_path in analysis["junk_files"]:
            try:
                total_size += Path(file_path).stat().st_size
            except:
                pass
        
        return total_size / (1024 * 1024)  # MB
    
    def backup_important_files(self) -> bool:
        """สำรองไฟล์สำคัญ"""
        logger.info("💾 เริ่มสำรองไฟล์สำคัญ...")
        
        try:
            # อ่านการวิเคราะห์
            with open(self.analysis_file, 'r', encoding='utf-8') as f:
                analysis = json.load(f)
            
            backup_count = 0
            for file_path in analysis["important_files"]:
                try:
                    source_path = Path(file_path)
                    if source_path.exists():
                        # สร้างโครงสร้างโฟลเดอร์ใน backup
                        relative_path = source_path.relative_to(self.project_root)
                        backup_path = self.backup_dir / relative_path
                        backup_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # คัดลอกไฟล์
                        shutil.copy2(source_path, backup_path)
                        backup_count += 1
                        logger.debug(f"✅ สำรอง: {file_path}")
                except Exception as e:
                    logger.warning(f"⚠️ ไม่สามารถสำรอง {file_path}: {e}")
            
            logger.info(f"✅ สำรองเสร็จสิ้น: {backup_count} ไฟล์")
            return True
            
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการสำรอง: {e}")
            return False
    
    def cleanup_junk_files(self, dry_run: bool = True) -> Dict:
        """ทำความสะอาดไฟล์ขยะ"""
        logger.info(f"🧹 เริ่มทำความสะอาด (dry_run: {dry_run})...")
        
        cleanup_result = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "removed_files": [],
            "removed_dirs": [],
            "errors": [],
            "total_size_saved_mb": 0
        }
        
        try:
            # อ่านการวิเคราะห์
            with open(self.analysis_file, 'r', encoding='utf-8') as f:
                analysis = json.load(f)
            
            # ลบไฟล์ขยะ
            for file_path in analysis["junk_files"]:
                try:
                    path = Path(file_path)
                    if path.exists():
                        file_size = path.stat().st_size / (1024 * 1024)  # MB
                        
                        if not dry_run:
                            path.unlink()
                            cleanup_result["removed_files"].append({
                                "path": str(path),
                                "size_mb": file_size
                            })
                            cleanup_result["total_size_saved_mb"] += file_size
                            logger.info(f"🗑️ ลบไฟล์: {path}")
                        else:
                            cleanup_result["removed_files"].append({
                                "path": str(path),
                                "size_mb": file_size
                            })
                            cleanup_result["total_size_saved_mb"] += file_size
                            logger.info(f"🔍 จะลบไฟล์: {path}")
                except Exception as e:
                    cleanup_result["errors"].append({
                        "path": file_path,
                        "error": str(e)
                    })
                    logger.warning(f"⚠️ ไม่สามารถลบ {file_path}: {e}")
            
            # ลบโฟลเดอร์ขยะ
            junk_dirs = ["__pycache__", ".pytest_cache", "node_modules", "logs", "temp"]
            for dir_name in junk_dirs:
                for dir_path in self.project_root.rglob(dir_name):
                    if dir_path.is_dir():
                        try:
                            dir_size = self._get_dir_size(dir_path) / (1024 * 1024)  # MB
                            
                            if not dry_run:
                                shutil.rmtree(dir_path)
                                cleanup_result["removed_dirs"].append({
                                    "path": str(dir_path),
                                    "size_mb": dir_size
                                })
                                cleanup_result["total_size_saved_mb"] += dir_size
                                logger.info(f"🗑️ ลบโฟลเดอร์: {dir_path}")
                            else:
                                cleanup_result["removed_dirs"].append({
                                    "path": str(dir_path),
                                    "size_mb": dir_size
                                })
                                cleanup_result["total_size_saved_mb"] += dir_size
                                logger.info(f"🔍 จะลบโฟลเดอร์: {dir_path}")
                        except Exception as e:
                            cleanup_result["errors"].append({
                                "path": str(dir_path),
                                "error": str(e)
                            })
                            logger.warning(f"⚠️ ไม่สามารถลบโฟลเดอร์ {dir_path}: {e}")
            
            # บันทึกผลลัพธ์
            result_file = self.project_root / f"cleanup_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(cleanup_result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ ทำความสะอาดเสร็จสิ้น")
            logger.info(f"📊 ไฟล์ที่ลบ: {len(cleanup_result['removed_files'])}")
            logger.info(f"📁 โฟลเดอร์ที่ลบ: {len(cleanup_result['removed_dirs'])}")
            logger.info(f"💾 ขนาดที่ประหยัดได้: {cleanup_result['total_size_saved_mb']:.2f} MB")
            
            return cleanup_result
            
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการทำความสะอาด: {e}")
            return cleanup_result
    
    def _get_dir_size(self, dir_path: Path) -> int:
        """คำนวณขนาดโฟลเดอร์"""
        total_size = 0
        try:
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except:
            pass
        return total_size
    
    def generate_report(self) -> str:
        """สร้างรายงานการทำความสะอาด"""
        logger.info("📊 สร้างรายงาน...")
        
        try:
            # อ่านการวิเคราะห์
            with open(self.analysis_file, 'r', encoding='utf-8') as f:
                analysis = json.load(f)
            
            report = f"""
# 🧹 AUTO CLEANUP REPORT
สร้างเมื่อ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 สรุปการวิเคราะห์
- ไฟล์ทั้งหมด: {analysis['total_files']:,} ไฟล์
- ไฟล์สำคัญ: {analysis['analysis_summary']['important_count']} ไฟล์
- ไฟล์ขยะ: {analysis['analysis_summary']['junk_count']} ไฟล์
- ไฟล์ขนาดใหญ่: {analysis['analysis_summary']['large_count']} ไฟล์
- ไฟล์ซ้ำ: {analysis['analysis_summary']['duplicate_count']} ไฟล์

## 💾 ประโยชน์ที่ได้
- ขนาดที่ประหยัดได้: {analysis['analysis_summary']['estimated_cleanup_size_mb']:.2f} MB
- ไฟล์ที่ประหยัดได้: {analysis['analysis_summary']['junk_count']} ไฟล์

## 🔍 ไฟล์ขยะที่พบ
"""
            
            for file_path in analysis["junk_files"][:20]:  # แสดง 20 ไฟล์แรก
                report += f"- {file_path}\n"
            
            if len(analysis["junk_files"]) > 20:
                report += f"- ... และอีก {len(analysis['junk_files']) - 20} ไฟล์\n"
            
            report += f"""
## 📁 โฟลเดอร์ขยะที่พบ
"""
            
            junk_dirs = ["__pycache__", ".pytest_cache", "node_modules", "logs", "temp"]
            for dir_name in junk_dirs:
                dir_count = len(list(self.project_root.rglob(dir_name)))
                if dir_count > 0:
                    report += f"- {dir_name}: {dir_count} โฟลเดอร์\n"
            
            report += f"""
## 🎯 แนะนำ
1. ตรวจสอบไฟล์สำคัญก่อนลบ
2. ใช้ dry_run=True ก่อนลบจริง
3. สำรองข้อมูลก่อนทำความสะอาด
4. ตรวจสอบผลลัพธ์หลังทำความสะอาด

---
สร้างโดย: WAWAGOT.AI Auto Cleanup System
"""
            
            # บันทึกรายงาน
            report_file = self.project_root / f"cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"✅ สร้างรายงานเสร็จสิ้น: {report_file}")
            return str(report_file)
            
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการสร้างรายงาน: {e}")
            return ""

def main():
    """ฟังก์ชันหลัก"""
    logger.info("🚀 เริ่มต้น Auto Cleanup System")
    
    try:
        # สร้างระบบ
        cleanup_system = AutoCleanupSystem()
        
        # วิเคราะห์ไฟล์
        analysis = cleanup_system.analyze_files()
        
        # สร้างรายงาน
        report_file = cleanup_system.generate_report()
        
        # สำรองไฟล์สำคัญ
        if analysis["analysis_summary"]["important_count"] > 0:
            backup_success = cleanup_system.backup_important_files()
            if not backup_success:
                logger.warning("⚠️ การสำรองไม่สำเร็จ - หยุดการทำงาน")
                return
        
        # ทำความสะอาด (dry run)
        logger.info("🧹 เริ่มทำความสะอาด (dry run)...")
        cleanup_result = cleanup_system.cleanup_junk_files(dry_run=True)
        
        # แสดงผลลัพธ์
        print(f"\n{'='*60}")
        print("🧹 AUTO CLEANUP SYSTEM - ผลลัพธ์")
        print(f"{'='*60}")
        print(f"📊 ไฟล์ทั้งหมด: {analysis['total_files']:,}")
        print(f"🗑️ ไฟล์ขยะ: {analysis['analysis_summary']['junk_count']}")
        print(f"💾 ขนาดที่ประหยัดได้: {analysis['analysis_summary']['estimated_cleanup_size_mb']:.2f} MB")
        print(f"📄 รายงาน: {report_file}")
        print(f"{'='*60}")
        
        # ถามผู้ใช้ว่าต้องการลบจริงหรือไม่
        if analysis["analysis_summary"]["junk_count"] > 0:
            print(f"\n❓ ต้องการลบไฟล์ขยะจริงหรือไม่? (y/N): ", end="")
            response = input().strip().lower()
            
            if response == 'y':
                logger.info("🧹 เริ่มทำความสะอาดจริง...")
                cleanup_result = cleanup_system.cleanup_junk_files(dry_run=False)
                print(f"✅ ทำความสะอาดเสร็จสิ้น!")
                print(f"💾 ประหยัดพื้นที่: {cleanup_result['total_size_saved_mb']:.2f} MB")
            else:
                print("❌ ยกเลิกการทำความสะอาด")
        
        logger.info("🎉 Auto Cleanup System เสร็จสิ้น")
        
    except KeyboardInterrupt:
        logger.info("🛑 ถูกหยุดโดยผู้ใช้")
    except Exception as e:
        logger.error(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    main() 