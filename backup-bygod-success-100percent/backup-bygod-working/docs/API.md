# API Documentation

## BackupController
- `create_backup(source_path, backup_name)`: สร้าง backup
- `restore_backup(backup_path, target_path)`: กู้คืน backup

## RestoreController
- `restore_system(backup_path, target_path)`: กู้คืนระบบ

## SystemMonitor
- `check_system_health()`: ตรวจสอบสุขภาพระบบ
