"""
Backup Tool - เครื่องมือ backup แบบ command line
"""
import argparse
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.backup_controller import BackupController

def main():
    parser = argparse.ArgumentParser(description='Backup Tool')
    parser.add_argument('source', help='Source path to backup')
    parser.add_argument('--name', help='Backup name')
    
    args = parser.parse_args()
    
    controller = BackupController()
    result = controller.create_backup(args.source, args.name)
    print(f"Backup created: {result}")

if __name__ == "__main__":
    main()
